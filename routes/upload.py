import os
import numpy as np
import pandas as pd
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from services.ml_service import rfm_model, rfm_scaler, rfm_segment_map
from services.session_store import UPLOAD_FOLDER, load_session
from config import BASE_URL

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/')
def home():
    return jsonify({"status": "CUE-X API running", "version": "2.0-RFM"})


# ── Upload & Segment ──────────────────────────────────────────────────────────
@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename  = f"{datetime.now().timestamp()}_{file.filename}"
    filepath  = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        # ── Step 1: Load ──────────────────────────────────────────────────────
        raw = pd.read_csv(filepath)

        required_columns = ['Customer_ID', 'Purchase_Date', 'Total_Price']
        for col in required_columns:
            if col not in raw.columns:
                return jsonify({'error': f'Missing required column: {col}'}), 400

        raw['Purchase_Date'] = pd.to_datetime(raw['Purchase_Date'])
        today = datetime.now()

        # ── Step 2: RFM feature engineering per customer ──────────────────────
        rfm = raw.groupby('Customer_ID').agg(
            Recency   = ('Purchase_Date', lambda x: (today - x.max()).days),
            Frequency = ('Purchase_Date', 'count'),
            Monetary  = ('Total_Price',   'sum')
        ).reset_index()

        # ── Step 3: Scale & predict ───────────────────────────────────────────
        if rfm_scaler is None or rfm_model is None:
            return jsonify({'error': 'RFM model not loaded. Run train_rfm_model.py first.'}), 500

        rfm_features = ['Recency', 'Frequency', 'Monetary']
        rfm_scaled   = rfm_scaler.transform(rfm[rfm_features])
        rfm['Cluster'] = rfm_model.predict(rfm_scaled)

        # ── Step 4: RFM quintile scoring (1-5) ───────────────────────────────
        def score_quintile(series, ascending=True):
            pct = series.rank(method='average', pct=True, ascending=ascending)
            return np.ceil(pct * 5).clip(1, 5).astype(int)

        rfm['R_Score'] = score_quintile(rfm['Recency'],   ascending=False) # lower recency = better
        rfm['F_Score'] = score_quintile(rfm['Frequency'], ascending=True)  # higher freq = better
        rfm['M_Score'] = score_quintile(rfm['Monetary'],  ascending=True)  # higher monetary = better
        rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

        # ── Step 5: Map cluster → segment name ───────────────────────────────
        rfm['Segment_Name']      = rfm['Cluster'].apply(
            lambda c: rfm_segment_map.get(str(c), {}).get('Segment_Name', f'Segment {c}'))
        rfm['Campaign_Strategy'] = rfm['Cluster'].apply(
            lambda c: rfm_segment_map.get(str(c), {}).get('Campaign_Strategy', 'Standard engagement'))

        # ── Step 6: Merge back onto raw (row-level, one row per transaction) ──
        customer_df = raw.merge(
            rfm[['Customer_ID','Recency','Frequency','Monetary',
                  'R_Score','F_Score','M_Score','RFM_Score',
                  'Cluster','Segment_Name','Campaign_Strategy']],
            on='Customer_ID', how='left'
        )

        # Keep extra columns if present
        if 'Quantity' in customer_df.columns and 'Total_Price' in customer_df.columns:
            customer_df['Avg_Order_Value'] = (
                customer_df['Total_Price'] / customer_df['Quantity'].replace(0, 1)
            )

        # ── Step 7: Save outputs ──────────────────────────────────────────────
        output_path  = os.path.join(UPLOAD_FOLDER, 'output.csv')
        customer_df.to_csv(output_path, index=False)

        session_id   = datetime.now().strftime("%Y%m%d%H%M%S")
        session_path = os.path.join(UPLOAD_FOLDER, f'session_{session_id}.csv')
        customer_df.to_csv(session_path, index=False)

        # BASE_URL from config is already imported, avoid shadowing
        return jsonify({
            'message':           'File processed successfully!',
            'download_url':      f'{BASE_URL}/download',
            'session_id':        session_id,
            'visualization_url': f'/visualization/{session_id}',
            'total_customers':   int(rfm['Customer_ID'].nunique()),
            'segments_found':    rfm['Segment_Name'].unique().tolist(),
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ── Download ─────────────────────────────────────────────────────────────────
@upload_bp.route('/download')
def download_file():
    output_path = os.path.join(UPLOAD_FOLDER, 'output.csv')
    if os.path.exists(output_path):
        return send_file(output_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404
