"""
Pydantic Schemas for Shared Models
Used for request/response validation and serialization
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Enums for Pydantic
class TenantStatusEnum(str):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class UserStatusEnum(str):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


# ==================== Tenant Schemas ====================

class TenantBase(BaseModel):
    """Base tenant schema"""
    tenant_code: str = Field(..., min_length=1, max_length=50, description="Tenant code")
    tenant_name: str = Field(..., min_length=1, max_length=100, description="Tenant name")
    description: Optional[str] = Field(None, max_length=500)
    domain: Optional[str] = Field(None, max_length=255)
    subdomain: Optional[str] = Field(None, max_length=100)
    settings: Optional[dict] = None
    admin_email: Optional[EmailStr] = None
    admin_name: Optional[str] = Field(None, max_length=100)
    status: str = Field(default="active")


class TenantCreate(TenantBase):
    """Schema for creating tenant"""
    pass


class TenantUpdate(BaseModel):
    """Schema for updating tenant"""
    tenant_name: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    subdomain: Optional[str] = None
    settings: Optional[dict] = None
    admin_email: Optional[EmailStr] = None
    admin_name: Optional[str] = None
    status: Optional[str] = None


class TenantResponse(TenantBase):
    """Schema for tenant response"""
    id: int
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: datetime
    updated_by: Optional[str] = None
    is_active: bool
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class TenantDetailResponse(TenantResponse):
    """Detailed tenant response with relationships"""
    users: Optional[List["UserResponse"]] = []
    user_groups: Optional[List["UserGroupResponse"]] = []


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating user"""
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    tenant_id: int


class UserUpdate(BaseModel):
    """Schema for updating user"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    status: Optional[str] = None
    is_superuser: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    tenant_id: int
    is_superuser: bool
    profile_image_url: Optional[str] = None
    status: str
    is_email_verified: bool
    email_verified_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: datetime
    updated_by: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(UserResponse):
    """Detailed user response with relationships"""
    user_groups: Optional[List["UserGroupResponse"]] = []
    roles: Optional[List["RoleResponse"]] = []


# ==================== User Group Schemas ====================

class UserGroupBase(BaseModel):
    """Base user group schema"""
    group_name: str = Field(..., min_length=1, max_length=100)
    group_code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    priority: int = Field(default=0)
    group_type: str = Field(default="custom")
    tenant_id: Optional[int] = None


class UserGroupCreate(UserGroupBase):
    """Schema for creating user group"""
    pass


class UserGroupUpdate(BaseModel):
    """Schema for updating user group"""
    group_name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class UserGroupResponse(UserGroupBase):
    """Schema for user group response"""
    id: int
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: datetime
    updated_by: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserGroupDetailResponse(UserGroupResponse):
    """Detailed user group response with relationships"""
    users: Optional[List[UserResponse]] = []


class UserGroupMemberCreate(BaseModel):
    """Schema for adding user to group"""
    user_id: int
    group_id: int


class UserGroupMemberResponse(BaseModel):
    """Schema for user group member response"""
    id: int
    user_id: int
    group_id: int
    created_at: datetime
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== Role Schemas ====================

class RoleBase(BaseModel):
    """Base role schema"""
    role_name: str = Field(..., min_length=1, max_length=100)
    role_code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    priority: int = Field(default=0)
    role_type: str = Field(default="both")


class RoleCreate(RoleBase):
    """Schema for creating role"""
    pass


class RoleUpdate(BaseModel):
    """Schema for updating role"""
    role_name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    """Schema for role response"""
    id: int
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: datetime
    updated_by: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class RoleDetailResponse(RoleResponse):
    """Detailed role response with relationships"""
    permissions: Optional[List["PermissionResponse"]] = []


class UserRoleCreate(BaseModel):
    """Schema for assigning role to user"""
    user_id: int
    role_id: int


class UserRoleResponse(BaseModel):
    """Schema for user role response"""
    id: int
    user_id: int
    role_id: int
    created_at: datetime
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== Permission Schemas ====================

class PermissionBase(BaseModel):
    """Base permission schema"""
    permission_name: str = Field(..., min_length=1, max_length=100)
    permission_code: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    resource: str
    action: str


class PermissionCreate(PermissionBase):
    """Schema for creating permission"""
    pass


class PermissionUpdate(BaseModel):
    """Schema for updating permission"""
    permission_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionResponse(PermissionBase):
    """Schema for permission response"""
    id: int
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: datetime
    updated_by: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class RolePermissionCreate(BaseModel):
    """Schema for assigning permission to role"""
    role_id: int
    permission_id: int


class RolePermissionResponse(BaseModel):
    """Schema for role permission response"""
    id: int
    role_id: int
    permission_id: int
    created_at: datetime
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== Menu Schemas ====================

class MenuBase(BaseModel):
    """Base menu schema"""
    menu_name: str = Field(..., min_length=1, max_length=100)
    menu_code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    menu_url: Optional[str] = Field(None, max_length=500)
    menu_icon: Optional[str] = Field(None, max_length=100)
    display_order: int = Field(default=0)
    parent_id: Optional[int] = None
    tenant_id: int


class MenuCreate(MenuBase):
    """Schema for creating menu"""
    pass


class MenuUpdate(BaseModel):
    """Schema for updating menu"""
    menu_name: Optional[str] = None
    description: Optional[str] = None
    menu_url: Optional[str] = None
    menu_icon: Optional[str] = None
    display_order: Optional[int] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None


class MenuResponse(MenuBase):
    """Schema for menu response"""
    id: int
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: datetime
    updated_by: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ==================== Board Schemas ====================

class BoardBase(BaseModel):
    """Base board schema"""
    board_name: str = Field(..., min_length=1, max_length=100)
    board_code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    tenant_id: int


class BoardCreate(BoardBase):
    """Schema for creating board"""
    pass


class BoardUpdate(BaseModel):
    """Schema for updating board"""
    board_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class BoardResponse(BoardBase):
    """Schema for board response"""
    id: int
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: datetime
    updated_by: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# Update forward references
UserGroupDetailResponse.model_rebuild()
UserDetailResponse.model_rebuild()
RoleDetailResponse.model_rebuild()
