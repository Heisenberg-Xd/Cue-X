"""
models.py
---------
Thin helper functions for inserting data into the CUE-X PostgreSQL tables.

Each function accepts a live SQLAlchemy connection (from database.get_connection)
and returns the newly created primary-key id where applicable.
"""

import logging
from sqlalchemy import text
from datetime import datetime

logger = logging.getLogger(__name__)

def serialize_datetime(value):
    """Safely convert datetime to ISO format string."""
    return value.isoformat() if value else None

# ── users ──────────────────────────────────────────────────────────────────────
def create_user(conn, email: str, password_hash: str) -> int | None:
    """
    Creates a new user record in the database.
    
    Args:
        conn: SQLAlchemy connection object.
        email: The user's email address.
        password_hash: The hashed password for security.
        
    Returns:
        The ID of the newly created user, or None if insertion fails.
    """
    try:
        result = conn.execute(
            text("INSERT INTO users (email, password_hash) VALUES (:email, :password_hash) RETURNING id"),
            {"email": email, "password_hash": password_hash}
        )
        return result.fetchone()[0]
    except Exception as exc:
        logger.error(f"[DB] create_user failed: {exc}")
        return None

def get_user_by_email(conn, email: str) -> dict | None:
    """
    Retrieves user details by their email address.
    
    Args:
        conn: SQLAlchemy connection object.
        email: The email address to search for.
        
    Returns:
        A dictionary containing user 'id', 'email', and 'password_hash', or None if not found.
    """
    try:
        result = conn.execute(
            text("SELECT id, email, password_hash FROM users WHERE email = :email"),
            {"email": email}
        )
        row = result.fetchone()
        return dict(row._mapping) if row else None
    except Exception as exc:
        logger.error(f"[DB] get_user_by_email failed: {exc}")
        return None

# ── workspaces ────────────────────────────────────────────────────────────────
def insert_workspace(conn, name: str, user_id: int) -> int | None:
    """
    Creates a new workspace for a user.
    
    Args:
        conn: SQLAlchemy connection object.
        name: Name of the workspace.
        user_id: ID of the user who owns the workspace.
        
    Returns:
        The new workspace_id (int) or None on failure.
    """
    try:
        result = conn.execute(
            text("INSERT INTO workspaces (name, user_id) VALUES (:name, :user_id) RETURNING id"),
            {"name": name, "user_id": user_id},
        )
        workspace_id = result.fetchone()[0]
        logger.info(f"[DB] Workspace created: id={workspace_id}, name={name}, user_id={user_id}")
        return workspace_id
    except Exception as exc:
        logger.error(f"[DB] insert_workspace failed: {exc}")
        return None

def get_workspaces(conn, user_id: int):
    """
    Retrieves all workspaces associated with a specific user.
    
    Args:
        conn: SQLAlchemy connection object.
        user_id: ID of the user whose workspaces are to be listed.
        
    Returns:
        A list of dictionaries representing the user's workspaces.
    """
    try:
        result = conn.execute(
            text("SELECT id, name, created_at FROM workspaces WHERE user_id = :user_id ORDER BY created_at DESC"),
            {"user_id": user_id}
        )
        rows = []
        for row in result.fetchall():
            d = dict(row._mapping)
            if 'created_at' in d:
                d['created_at'] = serialize_datetime(d['created_at'])
            rows.append(d)
        return rows
    except Exception as exc:
        logger.error(f"[DB] get_workspaces failed: {exc}")
        return []

# ── datasets ──────────────────────────────────────────────────────────────────
def get_datasets_by_workspace(conn, workspace_id: int):
    """
    Retrieves all datasets associated with a specific workspace.
    
    Args:
        conn: SQLAlchemy connection object.
        workspace_id: ID of the workspace.
        
    Returns:
        A list of dictionaries containing dataset metadata (id, filename, uploaded_at, row_count).
    """
    try:
        result = conn.execute(
            text("SELECT id, filename, uploaded_at, row_count FROM datasets WHERE workspace_id = :ws_id ORDER BY uploaded_at DESC"),
            {"ws_id": workspace_id}
        )
        rows = []
        for row in result.fetchall():
            d = dict(row._mapping)
            if 'uploaded_at' in d:
                d['uploaded_at'] = serialize_datetime(d['uploaded_at'])
            rows.append(d)
        return rows
    except Exception as exc:
        logger.error(f"[DB] get_datasets_by_workspace failed: {exc}")
        return []

