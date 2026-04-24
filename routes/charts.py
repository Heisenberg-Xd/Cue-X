from flask import Blueprint, jsonify
from services.session_store import load_session

charts_bp = Blueprint('charts', __name__)

# ── Segment Counts ────────────────────────────────────────────────────────────
@charts_bp.route('/api/segment-counts/<session_id>')
def segment_counts(session_id):
    df, err = load_session(session_id)
    if err:
        return jsonify({'error': err}), 404
    try:
        # Count unique customers per segment
        per_customer = df.drop_duplicates('Customer_ID')
        counts = per_customer['Segment_Name'].value_counts().to_dict()
        return jsonify({'labels': list(counts.keys()), 'values': list(counts.values())})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── Spending by Segment ───────────────────────────────────────────────────────
@charts_bp.route('/api/spending-by-segment/<session_id>')
def spending_by_segment(session_id):
    df, err = load_session(session_id)
    if err:
        return jsonify({'error': err}), 404
    try:
        per_customer = df.drop_duplicates('Customer_ID')
        avg_spend = per_customer.groupby('Segment_Name')['Monetary'].mean().to_dict()
        return jsonify({'labels': list(avg_spend.keys()), 'values': list(avg_spend.values())})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── Recency / Monetary Scatter ────────────────────────────────────────────────
@charts_bp.route('/api/recency-value-scatter/<session_id>')
def recency_value_scatter(session_id):
    df, err = load_session(session_id)
    if err:
        return jsonify({'error': err}), 404
    try:
        per_customer = df.drop_duplicates('Customer_ID')
        result = []
        for seg in per_customer['Segment_Name'].unique():
            seg_df = per_customer[per_customer['Segment_Name'] == seg]
            result.append({
                'name': seg,
                'data': seg_df[['Recency', 'Monetary', 'Customer_ID']].values.tolist()
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── Seasonal Distribution ─────────────────────────────────────────────────────
@charts_bp.route('/api/seasonal-distribution/<session_id>')
def seasonal_distribution(session_id):
    df, err = load_session(session_id)
    if err:
        return jsonify({'error': err}), 404
    try:
        if 'Season' not in df.columns:
            return jsonify({'labels': [], 'datasets': []})
        counts = df.groupby(['Season', 'Segment_Name']).size().unstack(fill_value=0)
        labels = counts.index.tolist()
        datasets = [{'label': col, 'data': counts[col].tolist()} for col in counts.columns]
        return jsonify({'labels': labels, 'datasets': datasets})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── RFM Scores per Segment (heatmap data) ─────────────────────────────────────
@charts_bp.route('/api/rfm-scores/<session_id>')
def rfm_scores(session_id):
    df, err = load_session(session_id)
    if err:
        return jsonify({'error': err}), 404
    try:
        per_customer = df.drop_duplicates('Customer_ID')
        scores = per_customer.groupby('Segment_Name').agg(
            R_Score=('R_Score', 'mean'),
            F_Score=('F_Score', 'mean'),
            M_Score=('M_Score', 'mean'),
            Recency=('Recency', 'mean'),
            Frequency=('Frequency', 'mean'),
            Monetary=('Monetary', 'mean'),
            Count=('Customer_ID', 'count')
        ).reset_index()
        return jsonify(scores.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
