"""
Pydantic Schemas for Category Management
Used for request/response validation and serialization
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ==================== Category Schemas ====================

class CategoryBase(BaseModel):
    """Base category schema"""
    category_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Category name"
    )
    category_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern="^[a-z0-9_]+$",
        description="Category code (lowercase, numbers, underscore only)"
    )
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    sort_order: int = Field(default=0)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    read_permission: str = Field(
        default="all",
        description="Read permission: all, members, admin"
    )
    write_permission: str = Field(
        default="all",
        description="Write permission: all, members, admin"
    )


class CategoryCreate(CategoryBase):
    """Schema for creating category"""
    board_id: int = Field(..., description="Board ID")
    tenant_id: int = Field(..., description="Tenant ID")


class CategoryUpdate(BaseModel):
    """Schema for updating category"""
    category_name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    read_permission: Optional[str] = None
    write_permission: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema for category response"""
    id: int
    tenant_id: int
    board_id: int
    depth: int
    path: Optional[str] = None
    post_count: int
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: datetime
    updated_by: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CategoryTreeResponse(CategoryResponse):
    """Hierarchical category response with children"""
    children: Optional[List["CategoryTreeResponse"]] = []

    model_config = ConfigDict(from_attributes=True)


class CategoryFlatResponse(CategoryResponse):
    """Flat category response (for lists)"""
    model_config = ConfigDict(from_attributes=True)


class CategoryDetailResponse(CategoryResponse):
    """Detailed category response"""
    # Additional fields for detail view
    model_config = ConfigDict(from_attributes=True)


class CategoryReorderRequest(BaseModel):
    """Schema for reordering categories (drag and drop)"""
    category_id: int = Field(..., description="Category to move")
    new_parent_id: Optional[int] = Field(None, description="New parent category ID")
    new_sort_order: int = Field(..., description="New sort order")


class CategoryBulkUpdateRequest(BaseModel):
    """Schema for bulk updating categories"""
    category_ids: List[int] = Field(..., description="List of category IDs to update")
    updates: dict = Field(..., description="Fields to update")


# Update forward references
CategoryTreeResponse.model_rebuild()
