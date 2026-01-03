"""Create board tables

Revision ID: 004_create_board_tables
Revises: 003_update_menus_table
Create Date: 2024-01-03 10:00:00.000000

This migration creates the multi-board system tables including:
- boards (extended with board_type and permissions)
- board_categories
- board_posts
- board_comments
- board_attachments
- board_likes
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_create_board_tables'
down_revision = '003_update_menus_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create board-related tables (posts, comments, attachments, likes)

    Note: boards table is already created in 001_create_shared_schema with full features
    """

    # Create board_categories table
    op.create_table(
        'board_categories',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('board_id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('category_name', sa.String(100), nullable=False),
        sa.Column('category_code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['board_id'], ['boards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('board_id', 'category_code', name='uk_bcats_board_category_code'),
    )
    op.create_index('idx_bcats_board_id', 'board_categories', ['board_id'])
    op.create_index('idx_bcats_tenant_id', 'board_categories', ['tenant_id'])
    op.create_index('idx_bcats_display_order', 'board_categories', ['display_order'])

    # Create board_posts table
    op.create_table(
        'board_posts',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('board_id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('category_id', sa.BigInteger(), nullable=True),
        sa.Column('author_id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('draft', 'published', 'hidden', 'deleted', name='poststatusenum'), nullable=False, server_default='published'),
        sa.Column('is_secret', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_notice', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_answered', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('accepted_answer_id', sa.BigInteger(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('like_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('comment_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('post_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['board_id'], ['boards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['board_categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_posts_board_id', 'board_posts', ['board_id'])
    op.create_index('idx_posts_tenant_id', 'board_posts', ['tenant_id'])
    op.create_index('idx_posts_category_id', 'board_posts', ['category_id'])
    op.create_index('idx_posts_author_id', 'board_posts', ['author_id'])
    op.create_index('idx_posts_status', 'board_posts', ['status'])
    op.create_index('idx_posts_created_at', 'board_posts', ['created_at'])
    op.create_index('idx_posts_is_pinned', 'board_posts', ['is_pinned'])
    op.create_index('idx_posts_is_notice', 'board_posts', ['is_notice'])
    op.create_index('idx_posts_board_status_created', 'board_posts', ['board_id', 'status', 'created_at'])

    # Create board_comments table
    op.create_table(
        'board_comments',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('post_id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('author_id', sa.BigInteger(), nullable=False),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('published', 'hidden', 'deleted', name='commentstatusenum'), nullable=False, server_default='published'),
        sa.Column('is_secret', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_answer', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('like_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['post_id'], ['board_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['board_comments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_comments_post_id', 'board_comments', ['post_id'])
    op.create_index('idx_comments_tenant_id', 'board_comments', ['tenant_id'])
    op.create_index('idx_comments_author_id', 'board_comments', ['author_id'])
    op.create_index('idx_comments_parent_id', 'board_comments', ['parent_id'])
    op.create_index('idx_comments_status', 'board_comments', ['status'])
    op.create_index('idx_comments_created_at', 'board_comments', ['created_at'])

    # Create board_attachments table
    op.create_table(
        'board_attachments',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('post_id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('uploader_id', sa.BigInteger(), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('stored_filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('is_image', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('thumbnail_path', sa.String(500), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('download_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['post_id'], ['board_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploader_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_attach_post_id', 'board_attachments', ['post_id'])
    op.create_index('idx_attach_tenant_id', 'board_attachments', ['tenant_id'])
    op.create_index('idx_attach_uploader_id', 'board_attachments', ['uploader_id'])
    op.create_index('idx_attach_is_image', 'board_attachments', ['is_image'])

    # Create board_likes table
    op.create_table(
        'board_likes',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('post_id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['board_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('post_id', 'user_id', name='uk_post_user_like'),
    )
    op.create_index('idx_likes_post_id', 'board_likes', ['post_id'])
    op.create_index('idx_likes_tenant_id', 'board_likes', ['tenant_id'])
    op.create_index('idx_likes_user_id', 'board_likes', ['user_id'])


def downgrade() -> None:
    """Drop board-related tables (except boards which is in 001)"""
    op.drop_table('board_likes')
    op.drop_table('board_attachments')
    op.drop_table('board_comments')
    op.drop_table('board_posts')
    op.drop_table('board_categories')
