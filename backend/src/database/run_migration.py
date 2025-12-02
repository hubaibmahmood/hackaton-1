"""
Direct migration runner to avoid Alembic env.py issues.
Runs the 001_create_auth_tables migration.
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

def run_migration():
    """Run the 001_create_auth_tables migration."""
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

    try:
        # Connect to database
        with psycopg.connect(conn_url) as conn:
            with conn.cursor() as cur:
                # Check if tables already exist
                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name IN ('users', 'user_sessions', 'user_profiles', 'tab_preferences');
                """)
                existing_tables = [row[0] for row in cur.fetchall()]

                if existing_tables:
                    print(f"Tables already exist: {existing_tables}")
                    print("Skipping migration to avoid conflicts.")
                    return

                print("Creating authentication tables...")

                # Create users table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        email VARCHAR(255) NOT NULL UNIQUE,
                        password_hash VARCHAR(255) NOT NULL,
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

                # Create user_profiles table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
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

                # Create user_sessions table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        token_hash VARCHAR(255) NOT NULL UNIQUE,
                        refresh_token_hash VARCHAR(255) NULL,
                        ip_address INET NULL,
                        user_agent TEXT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        revoked BOOLEAN DEFAULT false,
                        CONSTRAINT check_expires_after_created CHECK (expires_at > created_at)
                    );
                """)

                # Create tab_preferences table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS tab_preferences (
                        user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                        active_tab VARCHAR(20) NOT NULL DEFAULT 'original',
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT check_active_tab CHECK (active_tab IN ('original', 'personalized'))
                    );
                """)

                print("Creating indexes...")

                # Create indexes for users
                cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);")

                # Create indexes for user_profiles
                cur.execute("CREATE INDEX IF NOT EXISTS idx_derived_experience_level ON user_profiles(derived_experience_level);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_software_experience ON user_profiles(software_experience_years);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_hardware_experience ON user_profiles(hardware_experience_years);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_programming_languages ON user_profiles USING gin(programming_languages);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_frameworks ON user_profiles USING gin(frameworks);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_robotics_platforms ON user_profiles USING gin(robotics_platforms);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_sensors_actuators ON user_profiles USING gin(sensors_actuators);")

                # Create indexes for user_sessions
                cur.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(token_hash);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_activity ON user_sessions(last_activity_at);")

                # Create index for tab_preferences
                cur.execute("CREATE INDEX IF NOT EXISTS idx_tab_preferences_updated ON tab_preferences(updated_at);")

                conn.commit()
                print("✅ Migration completed successfully!")
                print("Created tables: users, user_profiles, user_sessions, tab_preferences")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