def insert_dataset(conn, filename: str, row_count: int, workspace_id: int = None,
                   source_id: int = None, ingestion_type: str = 'manual') -> int | None:
    """
    Inserts a record for an ingested dataset.
    
    Args:
        conn: SQLAlchemy connection object.
        filename: Name of the file being ingested.
        row_count: Total number of records in the dataset.
        workspace_id: Optional workspace ID.
        source_id: Optional source ID if synced from an external provider.
        ingestion_type: Method of ingestion (e.g., 'manual', 'sync').
        
    Returns:
        The new dataset_id (int) or None on failure.
    """
    try:
        result = conn.execute(
            text(
                "INSERT INTO datasets (filename, row_count, workspace_id, source_id, ingestion_type) "
                "VALUES (:filename, :row_count, :workspace_id, :source_id, :ingestion_type) RETURNING id"
            ),
            {"filename": filename, "row_count": row_count, "workspace_id": workspace_id,
             "source_id": source_id, "ingestion_type": ingestion_type},
        )
        dataset_id = result.fetchone()[0]
        logger.info(f"[DB] Dataset inserted: id={dataset_id}, file={filename}, ws={workspace_id}, type={ingestion_type}")
        return dataset_id
    except Exception as exc:
        logger.error(f"[DB] insert_dataset failed: {exc}")
        return None


# ── customers ─────────────────────────────────────────────────────────────────
def insert_customers(conn, rfm_df, dataset_id: int) -> bool:
    """
    Performs a bulk insertion of customer records derived from RFM analysis.
    
    This function processes a DataFrame containing customer metrics and cluster assignments,
    converting each row into a dictionary for batch execution via SQLAlchemy.
    
    Args:
        conn: SQLAlchemy connection object.
        rfm_df: pandas DataFrame with columns: Customer_ID, Recency, Frequency, Monetary, Cluster, Segment_Name.
        dataset_id: The ID of the dataset these customers belong to.
        
    Returns:
        True if the bulk insertion was successful, False otherwise.
    """
    rows = [
        {
            "dataset_id":    dataset_id,
            "customer_id":   str(row["Customer_ID"]),
            "recency":       float(row["Recency"]),
            "frequency":     float(row["Frequency"]),
            "monetary":      float(row["Monetary"]),
            "cluster_id":    int(row["Cluster"]),
            "segment_label": str(row["Segment_Name"]),
            "season":        str(row["Season"]) if "Season" in row else None,
        }
        for _, row in rfm_df.iterrows()
    ]

    if not rows:
        logger.warning("[DB] insert_customers called with empty DataFrame.")
        return False

    try:
        conn.execute(
            text(
                "INSERT INTO customers "
                "(dataset_id, customer_id, recency, frequency, monetary, "
                " cluster_id, segment_label, season) "
                "VALUES (:dataset_id, :customer_id, :recency, :frequency, "
                "        :monetary, :cluster_id, :segment_label, :season)"
            ),
            rows,
        )
        logger.info(f"[DB] {len(rows)} customer(s) inserted for dataset_id={dataset_id}")
        return True
    except Exception as exc:
        logger.error(f"[DB] insert_customers failed: {exc}")
        return False


# ── models_used ───────────────────────────────────────────────────────────────
def insert_model_metadata(
    conn,
    dataset_id: int,
    model_name: str,
    parameters: str,
    silhouette_score: float,
) -> int | None:
    """
    Insert one record describing the clustering model used.
    Returns the new models_used.id or None on failure.
    """
    try:
        result = conn.execute(
            text(
                "INSERT INTO models_used "
                "(dataset_id, model_name, parameters, silhouette_score) "
                "VALUES (:dataset_id, :model_name, :parameters, :silhouette_score) "
                "RETURNING id"
            ),
            {
                "dataset_id":       dataset_id,
                "model_name":       model_name,
                "parameters":       parameters,
                "silhouette_score": float(silhouette_score) if silhouette_score is not None else None,
            },
        )
        model_row_id = result.fetchone()[0]
        sil_text = f"{float(silhouette_score):.4f}" if silhouette_score is not None else "None"
        logger.info(
            f"[DB] Model metadata inserted: id={model_row_id}, "
            f"model={model_name}, silhouette={sil_text}"
        )
        return model_row_id
    except Exception as exc:
        logger.error(f"[DB] insert_model_metadata failed: {exc}")
        return None


