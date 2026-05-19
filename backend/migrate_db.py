"""
Migration: Add subscription columns and new tables to existing Render DB.
Run with: python migrate_db.py
Safe to run multiple times (uses IF NOT EXISTS / IF NOT IN).
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in .env")
    sys.exit(1)

try:
    import psycopg2
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

# Parse DATABASE_URL
url = DATABASE_URL.replace("postgresql://", "")
user_pass, rest = url.split("@", 1)
user, password = user_pass.split(":", 1)
host_port, db_name = rest.split("/", 1)
host = host_port.split(":")[0]
port = int(host_port.split(":")[1]) if ":" in host_port else 5432

print(f"Connecting to {host}/{db_name}...")

conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name)
conn.autocommit = True
cur = conn.cursor()

# ── 1. Add missing columns to users table ──────────────────────────────
print("[TABLE] Adding missing columns to users table...")

columns_to_add = [
    ("plan",                     "VARCHAR DEFAULT 'FREE'"),
    ("subscription_status",      "VARCHAR DEFAULT 'active'"),
    ("subscription_start",       "TIMESTAMP NULL"),
    ("subscription_end",         "TIMESTAMP NULL"),
    ("monthly_transaction_count","INTEGER DEFAULT 0"),
    ("currency",                 "VARCHAR DEFAULT 'KES'"),
    ("is_active",                "BOOLEAN DEFAULT TRUE"),
]

for col_name, col_def in columns_to_add:
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = %s
    """, (col_name,))
    if cur.fetchone() is None:
        cur.execute(f'ALTER TABLE users ADD COLUMN IF NOT EXISTS "{col_name}" {col_def}')
        print(f"  [OK] Added column: {col_name}")
    else:
        print(f"  [SKIP] Column already exists: {col_name}")

# ── 2. Create subscriptions table ──────────────────────────────────────
print("[TABLE] Creating subscriptions table if not exists...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        plan VARCHAR NOT NULL,
        amount FLOAT NOT NULL,
        status VARCHAR NOT NULL,
        started_at TIMESTAMP DEFAULT NOW(),
        expires_at TIMESTAMP NOT NULL
    )
""")
print("  [OK] subscriptions table ready")

# ── 3. Create payments table ────────────────────────────────────────────
print("[TABLE] Creating payments table if not exists...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        phone_number VARCHAR NOT NULL,
        amount FLOAT NOT NULL,
        status VARCHAR DEFAULT 'pending',
        mpesa_receipt VARCHAR NULL,
        checkout_request_id VARCHAR UNIQUE,
        merchant_request_id VARCHAR NULL,
        created_at TIMESTAMP DEFAULT NOW()
    )
""")
print("  [OK] payments table ready")

# ── 4. Create insights table if missing ────────────────────────────────
print("[TABLE] Creating insights table if not exists...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS insights (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        type VARCHAR NOT NULL,
        message TEXT NOT NULL,
        severity VARCHAR DEFAULT 'info',
        timestamp TIMESTAMP DEFAULT NOW(),
        is_read BOOLEAN DEFAULT FALSE
    )
""")
print("  [OK] insights table ready")

cur.close()
conn.close()
print("\n[DONE] Migration complete! All columns and tables are in sync.")
