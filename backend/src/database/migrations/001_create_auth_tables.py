"""Create authentication and profile tables

Revision ID: 001
Create Date: 2025-12-02
"""
revision = '001_create_auth_tables'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('email_verified', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.Column('last_login_at', sa.TIMESTAMP, nullable=True),
        sa.CheckConstraint("status IN ('active', 'suspended', 'deleted')", name='check_status'),
        sa.CheckConstraint(
            "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'",
            name='check_email_format'
        )
    )

    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('user_id', UUID, sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('programming_languages', JSONB, nullable=False, server_default="'[]'::jsonb"),
        sa.Column('frameworks', JSONB, nullable=False, server_default="'[]'::jsonb"),
        sa.Column('software_experience_years', sa.Integer, nullable=False, server_default='0'),
        sa.Column('robotics_platforms', JSONB, nullable=False, server_default="'[]'::jsonb"),
        sa.Column('sensors_actuators', JSONB, nullable=False, server_default="'[]'::jsonb"),
        sa.Column('hardware_experience_years', sa.Integer, nullable=False, server_default='0'),
        sa.Column('derived_experience_level', sa.String(20), nullable=False, server_default="'Beginner'"),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint(
            "derived_experience_level IN ('Beginner', 'Intermediate', 'Advanced')",
            name='check_experience_level'
        ),
        sa.CheckConstraint(
            "software_experience_years >= 0 AND software_experience_years <= 50",
            name='check_software_years'
        ),
        sa.CheckConstraint(
            "hardware_experience_years >= 0 AND hardware_experience_years <= 50",
            name='check_hardware_years'
        )
    )

    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('refresh_token_hash', sa.String(255), nullable=True),
        sa.Column('ip_address', INET, nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.Column('expires_at', sa.TIMESTAMP, nullable=False),
        sa.Column('last_activity_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.Column('revoked', sa.Boolean, server_default='false'),
        sa.CheckConstraint('expires_at > created_at', name='check_expires_after_created')
    )

    # Create tab_preferences table
    op.create_table(
        'tab_preferences',
        sa.Column('user_id', UUID, sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('active_tab', sa.String(20), nullable=False, server_default="'original'"),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint(
            "active_tab IN ('original', 'personalized')",
            name='check_active_tab'
        )
    )

    # Create indexes (see individual table definitions above)
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_status', 'users', ['status'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])

    op.create_index('idx_derived_experience_level', 'user_profiles', ['derived_experience_level'])
    op.create_index('idx_software_experience', 'user_profiles', ['software_experience_years'])
    op.create_index('idx_hardware_experience', 'user_profiles', ['hardware_experience_years'])
    op.create_index('idx_programming_languages', 'user_profiles', ['programming_languages'], postgresql_using='gin')
    op.create_index('idx_frameworks', 'user_profiles', ['frameworks'], postgresql_using='gin')
    op.create_index('idx_robotics_platforms', 'user_profiles', ['robotics_platforms'], postgresql_using='gin')
    op.create_index('idx_sensors_actuators', 'user_profiles', ['sensors_actuators'], postgresql_using='gin')

    op.create_index('idx_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('idx_user_sessions_token', 'user_sessions', ['token_hash'])
    op.create_index('idx_user_sessions_expires', 'user_sessions', ['expires_at'])
    op.create_index('idx_user_sessions_activity', 'user_sessions', ['last_activity_at'])

    op.create_index('idx_tab_preferences_updated', 'tab_preferences', ['updated_at'])


def downgrade():
    op.drop_table('tab_preferences')
    op.drop_table('user_sessions')
    op.drop_table('user_profiles')
    op.drop_table('users')