# ── data_sources ──────────────────────────────────────────────────────────────
def insert_data_source(conn, workspace_id: int, source_type: str, config: dict,
                       auto_sync_enabled: bool = False) -> int | None:
    """Create a new data source entry. Returns source_id or None."""
    import json
    try:
        result = conn.execute(
            text(
                "INSERT INTO data_sources (workspace_id, source_type, config, auto_sync_enabled) "
                "VALUES (:workspace_id, :source_type, :config, :auto_sync_enabled) RETURNING id"
            ),
            {"workspace_id": workspace_id, "source_type": source_type,
             "config": json.dumps(config), "auto_sync_enabled": auto_sync_enabled},
        )
        source_id = result.fetchone()[0]
        logger.info(f"[DB] Data source created: id={source_id}, type={source_type}, ws={workspace_id}")
        return source_id
    except Exception as exc:
        logger.error(f"[DB] insert_data_source failed: {exc}")
        return None


def get_data_sources_by_workspace(conn, workspace_id: int) -> list:
    """List all data sources for a workspace."""
    import json
    try:
        result = conn.execute(
            text("SELECT id, source_type, config, is_active, auto_sync_enabled, last_synced_at, created_at "
                 "FROM data_sources WHERE workspace_id = :ws_id ORDER BY created_at DESC"),
            {"ws_id": workspace_id}
        )
        rows = []
        for row in result.fetchall():
            d = dict(row._mapping)
            d['last_synced_at'] = serialize_datetime(d.get('last_synced_at'))
            d['created_at'] = serialize_datetime(d.get('created_at'))
            try:
                d['config'] = json.loads(d['config']) if d['config'] else {}
            except Exception:
                d['config'] = {}
            rows.append(d)
        return rows
    except Exception as exc:
        logger.error(f"[DB] get_data_sources_by_workspace failed: {exc}")
        return []


def update_data_source_sync_time(conn, source_id: int) -> bool:
    """Update last_synced_at to now for a source."""
    try:
        conn.execute(
            text("UPDATE data_sources SET last_synced_at = now() WHERE id = :id"),
            {"id": source_id}
        )
        return True
    except Exception as exc:
        logger.error(f"[DB] update_data_source_sync_time failed: {exc}")
        return False


def toggle_auto_sync(conn, source_id: int, enabled: bool) -> bool:
    """Enable or disable auto_sync for a data source."""
    try:
        conn.execute(
            text("UPDATE data_sources SET auto_sync_enabled = :enabled WHERE id = :id"),
            {"enabled": enabled, "id": source_id}
        )
        return True
    except Exception as exc:
        logger.error(f"[DB] toggle_auto_sync failed: {exc}")
        return False


def deactivate_data_source(conn, source_id: int) -> bool:
    """Soft-delete a data source by marking it inactive."""
    try:
        conn.execute(
            text("UPDATE data_sources SET is_active = false, auto_sync_enabled = false WHERE id = :id"),
            {"id": source_id}
        )
        return True
    except Exception as exc:
        logger.error(f"[DB] deactivate_data_source failed: {exc}")
        return False


def get_active_auto_sync_sources(conn) -> list:
    """Return all active sources with auto_sync_enabled = true."""
    import json
    try:
        result = conn.execute(
            text("SELECT id, workspace_id, source_type, config "
                 "FROM data_sources WHERE is_active = true AND auto_sync_enabled = true")
        )
        rows = []
        for row in result.fetchall():
            d = dict(row._mapping)
            try:
                d['config'] = json.loads(d['config']) if d['config'] else {}
            except Exception:
                d['config'] = {}
            rows.append(d)
        return rows
    except Exception as exc:
        logger.error(f"[DB] get_active_auto_sync_sources failed: {exc}")
        return []

