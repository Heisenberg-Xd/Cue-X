"""
routes/integrations.py
-----------------------
Hybrid data ingestion endpoints for Cue-X:

  GET  /api/integrations/sources?workspace_id=<id>
  POST /api/integrations/google-sheets/connect
  POST /api/integrations/webhook/<workspace_id>
  POST /api/integrations/<source_id>/refresh
  POST /api/integrations/<source_id>/toggle-sync
  DELETE /api/integrations/<source_id>
"""

import io
import logging
import traceback
import requests
import pandas as pd
from flask import Blueprint, request, jsonify

from database import get_connection
from models import (
    insert_data_source,
    get_data_sources_by_workspace,
    toggle_auto_sync,
    deactivate_data_source,
)
from routes.upload import map_sales_columns
from services.clustering_service import run_clustering
from services.cache import clear_cache
from utils.auth import login_required, verify_workspace_access
from sqlalchemy import text

logger = logging.getLogger(__name__)

integrations_bp = Blueprint("integrations", __name__, url_prefix="/api/integrations")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _verify_source_ownership(conn, source_id: int, user_id: int) -> dict | None:
    """
    Return the source row if it belongs to a workspace owned by user_id.
    Logs ownership details on denial.
    """
    try:
        row = conn.execute(
            text("""
                SELECT ds.id, ds.workspace_id, ds.source_type, ds.config,
                       ds.is_active, ds.auto_sync_enabled
                FROM data_sources ds
                JOIN workspaces w ON ds.workspace_id = w.id
                WHERE ds.id = :sid AND w.user_id = :uid
            """),
            {"sid": source_id, "uid": user_id},
        ).fetchone()
        if row is None:
            # Log exactly why — does the source exist at all?
            source_row = conn.execute(
                text("SELECT id, workspace_id FROM data_sources WHERE id = :sid"),
                {"sid": source_id}
            ).fetchone()
            if source_row is None:
                logger.warning(
                    "[Integrations] 404 source_id=%s does not exist at all",
                    source_id
                )
            else:
                ws_row = conn.execute(
                    text("SELECT user_id FROM workspaces WHERE id = :wid"),
                    {"wid": source_row[1]}
                ).fetchone()
                logger.warning(
                    "[Integrations] 403 OWNERSHIP MISMATCH | source_id=%s | "
                    "workspace_id=%s | workspace owned by user_id=%s | requesting user_id=%s",
                    source_id, source_row[1],
                    ws_row[0] if ws_row else 'unknown', user_id
                )
            return None
        return dict(row._mapping)
    except Exception as exc:
        logger.error(
            "[Integrations] _verify_source_ownership error | source_id=%s | user_id=%s\n%s",
            source_id, user_id, traceback.format_exc()
        )
        return None


def _sheets_url_to_csv_export(url: str) -> str:
    """Convert any Google Sheets URL into its CSV export URL."""
    # Extract spreadsheet ID
    import re
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if not match:
        raise ValueError("Invalid Google Sheets URL — could not extract spreadsheet ID.")
    sheet_id = match.group(1)
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"


def _fetch_google_sheet_df(config: dict) -> pd.DataFrame:
    """Fetch a Google Sheet as a pandas DataFrame using the CSV export trick."""
    export_url = _sheets_url_to_csv_export(config["sheet_url"])
    resp = requests.get(export_url, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch Google Sheet (HTTP {resp.status_code}). "
            "Make sure the sheet is shared as 'Anyone with the link can view'."
        )
    df = pd.read_csv(io.StringIO(resp.text))
    return df


# ── Routes ────────────────────────────────────────────────────────────────────

@integrations_bp.route("/sources", methods=["GET"])
@login_required
def list_sources(user_id):
    """List all data sources for a workspace."""
    workspace_id = request.args.get("workspace_id", type=int)
    if not workspace_id:
        return jsonify({"error": "workspace_id query param required"}), 400

    with get_connection() as conn:
        if conn is None:
            return jsonify({"error": "DB unavailable"}), 500
        if not verify_workspace_access(conn, workspace_id, user_id, endpoint="GET /api/integrations/sources"):
            return jsonify({
                "error": "Workspace not found or unauthorized",
                "detail": f"user_id={user_id} does not own workspace_id={workspace_id}. Check Render logs for ownership details."
            }), 403
        sources = get_data_sources_by_workspace(conn, workspace_id)
    return jsonify(sources)


@integrations_bp.route("/google-sheets/connect", methods=["POST"])
@login_required
def connect_google_sheets(user_id):
    """
    Connect a public Google Sheet as an auto-syncing data source.
    Body: { workspace_id, sheet_url, auto_sync_enabled (optional, default true) }
    """
    body = request.get_json(silent=True) or {}
    workspace_id = body.get("workspace_id")
    sheet_url    = (body.get("sheet_url") or "").strip()
    auto_sync    = body.get("auto_sync_enabled", True)

    if not workspace_id or not sheet_url:
        return jsonify({"error": "workspace_id and sheet_url are required"}), 400

    with get_connection() as conn:
        if conn is None:
            return jsonify({"error": "DB unavailable"}), 500
        if not verify_workspace_access(conn, workspace_id, user_id, endpoint="POST /api/integrations/google-sheets/connect"):
            return jsonify({
                "error": "Workspace not found or unauthorized",
                "detail": f"user_id={user_id} does not own workspace_id={workspace_id}"
            }), 403

        # Validate URL + test fetch before saving
        try:
            df_raw = _fetch_google_sheet_df({"sheet_url": sheet_url})
        except Exception as e:
            return jsonify({"error": f"Could not fetch Google Sheet: {e}"}), 400

        config = {"sheet_url": sheet_url}
        source_id = insert_data_source(
            conn,
            workspace_id=workspace_id,
            source_type="google_sheets",
            config=config,
            auto_sync_enabled=bool(auto_sync),
        )
        if not source_id:
            return jsonify({"error": "Failed to create data source"}), 500

    # Trigger initial clustering (outside transaction)
    try:
        df_mapped, _ = map_sales_columns(df_raw)
        result = run_clustering(
            df=df_mapped,
            workspace_id=workspace_id,
            filename=f"google_sheets_{source_id}",
            source_id=source_id,
            ingestion_type="auto",
        )
        if result.get("dataset_id"):
            clear_cache(f"dashboard:{result['dataset_id']}:")
            clear_cache(f"ai:{result['dataset_id']}:")
        return jsonify({
            "success": True,
            "source_id": source_id,
            "dataset_id": result.get("dataset_id"),
            "total_customers": result.get("total_customers"),
            "segments_found": result.get("segments_found"),
            "message": "Google Sheet connected and initial sync completed.",
        })
    except Exception as e:
        logger.error(f"[Integrations] Initial Google Sheets sync failed: {e}")
        return jsonify({
            "success": True,
            "source_id": source_id,
            "warning": f"Source saved but initial sync failed: {e}",
        })


