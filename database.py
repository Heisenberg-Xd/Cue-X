"""
database.py
-----------
SQLAlchemy engine + connection helper for CUE-X PostgreSQL integration.

On startup call `init_db()` to auto-create required tables.
Use `get_connection()` as a context-manager for any DB operation.

If the DB is unreachable the module sets `engine = None` so callers
can skip DB writes instead of crashing.
"""

import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# ── Engine ────────────────────────────────────────────────────────────────────
engine = None

if DATABASE_URL:
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,   # verify connection is alive before using it
            pool_size=5,
            max_overflow=10,
        )
        # Quick connectivity test
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("[DB] PostgreSQL connected successfully.")
    except Exception as exc:
        logger.error(f"[DB] Could not connect to PostgreSQL: {exc}")
        engine = None
else:
    logger.warning("[DB] DATABASE_URL not set — database features disabled.")


# ── Connection context-manager ────────────────────────────────────────────────
@contextmanager
def get_connection():
    """
    Yield a SQLAlchemy connection inside a transaction.
    If the engine is unavailable, yields None so callers can skip DB logic.
    """
    if engine is None:
        yield None
        return

    conn = engine.connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Table creation ─────────────────────────────────────────────────────────────
CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS datasets (
    id          SERIAL PRIMARY KEY,
    filename    TEXT        NOT NULL,
    uploaded_at TIMESTAMP   DEFAULT now(),
    row_count   INTEGER
);

CREATE TABLE IF NOT EXISTS customers (
    id            SERIAL PRIMARY KEY,
    dataset_id    INTEGER REFERENCES datasets(id) ON DELETE CASCADE,
    customer_id   TEXT,
    recency       FLOAT,
    frequency     FLOAT,
    monetary      FLOAT,
    cluster_id    INTEGER,
    segment_label TEXT
);

CREATE TABLE IF NOT EXISTS models_used (
    id               SERIAL PRIMARY KEY,
    dataset_id       INTEGER REFERENCES datasets(id) ON DELETE CASCADE,
    model_name       TEXT,
    parameters       TEXT,
    silhouette_score FLOAT,
    created_at       TIMESTAMP DEFAULT now()
);
"""


def init_db():
    """Create tables if they do not already exist."""
    if engine is None:
        logger.warning("[DB] init_db() skipped — no database connection.")
        return

    try:
        with engine.connect() as conn:
            conn.execute(text(CREATE_TABLES_SQL))
            conn.commit()
        logger.info("[DB] Tables verified / created.")
    except Exception as exc:
        logger.error(f"[DB] Table creation failed: {exc}")
