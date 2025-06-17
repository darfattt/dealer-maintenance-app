"""Add DEALER_USER role and users_dealer table

Revision ID: 001
Revises: 
Create Date: 2025-06-17 16:44:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create account schema if it doesn't exist
    op.execute("CREATE SCHEMA IF NOT EXISTS account")
    
    # Create users table if it doesn't exist
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('role', sa.Enum('SUPER_ADMIN', 'DEALER_ADMIN', 'DEALER_USER', name='userrole'), nullable=False),
        sa.Column('dealer_id', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('password_reset_token', sa.String(length=255), nullable=True),
        sa.Column('password_reset_expires', sa.DateTime(), nullable=True),
        sa.Column('email_verification_token', sa.String(length=255), nullable=True),
        sa.Column('email_verification_expires', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='account'
    )
    op.create_index(op.f('ix_account_users_id'), 'users', ['id'], unique=False, schema='account')
    op.create_index(op.f('ix_account_users_email'), 'users', ['email'], unique=True, schema='account')
    op.create_index(op.f('ix_account_users_username'), 'users', ['username'], unique=True, schema='account')
    op.create_index(op.f('ix_account_users_dealer_id'), 'users', ['dealer_id'], unique=False, schema='account')
    
    # Create users_dealer table
    op.create_table('users_dealer',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dealer_id', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['account.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='account'
    )
    op.create_index(op.f('ix_account_users_dealer_id'), 'users_dealer', ['id'], unique=False, schema='account')
    op.create_index(op.f('ix_account_users_dealer_user_id'), 'users_dealer', ['user_id'], unique=False, schema='account')
    op.create_index(op.f('ix_account_users_dealer_dealer_id'), 'users_dealer', ['dealer_id'], unique=False, schema='account')


def downgrade() -> None:
    # Drop users_dealer table
    op.drop_index(op.f('ix_account_users_dealer_dealer_id'), table_name='users_dealer', schema='account')
    op.drop_index(op.f('ix_account_users_dealer_user_id'), table_name='users_dealer', schema='account')
    op.drop_index(op.f('ix_account_users_dealer_id'), table_name='users_dealer', schema='account')
    op.drop_table('users_dealer', schema='account')
    
    # Update enum to remove DEALER_USER
    op.execute("ALTER TYPE userrole RENAME TO userrole_old")
    op.execute("CREATE TYPE userrole AS ENUM ('SUPER_ADMIN', 'DEALER_ADMIN')")
    op.execute("ALTER TABLE account.users ALTER COLUMN role TYPE userrole USING role::text::userrole")
    op.execute("DROP TYPE userrole_old")
