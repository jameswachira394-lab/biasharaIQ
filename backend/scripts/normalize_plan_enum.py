"""
One-off script to normalize users.plan values to lowercase and ensure the PostgreSQL enum values match.
Usage:
  # Option 1: provide DATABASE_URL env var
  DATABASE_URL="postgresql://..." python backend/scripts/normalize_plan_enum.py

  # Option 2: pass DB URL as command-line arg
  python backend/scripts/normalize_plan_enum.py "postgresql://..."

This script:
- Connects to Postgres
- If `plan` column is a plain varchar/text, updates values to lowercase
- If `plan` is a postgres enum type, attempts to rename enum value 'PRO'->'pro' if supported
- If rename is not supported, creates userplan_new enum and migrates safely
"""
import os
import sys
import argparse
import psycopg2


def get_conn(db_url):
    return psycopg2.connect(db_url)


def run_sql(conn, query, params=None):
    with conn.cursor() as cur:
        cur.execute(query, params or ())


def enum_values(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT pg_type.typname, pg_enum.enumlabel FROM pg_type JOIN pg_enum ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'userplan';")
        rows = cur.fetchall()
        return [r[1] for r in rows]


def column_is_enum(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT data_type, udt_name FROM information_schema.columns WHERE table_name='users' AND column_name='plan';")
        row = cur.fetchone()
        if not row:
            raise RuntimeError('users.plan column not found')
        data_type, udt_name = row
        return data_type == 'USER-DEFINED' or udt_name == 'userplan'


def normalize_text_column(conn):
    print('Normalizing text/varchar plan values to lowercase...')
    run_sql(conn, "UPDATE users SET plan = LOWER(plan) WHERE plan IS NOT NULL;")
    conn.commit()
    print('Done.')


def attempt_enum_rename(conn):
    print('Trying ALTER TYPE ... RENAME VALUE approach...')
    try:
        run_sql(conn, "ALTER TYPE userplan RENAME VALUE 'PRO' TO 'pro';")
        conn.commit()
        print("Renamed enum value 'PRO' to 'pro'.")
        return True
    except Exception as e:
        conn.rollback()
        print('ALTER TYPE rename failed or not supported:', str(e))
        return False


def migrate_enum_to_lower(conn):
    print('Migrating enum values by creating userplan_new and converting column...')
    try:
        run_sql(conn, "CREATE TYPE userplan_new AS ENUM ('free','pro');")
    except Exception as e:
        conn.rollback()
        print('Warning: failed to create userplan_new (may already exist):', e)
    try:
        run_sql(conn, "ALTER TABLE users ALTER COLUMN plan TYPE text;")
        run_sql(conn, "UPDATE users SET plan = LOWER(plan) WHERE plan IS NOT NULL;")
        run_sql(
            conn,
            "ALTER TABLE users ALTER COLUMN plan TYPE userplan_new USING plan::userplan_new;")
        # swap types
        run_sql(conn, "DROP TYPE IF EXISTS userplan;")
        run_sql(conn, "ALTER TYPE userplan_new RENAME TO userplan;")
        conn.commit()
        print('Migration to userplan enum with lowercase values completed.')
    except Exception as e:
        conn.rollback()
        print('Migration failed:', e)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('db', nargs='?', help='Database URL (optional)')
    args = parser.parse_args()

    db_url = args.db or os.getenv(
        'DATABASE_URL') or os.getenv('NEXT_PUBLIC_API_URL')
    if not db_url:
        print('Provide DATABASE_URL as env or argument')
        sys.exit(1)

    conn = get_conn(db_url)
    try:
        is_enum = column_is_enum(conn)
        print('users.plan column is enum:', is_enum)
        if not is_enum:
            normalize_text_column(conn)
        else:
            vals = enum_values(conn)
            print('Enum values currently:', vals)
            if 'PRO' in vals:
                ok = attempt_enum_rename(conn)
                if not ok:
                    migrate_enum_to_lower(conn)
            else:
                # ensure data normalized
                normalize_text_column(conn)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
