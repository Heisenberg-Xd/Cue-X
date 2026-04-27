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
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    email         TEXT        UNIQUE NOT NULL,
    password_hash TEXT        NOT NULL,
    created_at    TIMESTAMP   DEFAULT now()
);

CREATE TABLE IF NOT EXISTS workspaces (
    id          SERIAL PRIMARY KEY,
    name        TEXT        NOT NULL,
    user_id     INTEGER     REFERENCES users(id) ON DELETE CASCADE,
    created_at  TIMESTAMP   DEFAULT now()
);

CREATE TABLE IF NOT EXISTS data_sources (
    id                SERIAL PRIMARY KEY,
    workspace_id      INTEGER     REFERENCES workspaces(id) ON DELETE CASCADE,
    source_type       TEXT        NOT NULL DEFAULT 'manual',
    config            TEXT        DEFAULT '{}',
    is_active         BOOLEAN     DEFAULT true,
    auto_sync_enabled BOOLEAN     DEFAULT false,
    last_synced_at    TIMESTAMP,
    created_at        TIMESTAMP   DEFAULT now()
);

CREATE TABLE IF NOT EXISTS datasets (
    id             SERIAL PRIMARY KEY,
    workspace_id   INTEGER     REFERENCES workspaces(id) ON DELETE CASCADE,
    source_id      INTEGER     REFERENCES data_sources(id) ON DELETE SET NULL,
    ingestion_type TEXT        DEFAULT 'manual',
    filename       TEXT        NOT NULL,
    uploaded_at    TIMESTAMP   DEFAULT now(),
    row_count      INTEGER
);

CREATE TABLE IF NOT EXISTS customers (
    id            SERIAL PRIMARY KEY,
    dataset_id    INTEGER REFERENCES datasets(id) ON DELETE CASCADE,
    customer_id   TEXT,
    recency       FLOAT,
    frequency     FLOAT,
    monetary      FLOAT,
    cluster_id    INTEGER,
    segment_label TEXT,
    season        TEXT
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
            # 1. Create tables
            conn.execute(text(CREATE_TABLES_SQL))
            
            # 2. Migrations
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='datasets' AND column_name='workspace_id'
                    ) THEN
                        ALTER TABLE datasets ADD COLUMN workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE;
                    END IF;

                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='datasets' AND column_name='source_id'
                    ) THEN
                        ALTER TABLE datasets ADD COLUMN source_id INTEGER REFERENCES data_sources(id) ON DELETE SET NULL;
                    END IF;

                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='datasets' AND column_name='ingestion_type'
                    ) THEN
                        ALTER TABLE datasets ADD COLUMN ingestion_type TEXT DEFAULT 'manual';
                    END IF;
                    
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='customers' AND column_name='season'
                    ) THEN
                        ALTER TABLE customers ADD COLUMN season TEXT;
                    END IF;
                    
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='workspaces' AND column_name='user_id'
                    ) THEN
                        ALTER TABLE workspaces ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
                    END IF;
                END
                $$;
            """))
            
            conn.commit()
        logger.info("[DB] Tables verified / created / migrated.")
    except Exception as exc:
        logger.error(f"[DB] Table initialization failed: {exc}")
