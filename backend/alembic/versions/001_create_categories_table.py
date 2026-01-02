"""Create categories table

Revision ID: 001
Revises:
Create Date: 2026-01-03

카테고리 테이블 생성 마이그레이션
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """테이블 생성"""
    op.create_table(
        "categories",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.BigInteger(), nullable=False),
        sa.Column("board_id", sa.BigInteger(), nullable=False),
        sa.Column("parent_id", sa.BigInteger(), nullable=True),
        sa.Column("depth", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("path", sa.String(length=500), nullable=True),
        sa.Column("category_name", sa.String(length=100), nullable=False),
        sa.Column("category_code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column(
            "read_permission",
            sa.String(length=50),
            nullable=False,
            server_default="all",
        ),
        sa.Column(
            "write_permission",
            sa.String(length=50),
            nullable=False,
            server_default="all",
        ),
        sa.Column("post_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_by", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["categories.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "board_id",
            "category_code",
            name="uk_board_category_code",
        ),
    )

    # 인덱스 생성
    op.create_index("idx_tenant_board", "categories", ["tenant_id", "board_id"])
    op.create_index("idx_path_search", "categories", ["path"])
    op.create_index("idx_categories_tenant_id", "categories", ["tenant_id"])
    op.create_index("idx_categories_board_id", "categories", ["board_id"])
    op.create_index("idx_categories_parent_id", "categories", ["parent_id"])
    op.create_index("idx_categories_depth", "categories", ["depth"])
    op.create_index("idx_categories_sort_order", "categories", ["sort_order"])


def downgrade() -> None:
    """테이블 삭제"""
    op.drop_table("categories")
