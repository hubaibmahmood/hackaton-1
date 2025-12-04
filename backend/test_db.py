import psycopg
import os
from dotenv import load_dotenv

# Explicitly load .env from the current directory
load_dotenv(override=True)

# Prefer NEON_DB_URL as per your project's .env.example
url = os.getenv("NEON_DB_URL")
if not url:
    url = os.getenv("DATABASE_URL") # Fallback to DATABASE_URL if NEON_DB_URL is not set

print(f"Attempting to connect to: {url}")

if not url:
    print("❌ Error: NEON_DB_URL or DATABASE_URL not found in environment or .env file.")
else:
    try:
        # Use psycopg (v3) to connect
        conn = psycopg.connect(url)
        print("✅ Connected successfully using psycopg (v3)!")
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        print(f"✅ Query result: {result}")
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed using psycopg (v3): {e}")
