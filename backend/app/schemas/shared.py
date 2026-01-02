"""
Shared Schemas (Pydantic v2)

공유 모델의 요청/응답 스키마 정의

포함:
- TenantSchema
- UserGroupSchema
- RoleSchema
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum


# ============================================================
# Enums
# ============================================================
class GroupTypeEnum(str, Enum):
    """그룹 타입"""
    SYSTEM = "system"
    CUSTOM = "custom"


class RoleScopeEnum(str, Enum):
    """역할 범위"""
    ADMIN = "admin"
    USER = "user"
    BOTH = "both"


# ============================================================
# Tenant Schemas
# ============================================================
class TenantCreate(BaseModel):
    """테넌트 생성 요청"""
    tenant_code: str = Field(..., min_length=1, max_length=50)
    tenant_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    domain: Optional[str] = Field(None, max_length=255)
    subdomain: Optional[str] = Field(None, max_length=100)
    admin_email: Optional[str] = Field(None, max_length=255)
    admin_name: Optional[str] = Field(None, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tenant_code": "siteA",
                "tenant_name": "사이트 A",
                "description": "쇼핑몰",
                "domain": "siteA.com",
                "subdomain": "siteA",
                "admin_email": "admin@siteA.com",
                "admin_name": "관리자",
            }
        }
    )


class TenantUpdate(BaseModel):
    """테넌트 수정 요청"""
    tenant_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    domain: Optional[str] = Field(None, max_length=255)
    subdomain: Optional[str] = Field(None, max_length=100)
    admin_email: Optional[str] = Field(None, max_length=255)
    admin_name: Optional[str] = Field(None, max_length=100)


class TenantResponse(BaseModel):
    """테넌트 응답"""
    id: int
    tenant_code: str
    tenant_name: str
    description: Optional[str]
    domain: Optional[str]
    subdomain: Optional[str]
    admin_email: Optional[str]
    admin_name: Optional[str]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]
    is_active: bool
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# UserGroup Schemas
# ============================================================
class UserGroupCreate(BaseModel):
    """사용자 그룹 생성 요청"""
    tenant_id: Optional[int] = None
    group_name: str = Field(..., min_length=1, max_length=100)
    group_code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    priority: int = Field(0, ge=0)
    group_type: GroupTypeEnum = GroupTypeEnum.CUSTOM


class UserGroupUpdate(BaseModel):
    """사용자 그룹 수정 요청"""
    group_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[int] = Field(None, ge=0)


class UserGroupResponse(BaseModel):
    """사용자 그룹 응답"""
    id: int
    tenant_id: Optional[int]
    group_name: str
    group_code: str
    description: Optional[str]
    priority: int
    group_type: GroupTypeEnum
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]
    is_active: bool
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class UserGroupWithMembers(UserGroupResponse):
    """멤버 정보가 포함된 사용자 그룹"""
    member_count: Optional[int] = 0


# ============================================================
# UserGroupMember Schemas
# ============================================================
class UserGroupMemberCreate(BaseModel):
    """사용자-그룹 매핑 생성 요청"""
    user_id: str = Field(..., min_length=1, max_length=50)
    group_id: int


class UserGroupMemberResponse(BaseModel):
    """사용자-그룹 매핑 응답"""
    id: int
    user_id: str
    group_id: int
    created_at: datetime
    created_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Role Schemas
# ============================================================
class RoleCreate(BaseModel):
    """역할 생성 요청"""
    role_name: str = Field(..., min_length=1, max_length=100)
    role_code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    priority: int = Field(0, ge=0)
    role_scope: RoleScopeEnum = RoleScopeEnum.BOTH


class RoleUpdate(BaseModel):
    """역할 수정 요청"""
    role_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[int] = Field(None, ge=0)


class RoleResponse(BaseModel):
    """역할 응답"""
    id: int
    role_name: str
    role_code: str
    description: Optional[str]
    priority: int
    role_scope: RoleScopeEnum
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]
    is_active: bool
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# UserRole Schemas
# ============================================================
class UserRoleCreate(BaseModel):
    """사용자-역할 매핑 생성 요청"""
    user_id: str = Field(..., min_length=1, max_length=50)
    role_id: int


class UserRoleResponse(BaseModel):
    """사용자-역할 매핑 응답"""
    id: int
    user_id: str
    role_id: int
    created_at: datetime
    created_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 공통 응답 스키마
# ============================================================
class SuccessResponse(BaseModel):
    """성공 응답 (일반)"""
    success: bool = True
    data: Optional[dict] = None
    message: Optional[str] = None


class ListResponse(BaseModel):
    """성공 응답 (리스트)"""
    success: bool = True
    data: list = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20


class ErrorResponse(BaseModel):
    """실패 응답"""
    success: bool = False
    error_code: str
    message: str
