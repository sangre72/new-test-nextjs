"""
Board-related Models
Models for multi-board system including posts, comments, attachments, and likes
"""
from datetime import datetime
from sqlalchemy import (
    BigInteger, String, Text, DateTime, Boolean, Integer, JSON, ForeignKey,
    UniqueConstraint, Index, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from enum import Enum
from app.db.session import Base
from app.models.shared import AuditMixin


# Enums
class BoardTypeEnum(str, Enum):
    """Board type enumeration"""
    NOTICE = "notice"      # Notice board (admin only write, pinned posts)
    FREE = "free"          # Free board (anyone can write, comments enabled)
    QNA = "qna"           # Q&A board (question/answer, answer selection)
    FAQ = "faq"           # FAQ board (accordion style, Q&A pairs)
    GALLERY = "gallery"    # Gallery board (image grid, thumbnails)
    REVIEW = "review"      # Review board (star rating, recommendations)


class PermissionLevelEnum(str, Enum):
    """Permission level enumeration"""
    PUBLIC = "public"           # Anyone can access
    MEMBER = "member"           # Only authenticated members
    ADMIN = "admin"             # Only admins
    DISABLED = "disabled"       # Feature disabled


class PostStatusEnum(str, Enum):
    """Post status enumeration"""
    DRAFT = "draft"             # Draft (not published)
    PUBLISHED = "published"     # Published
    HIDDEN = "hidden"           # Hidden (by admin/moderator)
    DELETED = "deleted"         # Deleted


class CommentStatusEnum(str, Enum):
    """Comment status enumeration"""
    PUBLISHED = "published"     # Published
    HIDDEN = "hidden"           # Hidden (by admin/moderator)
    DELETED = "deleted"         # Deleted


# Models
class BoardExtended(Base, AuditMixin):
    """
    Extended Board model with multi-board type support
    Extends the basic Board model with type-specific features
    """
    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Tenant
    tenant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        comment="Tenant ID for multi-tenancy"
    )

    # Basic Information
    board_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Board display name"
    )
    board_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Unique board code within tenant (for URL)"
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Board Type
    board_type: Mapped[str] = mapped_column(
        SQLEnum(BoardTypeEnum, values_callable=lambda x: [e.value for e in x]),
        default=BoardTypeEnum.FREE,
        nullable=False,
        comment="Board type (notice/free/qna/faq/gallery/review)"
    )

    # Permissions
    read_permission: Mapped[str] = mapped_column(
        SQLEnum(PermissionLevelEnum, values_callable=lambda x: [e.value for e in x]),
        default=PermissionLevelEnum.PUBLIC,
        nullable=False,
        comment="Read permission level"
    )
    write_permission: Mapped[str] = mapped_column(
        SQLEnum(PermissionLevelEnum, values_callable=lambda x: [e.value for e in x]),
        default=PermissionLevelEnum.MEMBER,
        nullable=False,
        comment="Write permission level"
    )
    comment_permission: Mapped[str] = mapped_column(
        SQLEnum(PermissionLevelEnum, values_callable=lambda x: [e.value for e in x]),
        default=PermissionLevelEnum.MEMBER,
        nullable=False,
        comment="Comment permission level"
    )

    # Features
    enable_categories: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Enable category feature"
    )
    enable_secret_post: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Enable secret post feature"
    )
    enable_attachments: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Enable file attachments"
    )
    enable_likes: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Enable like/recommend feature"
    )
    enable_comments: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Enable comments"
    )

    # Board Settings (JSON)
    settings: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,
        comment="Board-specific settings (posts_per_page, max_file_size, etc.)"
    )

    # Display Order
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Display order in board list"
    )

    # Statistics (denormalized for performance)
    total_posts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of posts"
    )
    total_comments: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of comments"
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="boards")
    posts = relationship("BoardPost", back_populates="board", cascade="all, delete-orphan")
    categories = relationship("BoardCategory", back_populates="board", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        UniqueConstraint("tenant_id", "board_code", name="uk_tenant_board_code"),
        Index("idx_tenant_id", "tenant_id"),
        Index("idx_board_code", "board_code"),
        Index("idx_board_type", "board_type"),
        Index("idx_display_order", "display_order"),
    )

    def __repr__(self) -> str:
        return f"<Board(id={self.id}, code={self.board_code}, name={self.board_name})>"


class BoardCategory(Base, AuditMixin):
    """
    Board Category model
    Categories within a specific board (simple, non-hierarchical)
    """
    __tablename__ = "board_categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Board
    board_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False
    )

    # Tenant
    tenant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False
    )

    # Basic Information
    category_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Category name"
    )
    category_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Category code"
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Color for UI
    color: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
        comment="Category color (hex code)"
    )

    # Display Order
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Display order within board"
    )

    # Relationships
    board = relationship("BoardExtended", back_populates="categories")
    posts = relationship("BoardPost", back_populates="category")

    # Indexes
    __table_args__ = (
        UniqueConstraint("board_id", "category_code", name="uk_board_category_code"),
        Index("idx_board_id", "board_id"),
        Index("idx_tenant_id", "tenant_id"),
        Index("idx_display_order", "display_order"),
    )

    def __repr__(self) -> str:
        return f"<BoardCategory(id={self.id}, name={self.category_name})>"


