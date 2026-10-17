"""Add auth fields to users and workspaces

Revision ID: 003
Revises: 002
Create Date: 2026-10-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add full_name to users
    op.add_column('users', sa.Column('full_name', sa.String(255)))
    
    # Add owner_id to workspaces
    op.add_column('workspaces', sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_workspaces_owner', 'workspaces', 'users', ['owner_id'], ['id'], ondelete='CASCADE')
    op.create_index('idx_workspaces_owner', 'workspaces', ['owner_id'])


def downgrade() -> None:
    op.drop_index('idx_workspaces_owner', 'workspaces')
    op.drop_constraint('fk_workspaces_owner', 'workspaces', type_='foreignkey')
    op.drop_column('workspaces', 'owner_id')
    op.drop_column('users', 'full_name')
