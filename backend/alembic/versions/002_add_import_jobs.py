"""Add import jobs table

Revision ID: 002
Revises: 001
Create Date: 2026-10-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'import_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('filepath', sa.Text),
        sa.Column('status', sa.String(20), nullable=False, server_default='uploaded'),
        sa.Column('column_mapping', postgresql.JSONB),
        sa.Column('total_rows', sa.Integer, server_default='0'),
        sa.Column('imported_rows', sa.Integer, server_default='0'),
        sa.Column('skipped_rows', sa.Integer, server_default='0'),
        sa.Column('error_rows', sa.Integer, server_default='0'),
        sa.Column('preview_data', postgresql.JSONB),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True)),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
        sa.CheckConstraint("status IN ('uploaded', 'previewed', 'confirmed', 'failed')", name='check_import_status'),
    )
    op.create_index('idx_import_jobs_workspace', 'import_jobs', ['workspace_id'])


def downgrade() -> None:
    op.drop_table('import_jobs')