class BoardPost(Base, AuditMixin):
    """
    Board Post model
    Posts for all board types (multi-board support)
    """
    __tablename__ = "board_posts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Board
    board_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False
    )

    # Tenant
    tenant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False
    )

    # Category (optional)
    category_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("board_categories.id", ondelete="SET NULL"),
        nullable=True
    )

    # Author
    author_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Content
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Post title"
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Post content (HTML/Markdown)"
    )

    # Status
    status: Mapped[str] = mapped_column(
        SQLEnum(PostStatusEnum, values_callable=lambda x: [e.value for e in x]),
        default=PostStatusEnum.PUBLISHED,
        nullable=False
    )

    # Secret Post (for privacy)
    is_secret: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Secret post (only author and admin can view)"
    )

    # Pinned (for notice boards)
    is_pinned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Pinned to top"
    )

    # Notice (highlight as important)
    is_notice: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Notice flag (highlight)"
    )

    # QNA specific
    is_answered: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="QNA: Has accepted answer"
    )
    accepted_answer_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True,
        comment="QNA: Accepted answer comment ID"
    )

    # Review specific
    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        comment="Review: Star rating (1-5)"
    )

    # Statistics (denormalized for performance)
    view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="View count"
    )
    like_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Like/recommend count"
    )
    comment_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Comment count"
    )

    # Metadata (JSON)
    post_metadata: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional metadata (tags, custom fields, etc.)"
    )

    # Published date (for scheduling)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Publication date"
    )

    # Relationships
    board = relationship("BoardExtended", back_populates="posts")
    category = relationship("BoardCategory", back_populates="posts")
    author = relationship("User")
    comments = relationship("BoardComment", back_populates="post", cascade="all, delete-orphan")
    attachments = relationship("BoardAttachment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("BoardLike", back_populates="post", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_board_id", "board_id"),
        Index("idx_tenant_id", "tenant_id"),
        Index("idx_category_id", "category_id"),
        Index("idx_author_id", "author_id"),
        Index("idx_status", "status"),
        Index("idx_created_at", "created_at"),
        Index("idx_is_pinned", "is_pinned"),
        Index("idx_is_notice", "is_notice"),
        Index("idx_board_status_created", "board_id", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<BoardPost(id={self.id}, title={self.title})>"


class BoardComment(Base, AuditMixin):
    """
    Board Comment model
    Comments on board posts (supports nested replies)
    """
    __tablename__ = "board_comments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Post
    post_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("board_posts.id", ondelete="CASCADE"),
        nullable=False
    )

    # Tenant
    tenant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False
    )

    # Author
    author_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Parent comment (for nested replies)
    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("board_comments.id", ondelete="CASCADE"),
        nullable=True,
        comment="Parent comment ID for nested replies"
    )

    # Content
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Comment content"
    )

    # Status
    status: Mapped[str] = mapped_column(
        SQLEnum(CommentStatusEnum, values_callable=lambda x: [e.value for e in x]),
        default=CommentStatusEnum.PUBLISHED,
        nullable=False
    )

    # Secret Comment
    is_secret: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Secret comment (only author and post author can view)"
    )

    # QNA Answer flag
    is_answer: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="QNA: Is this an answer (not a question follow-up)"
    )

    # Statistics
    like_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Like count"
    )

    # Relationships
    post = relationship("BoardPost", back_populates="comments")
    author = relationship("User")
    parent = relationship("BoardComment", remote_side=[id], backref="replies")

    # Indexes
    __table_args__ = (
        Index("idx_post_id", "post_id"),
        Index("idx_tenant_id", "tenant_id"),
        Index("idx_author_id", "author_id"),
        Index("idx_parent_id", "parent_id"),
        Index("idx_status", "status"),
        Index("idx_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<BoardComment(id={self.id}, post_id={self.post_id})>"


class BoardAttachment(Base, AuditMixin):
    """
    Board Attachment model
    File attachments for board posts
    """
    __tablename__ = "board_attachments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Post
    post_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("board_posts.id", ondelete="CASCADE"),
        nullable=False
    )

    # Tenant
    tenant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False
    )

    # Uploader
    uploader_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # File Information
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Original filename"
    )
    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Stored filename (UUID)"
    )
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="File storage path"
    )
    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="File size in bytes"
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="MIME type"
    )

    # Image specific
    is_image: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Is image file"
    )
    thumbnail_path: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        comment="Thumbnail path (for images)"
    )
    width: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        comment="Image width"
    )
    height: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        comment="Image height"
    )

    # Statistics
    download_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Download count"
    )

    # Display Order
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Display order"
    )

    # Relationships
    post = relationship("BoardPost", back_populates="attachments")
    uploader = relationship("User")

    # Indexes
    __table_args__ = (
        Index("idx_post_id", "post_id"),
        Index("idx_tenant_id", "tenant_id"),
        Index("idx_uploader_id", "uploader_id"),
        Index("idx_is_image", "is_image"),
    )

    def __repr__(self) -> str:
        return f"<BoardAttachment(id={self.id}, filename={self.original_filename})>"


class BoardLike(Base):
    """
    Board Like/Recommend model
    User likes on posts
    """
    __tablename__ = "board_likes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Post
    post_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("board_posts.id", ondelete="CASCADE"),
        nullable=False
    )

    # Tenant
    tenant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False
    )

    # User
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    post = relationship("BoardPost", back_populates="likes")
    user = relationship("User")

    # Indexes
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uk_post_user_like"),
        Index("idx_post_id", "post_id"),
        Index("idx_tenant_id", "tenant_id"),
        Index("idx_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<BoardLike(post_id={self.post_id}, user_id={self.user_id})>"
