"""
scheduler.py
-------------
APScheduler-based background job for Cue-X auto-sync.

Guard: Only starts if the env var SCHEDULER_ENABLED=true is set.
This prevents duplicate job execution in multi-worker Gunicorn deployments.

For Render / Railway / Fly.io: add a separate "worker" service that sets
SCHEDULER_ENABLED=true and runs: python scheduler.py
"""

import io
import logging
import os
import requests
import pandas as pd

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)


def sync_all_active_sources(app=None):
    """
    APScheduler job: iterate over all active auto-sync sources and re-cluster.
    Can be called with an optional Flask app context for request-less execution.
    """
    from database import get_connection
    from models import get_active_auto_sync_sources
    from routes.upload import map_sales_columns
    from services.clustering_service import run_clustering

    logger.info("[Scheduler] Starting auto-sync job...")

    with get_connection() as conn:
        if conn is None:
            logger.warning("[Scheduler] DB unavailable, skipping sync.")
            return
        sources = get_active_auto_sync_sources(conn)

    logger.info(f"[Scheduler] Found {len(sources)} source(s) to sync.")

    for source in sources:
        source_id    = source["id"]
        workspace_id = source["workspace_id"]
        source_type  = source["source_type"]
        config       = source.get("config", {})

        try:
            if source_type == "google_sheets":
                sheet_url = config.get("sheet_url")
                if not sheet_url:
                    logger.warning(f"[Scheduler] Source {source_id} has no sheet_url, skipping.")
                    continue

                import re
                match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", sheet_url)
                if not match:
                    logger.warning(f"[Scheduler] Source {source_id} has invalid sheet URL, skipping.")
                    continue
                sheet_id   = match.group(1)
                export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

                resp = requests.get(export_url, timeout=30)
                if resp.status_code != 200:
                    logger.error(f"[Scheduler] Source {source_id}: HTTP {resp.status_code} fetching sheet.")
                    continue

                df_raw = pd.read_csv(io.StringIO(resp.text))
                df_mapped, _ = map_sales_columns(df_raw)
                result = run_clustering(
                    df=df_mapped,
                    workspace_id=workspace_id,
                    filename=f"auto_sync_{source_id}",
                    source_id=source_id,
                    ingestion_type="auto",
                )
                logger.info(
                    f"[Scheduler] Source {source_id} synced → "
                    f"dataset_id={result.get('dataset_id')}, "
                    f"customers={result.get('total_customers')}"
                )

            else:
                logger.debug(f"[Scheduler] Skipping source {source_id} of type '{source_type}' (not pollable).")

        except Exception as exc:
            logger.error(f"[Scheduler] Failed to sync source {source_id}: {exc}")


def start_scheduler(app=None):
    """
    Start the APScheduler background job.
    Only runs if SCHEDULER_ENABLED=true environment variable is set.
    Returns the scheduler instance or None.
    """
    if os.environ.get("SCHEDULER_ENABLED", "").lower() != "true":
        logger.info("[Scheduler] SCHEDULER_ENABLED != true — scheduler not started (Gunicorn-safe).")
        return None

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        sync_all_active_sources,
        trigger="interval",
        hours=1,
        id="auto_sync_job",
        replace_existing=True,
        kwargs={"app": app},
    )
    scheduler.start()
    logger.info("[Scheduler] Auto-sync scheduler started (runs every 1 hour).")
    return scheduler


# ── Standalone worker entry-point ──────────────────────────────────────────────
if __name__ == "__main__":
    """
    Run as a standalone worker process:
        SCHEDULER_ENABLED=true python scheduler.py

    Keeps running forever, executing sync every hour.
    """
    import time
    logging.basicConfig(level=logging.INFO)

    os.environ["SCHEDULER_ENABLED"] = "true"
    scheduler = start_scheduler()

    if scheduler:
        logger.info("[Scheduler] Worker is running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            logger.info("[Scheduler] Stopped.")
