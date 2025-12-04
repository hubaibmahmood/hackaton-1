"""
Reset database script.
DROPS all application tables.
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import psycopg

# Load environment variables
load_dotenv(override=True)

def reset_db():
    # Get database URL
    db_url = os.getenv("NEON_DB_URL") or os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: NEON_DB_URL or DATABASE_URL not found in environment")
        sys.exit(1)

    # Clean up URL for psycopg3
    conn_url = db_url
    if "postgresql+psycopg://" in conn_url:
         conn_url = conn_url.replace("postgresql+psycopg://", "postgresql://", 1)
    
    print(f"Connecting to database to RESET...")

    try:
        with psycopg.connect(conn_url) as conn:
            with conn.cursor() as cur:
                print("Dropping tables...")
                cur.execute("DROP TABLE IF EXISTS tab_preferences CASCADE;")
                cur.execute("DROP TABLE IF EXISTS user_sessions CASCADE;")
                cur.execute("DROP TABLE IF EXISTS user_profiles CASCADE;")
                cur.execute("DROP TABLE IF EXISTS accounts CASCADE;")
                cur.execute("DROP TABLE IF EXISTS users CASCADE;")
                
                conn.commit()
                print("✅ Database reset successfully! All application tables dropped.")

    except Exception as e:
        print(f"❌ Reset failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset_db()
