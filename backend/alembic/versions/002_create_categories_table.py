"""Create categories table

Revision ID: 002_create_categories_table
Revises: 001_create_shared_schema
Create Date: 2024-01-03 08:30:00.000000

This migration creates the categories table for board category management
with support for hierarchical structure.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_create_categories_table'
down_revision = '001_create_shared_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create categories table"""

    op.create_table(
        'categories',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('board_id', sa.BigInteger(), nullable=False),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('depth', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('path', sa.String(500), nullable=True),
        sa.Column('category_name', sa.String(100), nullable=False),
        sa.Column('category_code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('read_permission', sa.String(50), nullable=False, server_default='all'),
        sa.Column('write_permission', sa.String(50), nullable=False, server_default='all'),
        sa.Column('post_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['board_id'], ['boards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('board_id', 'category_code', name='uk_board_category_code'),
    )

    op.create_index('idx_tenant_id', 'categories', ['tenant_id'])
    op.create_index('idx_board_id', 'categories', ['board_id'])
    op.create_index('idx_parent_id', 'categories', ['parent_id'])
    op.create_index('idx_sort_order', 'categories', ['sort_order'])
    op.create_index('idx_path', 'categories', ['path'])
    op.create_index('idx_is_active', 'categories', ['is_active'])
    op.create_index('idx_is_deleted', 'categories', ['is_deleted'])


def downgrade() -> None:
    """Drop categories table"""

    op.drop_table('categories')
