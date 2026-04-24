"""
train_rfm_model.py
------------------
Run this script ONCE to train the RFM K-means model on the StyleSense dataset.
It saves:
  - rfm_kmeans_model.joblib  (trained 4-cluster KMeans)
  - rfm_scaler.joblib        (StandardScaler fitted on R, F, M)
  - rfm_segment_map.json     (cluster_id -> segment name/strategy)

Usage:
    python train_rfm_model.py
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "StyleSense_Dataset_updated.csv")

# ── Load dataset ──────────────────────────────────────────────────────────────
print("[INFO] Loading dataset...")
df = pd.read_csv(DATASET_PATH)
print(f"[INFO] Loaded {len(df)} rows, columns: {list(df.columns)}")

# ── RFM Feature Engineering ───────────────────────────────────────────────────
print("[INFO] Engineering RFM features...")

df['Purchase_Date'] = pd.to_datetime(df['Purchase_Date'])
today = datetime.now()

rfm = df.groupby('Customer_ID').agg(
    Recency   = ('Purchase_Date', lambda x: (today - x.max()).days),
    Frequency = ('Purchase_Date', 'count'),
    Monetary  = ('Total_Price',   'sum')
).reset_index()

print(f"[INFO] RFM shape: {rfm.shape}")
print(rfm.describe())

# ── Scale ─────────────────────────────────────────────────────────────────────
features = ['Recency', 'Frequency', 'Monetary']
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm[features])

# ── Train K-means (k=4) ───────────────────────────────────────────────────────
print("[INFO] Training K-means (k=4)...")
kmeans = KMeans(n_clusters=4, random_state=42, n_init=20, max_iter=500)
rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

# ── Analyze centroids to assign segment names ─────────────────────────────────
# Unscale centroids for interpretation
centroids = scaler.inverse_transform(kmeans.cluster_centers_)
centroid_df = pd.DataFrame(centroids, columns=features)
centroid_df['Cluster'] = range(4)

print("\n[INFO] Cluster Centroids (unscaled):")
print(centroid_df.to_string(index=False))

# Score each cluster: compute a composite score (low recency = good, high F/M = good)
# Normalise each dimension: Recency inverted (lower = better)
centroid_df['R_rank'] = centroid_df['Recency'].rank(ascending=True)   # lower recency → higher rank
centroid_df['F_rank'] = centroid_df['Frequency'].rank(ascending=False) # higher freq → higher rank
centroid_df['M_rank'] = centroid_df['Monetary'].rank(ascending=False)  # higher monetary → higher rank
centroid_df['Score']  = centroid_df['R_rank'] + centroid_df['F_rank'] + centroid_df['M_rank']
centroid_df = centroid_df.sort_values('Score')

# Assign tier labels by composite score rank (4 tiers for 4 clusters)
tier_labels = [
    {
        "Segment_Name": "Champions",
        "Campaign_Strategy": "VIP rewards, early product access, exclusive loyalty perks"
    },
    {
        "Segment_Name": "Loyal Customers",
        "Campaign_Strategy": "Upsell premium products, membership programs, referral bonuses"
    },
    {
        "Segment_Name": "Potential Loyalists",
        "Campaign_Strategy": "Cross-sell complementary products, engagement campaigns, welcome series"
    },
    {
        "Segment_Name": "At Risk / Lost",
        "Campaign_Strategy": "Win-back campaigns, high-value discounts, re-engagement emails"
    }
]

segment_map = {}
for i, (_, row) in enumerate(centroid_df.iterrows()):
    cluster_id = int(row['Cluster'])
    segment_map[str(cluster_id)] = tier_labels[i]

print("\n[INFO] Segment Map:")
for k, v in segment_map.items():
    print(f"   Cluster {k}: {v['Segment_Name']}")

# ── Save artefacts ─────────────────────────────────────────────────────────────
model_path   = os.path.join(BASE_DIR, "rfm_kmeans_model.joblib")
scaler_path  = os.path.join(BASE_DIR, "rfm_scaler.joblib")
map_path     = os.path.join(BASE_DIR, "rfm_segment_map.json")

joblib.dump(kmeans,  model_path)
joblib.dump(scaler,  scaler_path)
with open(map_path, 'w') as f:
    json.dump(segment_map, f, indent=2)

print(f"\n[OK] Saved: {model_path}")
print(f"[OK] Saved: {scaler_path}")
print(f"[OK] Saved: {map_path}")
print("\n[DONE] Training complete! You can now start app.py")
