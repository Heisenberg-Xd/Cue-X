import json
import joblib
from config import RFM_MODEL_PATH, RFM_SCALER_PATH, RFM_MAP_PATH

try:
    rfm_model = joblib.load(RFM_MODEL_PATH)
    print("[OK] RFM model loaded")
except Exception as e:
    print(f"[ERR] RFM model load failed: {e}")
    rfm_model = None

try:
    rfm_scaler = joblib.load(RFM_SCALER_PATH)
    print("[OK] RFM scaler loaded")
except Exception as e:
    print(f"[ERR] RFM scaler load failed: {e}")
    rfm_scaler = None

try:
    with open(RFM_MAP_PATH, 'r') as f:
        rfm_segment_map = json.load(f)
    print("[OK] Segment map loaded:", list(rfm_segment_map.keys()))
except Exception as e:
    print(f"[WARN] Segment map load failed: {e}. Using defaults.")
    rfm_segment_map = {
        "0": {"Segment_Name": "Champions",          "Campaign_Strategy": "VIP rewards, early product access"},
        "1": {"Segment_Name": "Loyal Customers",    "Campaign_Strategy": "Upsell premium, membership programs"},
        "2": {"Segment_Name": "Potential Loyalists","Campaign_Strategy": "Cross-sell, engagement campaigns"},
        "3": {"Segment_Name": "At Risk / Lost",     "Campaign_Strategy": "Win-back campaigns, re-engagement emails"},
    }
