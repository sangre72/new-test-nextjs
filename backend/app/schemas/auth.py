"""
Authentication Schemas
Pydantic models for request/response validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re


# ============================================================================
# Request Schemas
# ============================================================================

class UserRegisterRequest(BaseModel):
    """회원가입 요청"""
    tenant_id: int = Field(..., description="Tenant ID", gt=0)
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")

    @validator("password")
    def validate_password(cls, v: str) -> str:
        """비밀번호 복잡도 검증"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v

    @validator("username")
    def validate_username(cls, v: str) -> str:
        """사용자명 형식 검증"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "password": "SecurePass123!",
                "full_name": "John Doe",
                "phone": "010-1234-5678"
            }
        }


class UserLoginRequest(BaseModel):
    """로그인 요청"""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")
    tenant_id: Optional[int] = Field(None, description="Tenant ID (optional)")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "SecurePass123!"
            }
        }


class TokenRefreshRequest(BaseModel):
    """토큰 갱신 요청"""
    refresh_token: str = Field(..., description="Refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class PasswordChangeRequest(BaseModel):
    """비밀번호 변경 요청"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")

    @validator("new_password")
    def validate_new_password(cls, v: str, values: dict) -> str:
        """새 비밀번호 검증"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        # 현재 비밀번호와 동일한지 확인
        if "current_password" in values and v == values["current_password"]:
            raise ValueError("New password must be different from current password")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldPass123!",
                "new_password": "NewSecurePass456!"
            }
        }


class ProfileUpdateRequest(BaseModel):
    """프로필 업데이트 요청"""
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = Field(None, max_length=500)
    profile_image_url: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe Updated",
                "phone": "010-9876-5432",
                "bio": "Software Engineer"
            }
        }


# ============================================================================
# Response Schemas
# ============================================================================

class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class UserResponse(BaseModel):
    """사용자 정보 응답"""
    id: int
    tenant_id: int
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    profile_image_url: Optional[str]
    bio: Optional[str]
    status: str
    is_superuser: bool
    is_email_verified: bool
    email_verified_at: Optional[datetime]
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 123,
                "tenant_id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "phone": "010-1234-5678",
                "profile_image_url": None,
                "bio": None,
                "status": "active",
                "is_superuser": False,
                "is_email_verified": True,
                "email_verified_at": "2024-01-01T00:00:00Z",
                "last_login_at": "2024-01-03T10:30:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-03T10:30:00Z"
            }
        }


class LoginResponse(BaseModel):
    """로그인 응답"""
    user: UserResponse
    tokens: TokenResponse

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": 123,
                    "username": "john_doe",
                    "email": "john@example.com"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIs...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                    "token_type": "bearer",
                    "expires_in": 1800
                }
            }
        }


class MessageResponse(BaseModel):
    """일반 메시지 응답"""
    message: str
    detail: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "detail": "Additional information"
            }
        }
