"""
Menu Schemas
Pydantic models for menu API request/response validation
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator, constr, conint
from app.models.shared import MenuTypeEnum, MenuPermissionTypeEnum, MenuLinkTypeEnum


# ============================================================================
# Base Schemas
# ============================================================================

class MenuBase(BaseModel):
    """Base menu schema with common fields"""
    menu_name: constr(min_length=1, max_length=100) = Field(
        ...,
        description="Menu display name",
        example="Dashboard"
    )
    menu_code: constr(min_length=1, max_length=50) = Field(
        ...,
        description="Unique menu code",
        example="dashboard"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Menu description",
        example="Main dashboard page"
    )
    menu_type: MenuTypeEnum = Field(
        default=MenuTypeEnum.USER,
        description="Menu type: user, site, admin"
    )
    menu_url: Optional[constr(max_length=500)] = Field(
        None,
        description="Menu URL or route path",
        example="/dashboard"
    )
    menu_icon: Optional[constr(max_length=100)] = Field(
        None,
        description="Icon class or name",
        example="fa-dashboard"
    )
    link_type: MenuLinkTypeEnum = Field(
        default=MenuLinkTypeEnum.INTERNAL,
        description="Link behavior type"
    )
    parent_id: Optional[int] = Field(
        None,
        description="Parent menu ID for hierarchy",
        example=1
    )
    display_order: conint(ge=0) = Field(
        default=0,
        description="Display order within same parent",
        example=1
    )
    permission_type: MenuPermissionTypeEnum = Field(
        default=MenuPermissionTypeEnum.PUBLIC,
        description="Permission requirement type"
    )
    is_visible: bool = Field(
        default=True,
        description="Whether menu is visible"
    )
    is_active: bool = Field(
        default=True,
        description="Whether menu is active"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata (badge, tooltip, etc.)",
        example={"badge": "New", "tooltip": "New feature"}
    )

    @validator('menu_code')
    def validate_menu_code(cls, v):
        """Validate menu code format"""
        if not v:
            raise ValueError('menu_code is required')

        # Check for dangerous characters
        dangerous_chars = ['<', '>', '&', '"', "'", '/', '\\', ';', '--']
        if any(char in v for char in dangerous_chars):
            raise ValueError('menu_code contains invalid characters')

        # Only allow alphanumeric, underscore, hyphen
        if not all(c.isalnum() or c in ['_', '-'] for c in v):
            raise ValueError('menu_code can only contain alphanumeric, underscore, and hyphen')

        return v.strip().lower()

    @validator('menu_url')
    def validate_menu_url(cls, v):
        """Validate menu URL"""
        if v is None:
            return v

        # Trim whitespace
        v = v.strip()

        # Check length
        if len(v) > 500:
            raise ValueError('menu_url exceeds maximum length of 500')

        # Basic XSS protection
        dangerous_patterns = ['javascript:', '<script', 'onerror=', 'onclick=', 'onload=']
        if any(pattern in v.lower() for pattern in dangerous_patterns):
            raise ValueError('menu_url contains invalid patterns')

        return v

    @validator('metadata')
    def validate_metadata(cls, v):
        """Validate metadata structure"""
        if v is None:
            return v

        # Ensure it's a dict
        if not isinstance(v, dict):
            raise ValueError('metadata must be a dictionary')

        # Check for string values to prevent XSS
        def check_strings(obj):
            if isinstance(obj, str):
                dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onclick=']
                if any(pattern in obj.lower() for pattern in dangerous_patterns):
                    raise ValueError('metadata contains invalid patterns')
            elif isinstance(obj, dict):
                for value in obj.values():
                    check_strings(value)
            elif isinstance(obj, list):
                for item in obj:
                    check_strings(item)

        check_strings(v)
        return v


# ============================================================================
# Request Schemas
# ============================================================================

class MenuCreate(MenuBase):
    """Schema for creating a new menu"""
    pass


class MenuUpdate(BaseModel):
    """Schema for updating an existing menu (all fields optional)"""
    menu_name: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None
    menu_type: Optional[MenuTypeEnum] = None
    menu_url: Optional[constr(max_length=500)] = None
    menu_icon: Optional[constr(max_length=100)] = None
    link_type: Optional[MenuLinkTypeEnum] = None
    parent_id: Optional[int] = None
    display_order: Optional[conint(ge=0)] = None
    permission_type: Optional[MenuPermissionTypeEnum] = None
    is_visible: Optional[bool] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('menu_url')
    def validate_menu_url(cls, v):
        """Validate menu URL"""
        if v is None:
            return v

        v = v.strip()
        if len(v) > 500:
            raise ValueError('menu_url exceeds maximum length of 500')

        dangerous_patterns = ['javascript:', '<script', 'onerror=', 'onclick=', 'onload=']
        if any(pattern in v.lower() for pattern in dangerous_patterns):
            raise ValueError('menu_url contains invalid patterns')

        return v

    @validator('metadata')
    def validate_metadata(cls, v):
        """Validate metadata structure"""
        if v is None:
            return v

        if not isinstance(v, dict):
            raise ValueError('metadata must be a dictionary')

        def check_strings(obj):
            if isinstance(obj, str):
                dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onclick=']
                if any(pattern in obj.lower() for pattern in dangerous_patterns):
                    raise ValueError('metadata contains invalid patterns')
            elif isinstance(obj, dict):
                for value in obj.values():
                    check_strings(value)
            elif isinstance(obj, list):
                for item in obj:
                    check_strings(item)

        check_strings(v)
        return v


class MenuReorder(BaseModel):
    """Schema for reordering menus"""
    menu_id: int = Field(..., description="Menu ID to reorder")
    new_order: conint(ge=0) = Field(..., description="New display order")


class MenuBulkReorder(BaseModel):
    """Schema for bulk reordering menus"""
    items: List[MenuReorder] = Field(
        ...,
        description="List of menu reorder items",
        min_items=1
    )


class MenuMove(BaseModel):
    """Schema for moving a menu to a different parent"""
    new_parent_id: Optional[int] = Field(
        None,
        description="New parent ID (null for root level)"
    )
    new_order: Optional[conint(ge=0)] = Field(
        None,
        description="New display order in the new parent"
    )


# ============================================================================
# Response Schemas
# ============================================================================

class MenuResponse(MenuBase):
    """Schema for menu response"""
    id: int
    tenant_id: int
    depth: int
    path: Optional[str]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]
    is_deleted: bool

    class Config:
        from_attributes = True


class MenuTreeNode(MenuResponse):
    """Schema for menu tree node with children"""
    children: List['MenuTreeNode'] = []

    class Config:
        from_attributes = True


# Enable forward reference for recursive type
MenuTreeNode.model_rebuild()


class MenuListResponse(BaseModel):
    """Schema for menu list response"""
    total: int
    items: List[MenuResponse]


class MenuTreeResponse(BaseModel):
    """Schema for menu tree response"""
    total: int
    items: List[MenuTreeNode]


class MenuBulkDeleteRequest(BaseModel):
    """Schema for bulk delete request"""
    menu_ids: List[int] = Field(
        ...,
        description="List of menu IDs to delete",
        min_items=1
    )


# ============================================================================
# Query Parameters
# ============================================================================

class MenuQueryParams(BaseModel):
    """Query parameters for menu list"""
    menu_type: Optional[MenuTypeEnum] = Field(
        None,
        description="Filter by menu type"
    )
    parent_id: Optional[int] = Field(
        None,
        description="Filter by parent ID (null for root menus)"
    )
    is_visible: Optional[bool] = Field(
        None,
        description="Filter by visibility"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Filter by active status"
    )
    search: Optional[str] = Field(
        None,
        max_length=100,
        description="Search by menu name or code"
    )
    skip: conint(ge=0) = Field(
        default=0,
        description="Number of records to skip"
    )
    limit: conint(ge=1, le=100) = Field(
        default=50,
        description="Maximum number of records to return"
    )

    @validator('search')
    def validate_search(cls, v):
        """Validate search query"""
        if v is None:
            return v

        v = v.strip()
        if len(v) > 100:
            raise ValueError('search query exceeds maximum length of 100')

        # Prevent SQL injection patterns
        dangerous_patterns = ['--', ';--', '/*', '*/', 'xp_', 'sp_', 'exec ', 'execute ']
        if any(pattern in v.lower() for pattern in dangerous_patterns):
            raise ValueError('search query contains invalid patterns')

        return v