@integrations_bp.route("/webhook/<int:workspace_id>", methods=["POST"])
@login_required
def webhook_ingest(user_id, workspace_id):
    """
    Receive a JSON payload of records and trigger clustering.
    Expected body: { "records": [ { "customer_id", "transaction_date", "amount", ... } ] }
    """
    body = request.get_json(silent=True) or {}
    records = body.get("records")
    if not records or not isinstance(records, list):
        return jsonify({"error": "'records' array is required"}), 400

    with get_connection() as conn:
        if conn is None:
            return jsonify({"error": "DB unavailable"}), 500
        if not verify_workspace_access(conn, workspace_id, user_id, endpoint=f"POST /api/integrations/webhook/{workspace_id}"):
            return jsonify({
                "error": "Workspace not found or unauthorized",
                "detail": f"user_id={user_id} does not own workspace_id={workspace_id}"
            }), 403

        config = {"endpoint": f"/api/integrations/webhook/{workspace_id}"}
        source_id = insert_data_source(
            conn,
            workspace_id=workspace_id,
            source_type="webhook",
            config=config,
            auto_sync_enabled=False,  # Webhooks are push-driven, not polled
        )

    try:
        df = pd.DataFrame(records)
        df_mapped, _ = map_sales_columns(df)
        result = run_clustering(
            df=df_mapped,
            workspace_id=workspace_id,
            filename=f"webhook_{source_id}",
            source_id=source_id,
            ingestion_type="auto",
        )
        if result.get("dataset_id"):
            clear_cache(f"dashboard:{result['dataset_id']}:")
            clear_cache(f"ai:{result['dataset_id']}:")
        return jsonify({"success": True, **result})
    except Exception as e:
        logger.error(f"[Webhook] Clustering failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@integrations_bp.route("/<int:source_id>/refresh", methods=["POST"])
@login_required
def refresh_source(user_id, source_id):
    """Manually re-sync and re-cluster a specific data source."""
    with get_connection() as conn:
        if conn is None:
            return jsonify({"error": "DB unavailable"}), 500
        source = _verify_source_ownership(conn, source_id, user_id)
        if not source:
            return jsonify({"error": "Source not found or unauthorized"}), 404

    if source["source_type"] == "google_sheets":
        import json
        try:
            config = json.loads(source["config"]) if isinstance(source["config"], str) else source["config"]
        except Exception:
            config = {}

        try:
            df_raw = _fetch_google_sheet_df(config)
            df_mapped, _ = map_sales_columns(df_raw)
            result = run_clustering(
                df=df_mapped,
                workspace_id=source["workspace_id"],
                filename=f"google_sheets_{source_id}_refresh",
                source_id=source_id,
                ingestion_type="auto",
            )
            if result.get("dataset_id"):
                clear_cache(f"dashboard:{result['dataset_id']}:")
                clear_cache(f"ai:{result['dataset_id']}:")
            return jsonify({"success": True, **result})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif source["source_type"] == "manual":
        return jsonify({
            "success": False,
            "error": "Manual sources cannot be refreshed automatically. Upload a new CSV.",
        }), 400

    elif source["source_type"] == "webhook":
        return jsonify({
            "success": False,
            "error": "Webhook sources are push-driven. Send a new webhook payload to update.",
        }), 400

    return jsonify({"error": "Unknown source type"}), 400


@integrations_bp.route("/<int:source_id>/toggle-sync", methods=["POST"])
@login_required
def toggle_sync(user_id, source_id):
    """Enable or disable auto_sync for a source."""
    body = request.get_json(silent=True) or {}
    enabled = body.get("enabled")
    if enabled is None:
        return jsonify({"error": "'enabled' (bool) is required"}), 400

    with get_connection() as conn:
        if conn is None:
            return jsonify({"error": "DB unavailable"}), 500
        source = _verify_source_ownership(conn, source_id, user_id)
        if not source:
            return jsonify({"error": "Source not found or unauthorized"}), 404
        toggle_auto_sync(conn, source_id, bool(enabled))

    return jsonify({"success": True, "auto_sync_enabled": bool(enabled)})


@integrations_bp.route("/<int:source_id>", methods=["DELETE"])
@login_required
def disconnect_source(user_id, source_id):
    """Disconnect (soft-delete) a data source."""
    with get_connection() as conn:
        if conn is None:
            return jsonify({"error": "DB unavailable"}), 500
        source = _verify_source_ownership(conn, source_id, user_id)
        if not source:
            return jsonify({"error": "Source not found or unauthorized"}), 404
        deactivate_data_source(conn, source_id)

    return jsonify({"success": True, "message": "Source disconnected."})
