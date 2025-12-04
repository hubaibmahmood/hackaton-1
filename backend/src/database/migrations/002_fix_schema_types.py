"""Fix schema types for Prisma compatibility

Revision ID: 002
Revises: 001_create_auth_tables
Create Date: 2025-12-03
"""
revision = '002_fix_schema_types'
down_revision = '001_create_auth_tables'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INET

def upgrade():
    # Change ip_address from INET to VARCHAR(45) to support string input from Prisma
    op.alter_column('user_sessions', 'ip_address',
               existing_type=INET,
               type_=sa.String(45),
               existing_nullable=True)
               
    # Ensure password_hash is nullable if better-auth handles it differently, 
    # OR ensure it matches what we expect. 
    # Actually, better-auth uses 'password' field in Prisma which maps to 'password_hash'.
    # Let's keep password_hash as is for now but fix the IP issue which is the blocker.

def downgrade():
    # Revert ip_address back to INET
    op.alter_column('user_sessions', 'ip_address',
               existing_type=sa.String(45),
               type_=INET,
               existing_nullable=True,
               postgresql_using='ip_address::inet')
