"""
Category Management Models
Models for board categories with hierarchical structure
"""
from datetime import datetime
from sqlalchemy import (
    BigInteger, String, Text, DateTime, Boolean, ForeignKey,
    UniqueConstraint, Index, Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Category(Base):
    """
    Category model - represents a category within a board
    Supports hierarchical structure (parent-child relationships)
    """
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Tenant and Board relationships
    tenant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False
    )
    board_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False
    )

    # Hierarchical structure
    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        comment="Parent category ID for hierarchical structure"
    )
    depth: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Depth level in hierarchy (0 = root)"
    )
    path: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        comment="Path from root to this category (e.g., '/1/3/7/')"
    )

    # Basic Information
    category_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Display name of the category"
    )
    category_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Unique code for the category (slug)"
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Category description"
    )

    # Display Settings
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Display order within parent category"
    )
    icon: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        comment="Icon name/code (e.g., 'folder', 'star')"
    )
    color: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
        comment="Color code (e.g., '#FF5733')"
    )

    # Permissions
    read_permission: Mapped[str] = mapped_column(
        String(50),
        default="all",
        nullable=False,
        comment="Read permission level: all, members, admin"
    )
    write_permission: Mapped[str] = mapped_column(
        String(50),
        default="all",
        nullable=False,
        comment="Write permission level: all, members, admin"
    )

    # Statistics
    post_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of posts in this category (cache)"
    )

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    created_by: Mapped[str] = mapped_column(String(100), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Self-referential relationship for parent-child
    parent = relationship(
        "Category",
        back_populates="children",
        remote_side="Category.id",
        foreign_keys=[parent_id]
    )
    children = relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys="Category.parent_id"
    )

    # Indexes
    __table_args__ = (
        UniqueConstraint(
            "board_id", "category_code",
            name="uk_board_category_code"
        ),
        Index("idx_tenant_id", "tenant_id"),
        Index("idx_board_id", "board_id"),
        Index("idx_parent_id", "parent_id"),
        Index("idx_sort_order", "sort_order"),
        Index("idx_path", "path"),
        Index("idx_is_active", "is_active"),
        Index("idx_is_deleted", "is_deleted"),
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.category_name}, code={self.category_code})>"
