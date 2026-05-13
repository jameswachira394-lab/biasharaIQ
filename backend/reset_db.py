
import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

# Parse DATABASE_URL
db_url = os.getenv("DATABASE_URL", "postgresql://postgres:james8080@localhost/biasharaiq")
# Extract connection params
db_parts = db_url.replace("postgresql://", "").split("@")
user_pass = db_parts[0].split(":")
user = user_pass[0]
password = user_pass[1]
host_db = db_parts[1].split("/")
host = host_db[0]
db_name = host_db[1]

# Connect to postgres (default database) to drop/create biasharaiq
conn = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database="postgres"
)
conn.autocommit = True
cursor = conn.cursor()

print(f"🔄 Dropping database {db_name}...")
cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name)))

print(f"✨ Creating database {db_name}...")
cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))

cursor.close()
conn.close()

# Now connect to biasharaiq and run schema.sql
print("📝 Applying schema...")
conn = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)
cursor = conn.cursor()

with open("schema.sql", "r") as f:
    schema = f.read()
    cursor.execute(schema)

conn.commit()
cursor.close()
conn.close()

print("✅ Database reset complete!")
#hehehe