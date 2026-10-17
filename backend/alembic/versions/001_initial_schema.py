"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-10-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    
    # Workspaces
    op.create_table(
        'workspaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('mode', sa.String(20), nullable=False),
        sa.Column('currency', sa.String(3), server_default='IDR'),
        sa.Column('timezone', sa.String(50), server_default='Asia/Jakarta'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("mode IN ('personal', 'business')", name='check_workspace_mode'),
    )
    
    # Accounts
    op.create_table(
        'accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('account_type', sa.String(20), nullable=False),
        sa.Column('currency', sa.String(3), server_default='IDR'),
        sa.Column('initial_balance', sa.NUMERIC(19, 2), server_default='0.00'),
        sa.Column('archived_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('workspace_id', 'name', name='uq_workspace_account_name'),
        sa.CheckConstraint("account_type IN ('cash', 'bank', 'savings', 'business')", name='check_account_type'),
    )
    op.create_index('idx_accounts_workspace', 'accounts', ['workspace_id'])
    
    # Categories
    op.create_table(
        'categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category_type', sa.String(10), nullable=False),
        sa.Column('color', sa.String(7), server_default='#6B7280'),
        sa.Column('is_default', sa.Boolean, server_default='false'),
        sa.Column('archived_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('workspace_id', 'name', 'category_type', name='uq_workspace_category'),
        sa.CheckConstraint("category_type IN ('income', 'expense')", name='check_category_type'),
    )
    op.create_index('idx_categories_workspace', 'categories', ['workspace_id'])
    
    # Transactions
    op.create_table(
        'transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True)),
        sa.Column('transaction_type', sa.String(10), nullable=False),
        sa.Column('amount', sa.NUMERIC(19, 2), nullable=False),
        sa.Column('transaction_date', sa.Date, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('notes', sa.Text),
        sa.Column('transfer_to_account_id', postgresql.UUID(as_uuid=True)),
        sa.Column('transfer_pair_id', postgresql.UUID(as_uuid=True)),
        sa.Column('import_job_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['transfer_to_account_id'], ['accounts.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['transfer_pair_id'], ['transactions.id'], ondelete='CASCADE'),
        sa.CheckConstraint("transaction_type IN ('income', 'expense', 'transfer')", name='check_transaction_type'),
        sa.CheckConstraint("amount > 0", name='check_positive_amount'),
    )
    op.create_index('idx_transactions_workspace', 'transactions', ['workspace_id'])
    op.create_index('idx_transactions_account', 'transactions', ['account_id'])
    op.create_index('idx_transactions_date', 'transactions', ['transaction_date'])
    op.create_index('idx_transactions_workspace_date', 'transactions', ['workspace_id', 'transaction_date'])


def downgrade() -> None:
    op.drop_table('transactions')
    op.drop_table('categories')
    op.drop_table('accounts')
    op.drop_table('workspaces')
    op.drop_table('users')
