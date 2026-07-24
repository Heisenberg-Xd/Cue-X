import json
import joblib
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

import os

# --- Hardcoded Production Path Resolution ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

print("[DEBUG] MODEL_DIR =", MODEL_DIR)
if os.path.exists(MODEL_DIR):
    print("[DEBUG] Files in models:", os.listdir(MODEL_DIR))
else:
    print("[DEBUG] Files in models: directory does not exist!")

RFM_MODEL_PATH = os.path.join(MODEL_DIR, "rfm_kmeans_model.joblib")
RFM_SCALER_PATH = os.path.join(MODEL_DIR, "rfm_scaler.joblib")
RFM_MAP_PATH = os.path.join(MODEL_DIR, "rfm_segment_map.json")
# ------------------------------------------

# The legacy pre-trained models (rfm_kmeans_model.joblib, rfm_scaler.joblib) 
# have been removed because they are not used by auto_cluster_rfm and 
# loading them with newer scikit-learn/numpy versions causes a SIGSEGV (code 139) in Gunicorn.


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


def _pick_elbow_k(inertia_by_k: dict[int, float]) -> int | None:
    """
    Approximate elbow point using max distance from line between
    the first and last inertia points.
    """
    if len(inertia_by_k) < 3:
        return None

    sorted_items = sorted(inertia_by_k.items())
    ks = np.array([k for k, _ in sorted_items], dtype=float)
    inertias = np.array([v for _, v in sorted_items], dtype=float)

    # Inertia decreases with k, so use geometric distance to baseline.
    start = np.array([ks[0], inertias[0]], dtype=float)
    end = np.array([ks[-1], inertias[-1]], dtype=float)
    baseline = end - start
    baseline_norm = np.linalg.norm(baseline)
    if baseline_norm == 0:
        return int(ks[0])

    distances = []
    for idx, k in enumerate(ks):
        point = np.array([k, inertias[idx]], dtype=float)
        distance = np.abs(np.cross(baseline, point - start)) / baseline_norm
        distances.append(distance)

    return int(ks[int(np.argmax(distances))])


def auto_cluster_rfm(
    rfm_df: pd.DataFrame,
    feature_cols: list[str],
    min_k: int = 2,
    max_k: int = 10,
    random_state: int = 42,
) -> tuple[np.ndarray, StandardScaler, KMeans | None, dict[str, Any]]:
    """
    Auto-select KMeans k using silhouette as primary signal and elbow as
    supporting signal. Returns labels, fitted scaler, fitted model, diagnostics.
    """
    n_customers = len(rfm_df)
    scaler = StandardScaler()
    print("[ML_DEBUG] Entering scaler.fit_transform")
    X = scaler.fit_transform(rfm_df[feature_cols])
    print("[ML_DEBUG] Completed scaler.fit_transform")

    if n_customers == 0:
        raise ValueError("No customers available for clustering.")

    if n_customers == 1:
        return np.array([0]), scaler, None, {
            "selected_k": 1,
            "selection_method": "single_customer",
            "elbow_k": 1,
            "candidates": [],
            "silhouette_score": None,
        }

    min_k = max(2, min_k)
    max_k = min(max_k, n_customers)
    candidate_ks = list(range(min_k, max_k + 1))

    # If there is only one feasible k, run directly.
    if len(candidate_ks) == 1:
        only_k = candidate_ks[0]
        model = KMeans(n_clusters=only_k, random_state=random_state, n_init=10)
        print("[ML_DEBUG] Entering kmeans.fit_predict (single candidate)")
        labels = model.fit_predict(X)
        print("[ML_DEBUG] Completed kmeans.fit_predict (single candidate)")
        sil = None
        if len(set(labels)) > 1 and len(set(labels)) < len(labels):
            try:
                print("[ML_DEBUG] Entering silhouette_score (single candidate)")
                sil = float(silhouette_score(X, labels))
                print("[ML_DEBUG] Completed silhouette_score (single candidate)")
            except Exception as e:
                print(f"[ML_DEBUG] Exception in silhouette_score: {e}")
                sil = None
        return labels, scaler, model, {
            "selected_k": only_k,
            "selection_method": "single_candidate",
            "elbow_k": only_k,
            "candidates": [{"k": only_k, "inertia": float(model.inertia_), "silhouette": sil}],
            "silhouette_score": sil,
        }

    candidate_runs = []
    inertia_by_k: dict[int, float] = {}
    best_silhouette: float | None = None
    best_model: KMeans | None = None
    best_labels: np.ndarray | None = None
    best_k: int | None = None

    for k in candidate_ks:
        model = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        print(f"[ML_DEBUG] Entering kmeans.fit_predict for k={k}")
        labels = model.fit_predict(X)
        print(f"[ML_DEBUG] Completed kmeans.fit_predict for k={k}")
        inertia = float(model.inertia_)
        inertia_by_k[k] = inertia

        sil = None
        if len(set(labels)) > 1 and len(set(labels)) < len(labels):
            try:
                print(f"[ML_DEBUG] Entering silhouette_score for k={k}")
                sil = float(silhouette_score(X, labels))
                print(f"[ML_DEBUG] Completed silhouette_score for k={k}")
            except Exception as e:
                print(f"[ML_DEBUG] Exception in silhouette_score for k={k}: {e}")
                sil = None

        candidate_runs.append({"k": k, "inertia": inertia, "silhouette": sil})

        if sil is not None and (best_silhouette is None or sil > best_silhouette):
            best_silhouette = sil
            best_model = model
            best_labels = labels
            best_k = k

    elbow_k = _pick_elbow_k(inertia_by_k)

    selection_method = "silhouette"
    if best_model is None:
        selection_method = "elbow_fallback"
        fallback_k = elbow_k if elbow_k is not None else candidate_ks[0]
        best_model = KMeans(n_clusters=fallback_k, random_state=random_state, n_init=10)
        print(f"[ML_DEBUG] Entering kmeans.fit_predict (fallback) for k={fallback_k}")
        best_labels = best_model.fit_predict(X)
        print(f"[ML_DEBUG] Completed kmeans.fit_predict (fallback) for k={fallback_k}")
        best_k = fallback_k

    return best_labels, scaler, best_model, {
        "selected_k": int(best_k),
        "selection_method": selection_method,
        "elbow_k": int(elbow_k) if elbow_k is not None else None,
        "candidates": candidate_runs,
        "silhouette_score": best_silhouette,
    }
