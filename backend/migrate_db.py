"""
Migration: Add subscription columns and new tables to existing Render DB.
Run with: python migrate_db.py
Safe to run multiple times (uses IF NOT EXISTS / IF NOT IN).
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT", "5432")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

print(f"Connecting to {host}/{db_name}...")

conn = psycopg2.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    dbname=db_name,
    sslmode="require"
)
conn.autocommit = True
cur = conn.cursor()

# Check if users table exists, if not apply schema.sql first
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public'
        AND table_name = 'users'
    );
""")
users_exists = cur.fetchone()[0]
if not users_exists:
    print("Table 'users' does not exist. Applying schema.sql first...")
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        schema = f.read()
        cur.execute(schema)
    print("Schema applied successfully.")

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
    ("is_verified",              "BOOLEAN DEFAULT FALSE"),
    ("verification_code",        "VARCHAR(10) NULL"),
    ("verification_expires_at",  "TIMESTAMP NULL"),
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

# ── 1.5. Add missing columns to transactions table ─────────────────────
print("[TABLE] Adding missing columns to transactions table...")

tx_columns_to_add = [
    ("source",                   "VARCHAR DEFAULT 'manual'"),
    ("import_batch_id",          "VARCHAR NULL"),
    ("status",                   "VARCHAR DEFAULT 'confirmed'"),
]

for col_name, col_def in tx_columns_to_add:
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'transactions' AND column_name = %s
    """, (col_name,))
    if cur.fetchone() is None:
        cur.execute(f'ALTER TABLE transactions ADD COLUMN IF NOT EXISTS "{col_name}" {col_def}')
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
