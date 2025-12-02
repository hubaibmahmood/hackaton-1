"""
Rollback script for 001_create_auth_tables migration.
Drops authentication tables in correct order (reverse foreign key dependencies).
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
load_dotenv()

def rollback_migration():
    """Rollback the 001_create_auth_tables migration."""
    # Get database URL
    db_url = os.getenv("DATABASE_URL") or os.getenv("NEON_DB_URL")
    if not db_url:
        print("ERROR: DATABASE_URL or NEON_DB_URL not found in environment")
        sys.exit(1)

    # Convert URL format if needed
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    # Remove the +psycopg part for psycopg3 direct connection
    conn_url = db_url.replace("postgresql+psycopg://", "postgresql://", 1)

    print(f"Connecting to database...")

    # Confirm before rolling back
    response = input("⚠️  This will DROP tables: tab_preferences, user_sessions, user_profiles, users. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Rollback cancelled.")
        sys.exit(0)

    try:
        # Connect to database
        with psycopg.connect(conn_url) as conn:
            with conn.cursor() as cur:
                print("Rolling back migration...")

                # Drop tables in reverse order (respecting foreign keys)
                cur.execute("DROP TABLE IF EXISTS tab_preferences CASCADE;")
                print("  Dropped tab_preferences")

                cur.execute("DROP TABLE IF NOT EXISTS user_sessions CASCADE;")
                print("  Dropped user_sessions")

                cur.execute("DROP TABLE IF EXISTS user_profiles CASCADE;")
                print("  Dropped user_profiles")

                cur.execute("DROP TABLE IF EXISTS users CASCADE;")
                print("  Dropped users")

                conn.commit()
                print("✅ Rollback completed successfully!")

    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    rollback_migration()
