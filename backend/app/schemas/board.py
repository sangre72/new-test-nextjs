"""
Board-related Pydantic Schemas
Request/Response schemas for board operations
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


# ========== Board Schemas ==========

class BoardBase(BaseModel):
    """Base board schema"""
    board_name: str = Field(..., min_length=1, max_length=100, description="Board name")
    board_code: str = Field(..., min_length=1, max_length=50, description="Board code (URL)")
    description: Optional[str] = Field(None, description="Board description")
    board_type: str = Field("free", description="Board type (notice/free/qna/faq/gallery/review)")
    read_permission: str = Field("public", description="Read permission (public/member/admin/disabled)")
    write_permission: str = Field("member", description="Write permission")
    comment_permission: str = Field("member", description="Comment permission")
    enable_categories: bool = Field(True, description="Enable categories")
    enable_secret_post: bool = Field(False, description="Enable secret posts")
    enable_attachments: bool = Field(True, description="Enable attachments")
    enable_likes: bool = Field(True, description="Enable likes")
    enable_comments: bool = Field(True, description="Enable comments")
    settings: Optional[Dict[str, Any]] = Field(None, description="Additional settings")
    display_order: int = Field(0, description="Display order")


class BoardCreate(BoardBase):
    """Board creation schema"""
    tenant_id: int = Field(..., gt=0, description="Tenant ID")


class BoardUpdate(BaseModel):
    """Board update schema"""
    board_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    board_type: Optional[str] = None
    read_permission: Optional[str] = None
    write_permission: Optional[str] = None
    comment_permission: Optional[str] = None
    enable_categories: Optional[bool] = None
    enable_secret_post: Optional[bool] = None
    enable_attachments: Optional[bool] = None
    enable_likes: Optional[bool] = None
    enable_comments: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class BoardResponse(BoardBase):
    """Board response schema"""
    id: int
    tenant_id: int
    total_posts: int
    total_comments: int
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]
    is_active: bool
    is_deleted: bool

    class Config:
        from_attributes = True


# ========== Board Category Schemas ==========

class BoardCategoryBase(BaseModel):
    """Base board category schema"""
    category_name: str = Field(..., min_length=1, max_length=100)
    category_code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=20, description="Color (hex code)")
    display_order: int = Field(0)


class BoardCategoryCreate(BoardCategoryBase):
    """Board category creation schema"""
    board_id: int = Field(..., gt=0)
    tenant_id: int = Field(..., gt=0)


class BoardCategoryUpdate(BaseModel):
    """Board category update schema"""
    category_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class BoardCategoryResponse(BoardCategoryBase):
    """Board category response schema"""
    id: int
    board_id: int
    tenant_id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# ========== Board Post Schemas ==========

class BoardPostBase(BaseModel):
    """Base board post schema"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    category_id: Optional[int] = Field(None, gt=0)
    is_secret: bool = Field(False)
    is_pinned: bool = Field(False)
    is_notice: bool = Field(False)
    rating: Optional[int] = Field(None, ge=1, le=5, description="Star rating (1-5) for review type")
    metadata: Optional[Dict[str, Any]] = None


class BoardPostCreate(BoardPostBase):
    """Board post creation schema"""
    board_id: int = Field(..., gt=0)
    tenant_id: int = Field(..., gt=0)


class BoardPostUpdate(BaseModel):
    """Board post update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    category_id: Optional[int] = None
    is_secret: Optional[bool] = None
    is_pinned: Optional[bool] = None
    is_notice: Optional[bool] = None
    status: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    metadata: Optional[Dict[str, Any]] = None


class BoardPostListResponse(BaseModel):
    """Board post list response schema (simplified)"""
    id: int
    board_id: int
    category_id: Optional[int]
    category_name: Optional[str]
    author_id: int
    author_name: str
    title: str
    status: str
    is_secret: bool
    is_pinned: bool
    is_notice: bool
    is_answered: bool
    rating: Optional[int]
    view_count: int
    like_count: int
    comment_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BoardPostDetailResponse(BoardPostBase):
    """Board post detail response schema"""
    id: int
    board_id: int
    tenant_id: int
    author_id: int
    author_name: str
    author_email: Optional[str]
    category_name: Optional[str]
    status: str
    is_answered: bool
    accepted_answer_id: Optional[int]
    view_count: int
    like_count: int
    comment_count: int
    published_at: Optional[datetime]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]
    is_active: bool

    # Permissions for current user
    can_edit: bool = False
    can_delete: bool = False
    has_liked: bool = False

    class Config:
        from_attributes = True


class BoardPostListRequest(BaseModel):
    """Board post list request (query parameters)"""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    category_id: Optional[int] = None
    search: Optional[str] = None
    status: Optional[str] = None
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", description="Sort order (asc/desc)")


class BoardPostListPaginated(BaseModel):
    """Paginated board post list response"""
    items: List[BoardPostListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ========== Board Comment Schemas ==========

class BoardCommentBase(BaseModel):
    """Base board comment schema"""
    content: str = Field(..., min_length=1)
    parent_id: Optional[int] = Field(None, gt=0, description="Parent comment ID for nested replies")
    is_secret: bool = Field(False)
    is_answer: bool = Field(False, description="QNA: Is this an answer")


class BoardCommentCreate(BoardCommentBase):
    """Board comment creation schema"""
    post_id: int = Field(..., gt=0)
    tenant_id: int = Field(..., gt=0)


class BoardCommentUpdate(BaseModel):
    """Board comment update schema"""
    content: Optional[str] = Field(None, min_length=1)
    is_secret: Optional[bool] = None
    status: Optional[str] = None


class BoardCommentResponse(BoardCommentBase):
    """Board comment response schema"""
    id: int
    post_id: int
    tenant_id: int
    author_id: int
    author_name: str
    status: str
    like_count: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    # Permissions
    can_edit: bool = False
    can_delete: bool = False

    # Nested replies
    replies: List['BoardCommentResponse'] = []

    class Config:
        from_attributes = True


# ========== Board Attachment Schemas ==========

class BoardAttachmentBase(BaseModel):
    """Base board attachment schema"""
    original_filename: str
    file_size: int
    mime_type: Optional[str]
    is_image: bool = False
    width: Optional[int] = None
    height: Optional[int] = None


class BoardAttachmentCreate(BoardAttachmentBase):
    """Board attachment creation schema"""
    post_id: int = Field(..., gt=0)
    tenant_id: int = Field(..., gt=0)
    stored_filename: str
    file_path: str
    thumbnail_path: Optional[str] = None
    display_order: int = Field(0)


class BoardAttachmentResponse(BoardAttachmentBase):
    """Board attachment response schema"""
    id: int
    post_id: int
    download_count: int
    display_order: int
    created_at: datetime

    # URLs (generated)
    download_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    class Config:
        from_attributes = True


# ========== Board Like Schemas ==========

class BoardLikeCreate(BaseModel):
    """Board like creation schema"""
    post_id: int = Field(..., gt=0)
    tenant_id: int = Field(..., gt=0)


class BoardLikeResponse(BaseModel):
    """Board like response schema"""
    post_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Statistics Schemas ==========

class BoardStatistics(BaseModel):
    """Board statistics schema"""
    total_posts: int
    total_comments: int
    total_views: int
    total_likes: int
    recent_posts: int = Field(0, description="Posts in last 7 days")


class PostStatistics(BaseModel):
    """Post statistics schema"""
    view_count: int
    like_count: int
    comment_count: int
    is_liked_by_user: bool = False


# Enable forward references for nested models
BoardCommentResponse.model_rebuild()
