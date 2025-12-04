"""Add name and image to users table for better-auth compatibility

Revision ID: 002
Create Date: 2025-12-03
"""
revision = '002_add_user_name_image'
down_revision = '001_create_auth_tables'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('users', sa.Column('name', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('image', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('users', 'image')
    op.drop_column('users', 'name')
