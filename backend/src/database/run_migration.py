"""
Direct migration runner to avoid Alembic env.py issues.
Runs database migrations/initialization.
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

def run_migration():
    """Run database migrations."""
    # Get database URL
    db_url = os.getenv("NEON_DB_URL") or os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: NEON_DB_URL or DATABASE_URL not found in environment")
        sys.exit(1)

    # Clean up URL for psycopg3
    conn_url = db_url
    if "postgresql+psycopg://" in conn_url:
         conn_url = conn_url.replace("postgresql+psycopg://", "postgresql://", 1)
    
    print(f"Connecting to database...")

    try:
        # Connect to database
        with psycopg.connect(conn_url) as conn:
            with conn.cursor() as cur:
                print("Checking database state...")
                
                # 1. Create Tables if they don't exist
                # Create users table (updated with name/image and VARCHAR id)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255) NULL,
                        email VARCHAR(255) NOT NULL UNIQUE,
                        password_hash VARCHAR(255) NULL,
                        image TEXT NULL,
                        status VARCHAR(20) NOT NULL DEFAULT 'active',
                        email_verified BOOLEAN DEFAULT false,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login_at TIMESTAMP NULL,
                        CONSTRAINT check_status CHECK (status IN ('active', 'suspended', 'deleted')),
                        CONSTRAINT check_email_format CHECK (
                            email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'
                        )
                    );
                """)

                # Create accounts table for better-auth
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS accounts (
                        id VARCHAR(255) PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        type VARCHAR(255) NULL,
                        provider_id VARCHAR(255) NOT NULL,
                        account_id VARCHAR(255) NOT NULL,
                        refresh_token TEXT NULL,
                        access_token TEXT NULL,
                        expires_at INTEGER NULL,
                        token_type VARCHAR(255) NULL,
                        scope VARCHAR(255) NULL,
                        id_token TEXT NULL,
                        session_state VARCHAR(255) NULL,
                        password_hash VARCHAR(255) NULL,
                        password_salt VARCHAR(255) NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE (provider_id, account_id)
                    );
                """)

                # Create user_profiles table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id VARCHAR(255) PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                        programming_languages JSONB NOT NULL DEFAULT '[]'::jsonb,
                        frameworks JSONB NOT NULL DEFAULT '[]'::jsonb,
                        software_experience_years INTEGER NOT NULL DEFAULT 0,
                        robotics_platforms JSONB NOT NULL DEFAULT '[]'::jsonb,
                        sensors_actuators JSONB NOT NULL DEFAULT '[]'::jsonb,
                        hardware_experience_years INTEGER NOT NULL DEFAULT 0,
                        derived_experience_level VARCHAR(20) NOT NULL DEFAULT 'Beginner',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT check_experience_level CHECK (
                            derived_experience_level IN ('Beginner', 'Intermediate', 'Advanced')
                        ),
                        CONSTRAINT check_software_years CHECK (
                            software_experience_years >= 0 AND software_experience_years <= 50
                        ),
                        CONSTRAINT check_hardware_years CHECK (
                            hardware_experience_years >= 0 AND hardware_experience_years <= 50
                        )
                    );
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id VARCHAR(255) PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        token VARCHAR(255) NOT NULL UNIQUE,
                        expires_at TIMESTAMP NOT NULL,
                        ip_address TEXT NULL,
                        user_agent TEXT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT check_expires_after_created CHECK (expires_at > created_at)
                    );
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS tab_preferences (
                        user_id VARCHAR(255) PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                        active_tab VARCHAR(20) NOT NULL DEFAULT 'original',
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT check_active_tab CHECK (active_tab IN ('original', 'personalized'))
                    );
                """)

                # 3. Create Indexes (IF NOT EXISTS handles duplicates)
                print("Verifying indexes...")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_derived_experience_level ON user_profiles(derived_experience_level);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_software_experience ON user_profiles(software_experience_years);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_hardware_experience ON user_profiles(hardware_experience_years);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_programming_languages ON user_profiles USING gin(programming_languages);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_frameworks ON user_profiles USING gin(frameworks);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_robotics_platforms ON user_profiles USING gin(robotics_platforms);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_sensors_actuators ON user_profiles USING gin(sensors_actuators);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(token);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_tab_preferences_updated ON tab_preferences(updated_at);")

                conn.commit()
                print("✅ Database migration completed successfully!")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
