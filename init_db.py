"""
init_db.py
----------
Standalone database initialization script for CUE-X.

Run this ONCE after pointing DATABASE_URL at a new PostgreSQL instance
(e.g., after migrating from Render → Neon) to create the full schema.

Usage:
    python init_db.py

Safe to run multiple times — all DDL uses CREATE TABLE IF NOT EXISTS and
DO $$ IF NOT EXISTS $$ guards, so no data is ever overwritten.

Exit codes:
    0  — success
    1  — database unreachable or schema creation failed
"""

import sys
import logging
import traceback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    # ── 1. Validate environment ────────────────────────────────────────────────
    from config import DATABASE_URL
    if not DATABASE_URL:
        logger.critical(
            "DATABASE_URL is not set!\n"
            "  Set it in your shell or .env file:\n"
            "  DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require"
        )
        sys.exit(1)

    # Mask password in log
    safe_url = DATABASE_URL
    try:
        from urllib.parse import urlparse, urlunparse
        p = urlparse(DATABASE_URL)
        safe_url = urlunparse(p._replace(netloc=f"{p.username}:***@{p.hostname}{':'+str(p.port) if p.port else ''}" ))
    except Exception:
        pass
    logger.info(f"Using DATABASE_URL: {safe_url}")

    # ── 2. Import engine (triggers startup connection + retry logic) ───────────
    from database import engine, init_db
    from sqlalchemy import text

    if engine is None:
        logger.critical(
            "Could not connect to PostgreSQL.\n"
            "  Check the startup logs above for the real exception.\n"
            "  Ensure DATABASE_URL points to a reachable Neon instance\n"
            "  and that sslmode=require is included."
        )
        sys.exit(1)

    # ── 3. Print server information ────────────────────────────────────────────
    try:
        with engine.connect() as conn:
            pg_version  = conn.execute(text("SELECT version()")).scalar()
            db_name     = conn.execute(text("SELECT current_database()")).scalar()
            db_encoding = conn.execute(text("SELECT pg_encoding_to_char(encoding) FROM pg_database WHERE datname = current_database()")).scalar()

        logger.info("=" * 65)
        logger.info("PostgreSQL Server Information")
        logger.info(f"  Version  : {pg_version}")
        logger.info(f"  Database : {db_name}")
        logger.info(f"  Encoding : {db_encoding}")
        logger.info("=" * 65)
    except Exception as exc:
        logger.error(f"Could not read server info: {exc}")

    # ── 4. Create / migrate schema ─────────────────────────────────────────────
    logger.info("Creating schema (CREATE TABLE IF NOT EXISTS) …")
    init_db()

    # ── 5. Verify all expected tables exist ────────────────────────────────────
    EXPECTED_TABLES = {
        "users",
        "workspaces",
        "data_sources",
        "datasets",
        "customers",
        "models_used",
    }

    try:
        with engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' "
                "ORDER BY table_name"
            )).fetchall()
        found_tables = {r[0] for r in rows}
    except Exception as exc:
        logger.error(f"Could not query information_schema: {exc}\n{traceback.format_exc()}")
        sys.exit(1)

    logger.info("Tables found in database:")
    for t in sorted(found_tables):
        status = "✅" if t in EXPECTED_TABLES else "⚠️  (unexpected)"
        logger.info(f"  {status}  {t}")

    missing = EXPECTED_TABLES - found_tables
    if missing:
        logger.error(f"MISSING tables: {missing}")
        sys.exit(1)

    # ── 6. Print column layout for each table ──────────────────────────────────
    logger.info("\nColumn layout:")
    try:
        with engine.connect() as conn:
            for table in sorted(EXPECTED_TABLES):
                cols = conn.execute(text(
                    "SELECT column_name, data_type, is_nullable, column_default "
                    "FROM information_schema.columns "
                    "WHERE table_schema='public' AND table_name=:t "
                    "ORDER BY ordinal_position"
                ), {"t": table}).fetchall()
                logger.info(f"\n  [{table}]")
                for col in cols:
                    nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                    default  = f" DEFAULT {col[3]}" if col[3] else ""
                    logger.info(f"    {col[0]:<25} {col[1]:<20} {nullable}{default}")
    except Exception as exc:
        logger.warning(f"Could not print column layout: {exc}")

    # ── 7. Round-trip connectivity smoke test ──────────────────────────────────
    logger.info("\nRunning round-trip smoke test …")
    try:
        with engine.connect() as conn:
            # Insert a test user
            uid = conn.execute(text(
                "INSERT INTO users (email, password_hash) "
                "VALUES ('__init_db_test__@cuex.internal', 'test_hash') "
                "ON CONFLICT (email) DO UPDATE SET password_hash='test_hash' "
                "RETURNING id"
            )).scalar()

            # Verify read-back
            row = conn.execute(
                text("SELECT id, email FROM users WHERE id = :id"),
                {"id": uid}
            ).fetchone()
            assert row is not None, "Read-back returned None!"
            assert row[1].endswith("@cuex.internal"), "Wrong email read back"

            # Clean up
            conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": uid})
            conn.commit()

        logger.info("  ✅  Round-trip smoke test PASSED (insert → read → delete).")
    except Exception as exc:
        logger.error(
            f"  ❌  Round-trip smoke test FAILED.\n"
            f"  {type(exc).__name__}: {exc}\n"
            f"{traceback.format_exc()}"
        )
        sys.exit(1)

    logger.info("")
    logger.info("=" * 65)
    logger.info("✅  init_db.py complete — Neon PostgreSQL is ready for CUE-X.")
    logger.info("   Next step: deploy the backend and test /api/auth/login")
    logger.info("=" * 65)


if __name__ == "__main__":
    main()
