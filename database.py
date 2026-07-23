"""
database.py
-----------
SQLAlchemy engine + connection helper for CUE-X PostgreSQL integration.

Migration note (2026-07):
  The original Render PostgreSQL free-tier database was permanently deleted.
  This file now targets Neon PostgreSQL (ap-southeast-1).
  Neon requires sslmode=require on every connection.

On startup, call `init_db()` to auto-create / migrate required tables.
Use `get_connection()` as a context-manager for any DB operation.

If the DB is unreachable the module sets `engine = None` and logs the FULL
exception + traceback so the real cause is always visible in Render logs.
"""

import logging
import time
import traceback
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from config import DATABASE_URL

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Engine ────────────────────────────────────────────────────────────────────
engine = None

_MAX_RETRIES   = 3      # startup connection attempts
_RETRY_DELAY_S = 2      # seconds between retries (doubles each attempt)


def _build_engine(url: str):
    """
    Create a SQLAlchemy engine configured for Neon PostgreSQL.

    Neon mandates TLS on every connection.  We pass sslmode=require via
    both the URL query-string (already present) AND connect_args so that
    psycopg2 enforces it regardless of any default pg_hba settings.
    """
    return create_engine(
        url,
        connect_args={"sslmode": "require"},
        pool_pre_ping=True,    # health-check connection before every use
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,       # seconds to wait for a pool slot
        pool_recycle=1800,     # recycle connections every 30 min (Neon idle timeout)
    )


def _try_connect(attempt: int) -> bool:
    """Attempt one connection test. Returns True on success."""
    global engine
    try:
        logger.info(f"[DB] Connection attempt {attempt}/{_MAX_RETRIES} …")
        candidate = _build_engine(DATABASE_URL)

        with candidate.connect() as conn:
            # Verify connectivity and log server info
            pg_version = conn.execute(text("SELECT version()")).scalar()
            db_name    = conn.execute(text("SELECT current_database()")).scalar()

        engine = candidate
        logger.info("=" * 60)
        logger.info("[DB] ✅  PostgreSQL connected successfully")
        logger.info(f"[DB] Server  : {pg_version}")
        logger.info(f"[DB] Database: {db_name}")
        logger.info("=" * 60)
        return True

    except Exception as exc:
        logger.error("=" * 60)
        logger.error(f"[DB] ❌  Connection attempt {attempt} FAILED")
        logger.error(f"[DB] Exception type : {type(exc).__name__}")
        logger.error(f"[DB] Exception msg  : {exc}")
        logger.error("[DB] Full traceback:")
        logger.error(traceback.format_exc())
        logger.error("=" * 60)
        return False


# ── Startup connection with retry ─────────────────────────────────────────────
if not DATABASE_URL:
    logger.critical(
        "[DB] DATABASE_URL is not set!\n"
        "     Set it in Render → Environment → DATABASE_URL\n"
        "     Expected format: postgresql://user:pass@host/dbname?sslmode=require"
    )
else:
    delay = _RETRY_DELAY_S
    connected = False
    for attempt in range(1, _MAX_RETRIES + 1):
        if _try_connect(attempt):
            connected = True
            break
        if attempt < _MAX_RETRIES:
            logger.warning(f"[DB] Retrying in {delay}s …")
            time.sleep(delay)
            delay *= 2   # exponential back-off: 2s → 4s → 8s

    if not connected:
        logger.critical(
            "[DB] ❌  ALL connection attempts exhausted.\n"
            "[DB]     The backend will start but ALL database operations will return HTTP 500.\n"
            "[DB]     Troubleshoot:\n"
            "[DB]       1. Check DATABASE_URL is set correctly in Render env vars.\n"
            "[DB]       2. Verify the Neon project is active (app.neon.tech).\n"
            "[DB]       3. Ensure sslmode=require is in the connection string.\n"
            "[DB]       4. Check Neon IP allow-list if enabled.\n"
        )


# ── Connection context-manager ─────────────────────────────────────────────────
@contextmanager
def get_connection():
    """
    Yield a SQLAlchemy connection inside a transaction.

    Usage:
        with get_connection() as conn:
            if conn is None:
                return jsonify({'error': 'Database unavailable'}), 500
            conn.execute(text("SELECT 1"))

    If the engine is unavailable, yields None so callers can skip DB logic
    without crashing the server.  The real error is already logged above.
    """
    if engine is None:
        logger.error(
            "[DB] get_connection() called but engine is None — "
            "database is unreachable. Check startup logs for the real error."
        )
        yield None
        return

    conn = engine.connect()
    try:
        yield conn
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.error(
            f"[DB] Transaction rolled back.\n"
            f"     Exception type : {type(exc).__name__}\n"
            f"     Exception msg  : {exc}\n"
            f"     Traceback:\n{traceback.format_exc()}"
        )
        raise
    finally:
        conn.close()


# ── Table creation DDL ─────────────────────────────────────────────────────────
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
    """
    Create tables if they do not already exist, then run safe column migrations.
    Safe to call multiple times — all statements use IF NOT EXISTS guards.
    """
    if engine is None:
        logger.warning(
            "[DB] init_db() skipped — no database connection.\n"
            "     Tables were NOT created. Fix the DATABASE_URL and restart."
        )
        return

    try:
        with engine.connect() as conn:
            # ── 1. Create base tables ──────────────────────────────────────────
            logger.info("[DB] Creating / verifying tables …")
            conn.execute(text(CREATE_TABLES_SQL))

            # ── 2. Idempotent column migrations ───────────────────────────────
            conn.execute(text("""
                DO $$
                BEGIN
                    -- datasets.workspace_id
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='datasets' AND column_name='workspace_id'
                    ) THEN
                        ALTER TABLE datasets ADD COLUMN workspace_id INTEGER
                            REFERENCES workspaces(id) ON DELETE CASCADE;
                    END IF;

                    -- datasets.source_id
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='datasets' AND column_name='source_id'
                    ) THEN
                        ALTER TABLE datasets ADD COLUMN source_id INTEGER
                            REFERENCES data_sources(id) ON DELETE SET NULL;
                    END IF;

                    -- datasets.ingestion_type
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='datasets' AND column_name='ingestion_type'
                    ) THEN
                        ALTER TABLE datasets ADD COLUMN ingestion_type TEXT DEFAULT 'manual';
                    END IF;

                    -- customers.season
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='customers' AND column_name='season'
                    ) THEN
                        ALTER TABLE customers ADD COLUMN season TEXT;
                    END IF;

                    -- workspaces.user_id
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='workspaces' AND column_name='user_id'
                    ) THEN
                        ALTER TABLE workspaces ADD COLUMN user_id INTEGER
                            REFERENCES users(id) ON DELETE CASCADE;
                    END IF;
                END
                $$;
            """))

            conn.commit()

        logger.info("[DB] ✅  Tables verified / created / migrated successfully.")

    except Exception as exc:
        logger.error(
            f"[DB] ❌  Table initialization failed!\n"
            f"     Exception type : {type(exc).__name__}\n"
            f"     Exception msg  : {exc}\n"
            f"     Traceback:\n{traceback.format_exc()}"
        )
