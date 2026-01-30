"""add export_allow_partial to projects table

Revision ID: 013
Revises: 012_add_user_token_to_settings
Create Date: 2025-01-29

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '013'
down_revision = '012_add_user_token_to_settings'
branch_labels = None
depends_on = None


def upgrade():
    # Add export_allow_partial column to projects table
    op.add_column('projects', sa.Column('export_allow_partial', sa.Boolean(), nullable=True, server_default='0'))
    # 为现有行设置默认值 false，避免 NULL 状态
    op.execute("UPDATE projects SET export_allow_partial = false WHERE export_allow_partial IS NULL")


def downgrade():
    op.drop_column('projects', 'export_allow_partial')
