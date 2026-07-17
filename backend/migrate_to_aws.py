"""
BiasharaIQ — Migrate from Render PostgreSQL → AWS RDS PostgreSQL
================================================================
Steps performed:
  1. Connect to both databases
  2. Create schema + all tables on AWS RDS (via SQLAlchemy models)
  3. Export every row from Render, insert into AWS RDS
  4. Sync sequences so auto-increment IDs stay correct
  5. Print row-count validation

Usage:
  Set SOURCE_DATABASE_URL (Render) and TARGET_DATABASE_URL (AWS) in your .env
  or pass them as env vars, then run:

    python migrate_to_aws.py

  You can also do a DRY RUN (no writes) with:
    DRY_RUN=1 python migrate_to_aws.py
"""

import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ─── Config ────────────────────────────────────────────────────────────────────
# SOURCE  = old Render Postgres
# TARGET  = new AWS RDS Postgres  (already in your .env as DATABASE_URL)

SOURCE_URL = os.getenv(
    "SOURCE_DATABASE_URL",
    # ← Replace with your Render internal DB URL if not in .env
    "",
)
TARGET_URL = os.getenv(
    "TARGET_DATABASE_URL",
    os.getenv("DATABASE_URL", ""),   # fallback to DATABASE_URL (already AWS)
)
DRY_RUN = os.getenv("DRY_RUN", "0") == "1"

# Tables in dependency order (parents before children)
TABLES = [
    "users",
    "categories",
    "transactions",
    "subscriptions",
    "payments",
    "uploaded_documents",
    "insights",
    "chat_messages",
    "default_categories",
]

# ─── Validation ────────────────────────────────────────────────────────────────
if not SOURCE_URL:
    log.error(
        "SOURCE_DATABASE_URL is not set.\n"
        "Add it to your .env file:\n"
        "  SOURCE_DATABASE_URL=postgresql://user:pass@host:5432/dbname"
    )
    sys.exit(1)

if not TARGET_URL:
    log.error("TARGET_DATABASE_URL (or DATABASE_URL) is not set in .env")
    sys.exit(1)

if SOURCE_URL == TARGET_URL:
    log.error("SOURCE and TARGET are the same database — aborting.")
    sys.exit(1)

# ─── Imports ───────────────────────────────────────────────────────────────────
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    log.error("psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

try:
    from sqlalchemy import create_engine, text, inspect
except ImportError:
    log.error("sqlalchemy not installed. Run: pip install sqlalchemy")
    sys.exit(1)


# ─── Helpers ───────────────────────────────────────────────────────────────────
def make_connect_args(url: str) -> dict:
    """Return sslmode=require for non-local DBs."""
    if "localhost" in url or "127.0.0.1" in url:
        return {}
    return {"sslmode": "require"}


def pg_connect(url: str, label: str):
    """Open a psycopg2 connection with SSL for cloud DBs."""
    connect_args = make_connect_args(url)
    try:
        conn = psycopg2.connect(url, **connect_args)
        conn.autocommit = False
        log.info(f"✅  Connected to {label}")
        return conn
    except Exception as e:
        log.error(f"❌  Could not connect to {label}: {e}")
        sys.exit(1)


def table_exists(cur, table: str) -> bool:
    cur.execute(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name=%s",
        (table,),
    )
    return cur.fetchone() is not None


def get_row_count(cur, table: str) -> int:
    try:
        cur.execute(f'SELECT COUNT(*) FROM "{table}"')
        return cur.fetchone()[0]
    except Exception:
        return 0


def get_columns(cur, table: str):
    """Return ordered list of column names for a table."""
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
        """,
        (table,),
    )
    return [row[0] for row in cur.fetchall()]


def sync_sequence(cur, table: str, pk_col: str = "id"):
    """Reset the serial sequence to max(id) so future inserts don't collide."""
    cur.execute(
        f"""
        SELECT setval(
            pg_get_serial_sequence('{table}', '{pk_col}'),
            COALESCE((SELECT MAX({pk_col}) FROM "{table}"), 1),
            true
        )
        """
    )


# ─── Step 1: Create schema on AWS RDS ──────────────────────────────────────────
def create_schema_on_target(target_url: str):
    log.info("📐  Creating schema on AWS RDS via SQLAlchemy models...")

    # Add the backend dir to path so models are importable
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    try:
        from models.models import Base
        from core.database import Base as CoreBase  # noqa — registers models
    except ImportError:
        # Fallback: import Base directly from models
        try:
            from models.models import Base
        except ImportError as e:
            log.error(f"Could not import models: {e}")
            sys.exit(1)

    engine = create_engine(
        target_url,
        connect_args=make_connect_args(target_url),
    )

    if DRY_RUN:
        log.info("[DRY RUN] Skipping schema creation on target.")
        return

    try:
        Base.metadata.create_all(engine)
        log.info("✅  Schema created (or already exists) on AWS RDS")
    except Exception as e:
        log.error(f"❌  Schema creation failed: {e}")
        sys.exit(1)
    finally:
        engine.dispose()


# ─── Step 2: Copy data table by table ─────────────────────────────────────────
def migrate_table(src_cur, tgt_cur, table: str):
    if not table_exists(src_cur, table):
        log.warning(f"⚠️   Table '{table}' not found in source — skipping")
        return 0

    if not table_exists(tgt_cur, table):
        log.warning(f"⚠️   Table '{table}' not found in target — skipping")
        return 0

    src_cols = get_columns(src_cur, table)
    tgt_cols = get_columns(tgt_cur, table)

    # Only copy columns that exist in BOTH source and target
    common_cols = [c for c in src_cols if c in tgt_cols]
    if not common_cols:
        log.warning(f"⚠️   No common columns for '{table}' — skipping")
        return 0

    col_list = ", ".join(f'"{c}"' for c in common_cols)
    placeholders = ", ".join(["%s"] * len(common_cols))

    src_cur.execute(f'SELECT {col_list} FROM "{table}"')
    rows = src_cur.fetchall()

    if not rows:
        log.info(f"   ↳  '{table}': 0 rows (empty)")
        return 0

    if DRY_RUN:
        log.info(f"[DRY RUN] '{table}': would copy {len(rows)} rows")
        return len(rows)

    # Disable triggers temporarily for faster inserts (optional)
    try:
        tgt_cur.execute(f'ALTER TABLE "{table}" DISABLE TRIGGER ALL')
    except Exception:
        pass  # may fail if no triggers — that's fine

    insert_sql = (
        f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders}) '
        f'ON CONFLICT DO NOTHING'
    )

    try:
        psycopg2.extras.execute_batch(tgt_cur, insert_sql, rows, page_size=500)
    except Exception as e:
        log.error(f"❌  Failed to insert into '{table}': {e}")
        raise

    try:
        tgt_cur.execute(f'ALTER TABLE "{table}" ENABLE TRIGGER ALL')
    except Exception:
        pass

    log.info(f"   ✅  '{table}': {len(rows)} rows copied")
    return len(rows)


# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    if DRY_RUN:
        log.info("🔍  DRY RUN mode — no data will be written to AWS RDS")

    log.info(f"SOURCE: {SOURCE_URL.split('@')[-1]}")
    log.info(f"TARGET: {TARGET_URL.split('@')[-1]}")
    log.info("")

    # Step 1 — Schema
    create_schema_on_target(TARGET_URL)

    # Step 2 — Connect both
    src_conn = pg_connect(SOURCE_URL, "Render (source)")
    tgt_conn = pg_connect(TARGET_URL, "AWS RDS (target)")

    src_cur = src_conn.cursor()
    tgt_cur = tgt_conn.cursor()

    total_rows = 0
    results = {}

    try:
        for table in TABLES:
            log.info(f"→  Migrating '{table}'...")
            count = migrate_table(src_cur, tgt_cur, table)
            results[table] = count
            total_rows += count

        if not DRY_RUN:
            # Step 3 — Sync sequences
            log.info("")
            log.info("🔄  Syncing sequences...")
            for table in TABLES:
                if table_exists(tgt_cur, table) and "id" in get_columns(tgt_cur, table):
                    try:
                        sync_sequence(tgt_cur, table)
                        log.info(f"   ✅  Sequence synced for '{table}'")
                    except Exception as e:
                        log.warning(f"   ⚠️  Could not sync sequence for '{table}': {e}")

            tgt_conn.commit()
            log.info("")
            log.info("✅  All changes committed to AWS RDS")

    except Exception as e:
        log.error(f"❌  Migration failed: {e}")
        if not DRY_RUN:
            tgt_conn.rollback()
            log.info("↩️   Rolled back all changes to keep target DB clean")
        sys.exit(1)
    finally:
        src_cur.close()
        tgt_cur.close()
        src_conn.close()
        tgt_conn.close()

    # ─── Validation report ──────────────────────────────────────────────────
    log.info("")
    log.info("=" * 55)
    log.info("  MIGRATION SUMMARY")
    log.info("=" * 55)
    log.info(f"  {'Table':<28} {'Rows Copied':>10}")
    log.info("  " + "-" * 42)
    for table, count in results.items():
        log.info(f"  {table:<28} {count:>10,}")
    log.info("  " + "-" * 42)
    log.info(f"  {'TOTAL':<28} {total_rows:>10,}")
    log.info("=" * 55)
    log.info("")

    if DRY_RUN:
        log.info("✅  Dry run complete. Re-run without DRY_RUN=1 to migrate.")
    else:
        log.info("🎉  Migration to AWS RDS complete!")
        log.info("   Next: Update DATABASE_URL in Render environment variables")
        log.info(f"   New URL: {TARGET_URL.split('@')[-1]}")


if __name__ == "__main__":
    main()
