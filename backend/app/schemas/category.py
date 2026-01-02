"""
Category Schemas (Pydantic v2)

카테고리 모델의 요청/응답 스키마 정의

포함:
- CategoryCreate: 카테고리 생성 요청
- CategoryUpdate: 카테고리 수정 요청
- CategoryResponse: 카테고리 응답
- CategoryReorder: 카테고리 순서/계층 변경 요청
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


# ============================================================
# Category Request/Response Schemas
# ============================================================
class CategoryCreate(BaseModel):
    """카테고리 생성 요청"""

    board_id: int = Field(..., gt=0, description="게시판 ID")
    parent_id: Optional[int] = Field(
        None, ge=0, description="상위 카테고리 ID (NULL이면 최상위)"
    )
    category_name: str = Field(
        ..., min_length=1, max_length=100, description="카테고리명"
    )
    category_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[a-z0-9_]+$",
        description="카테고리 코드 (영문 소문자, 숫자, 언더스코어)",
    )
    description: Optional[str] = Field(
        None, max_length=500, description="설명"
    )
    sort_order: int = Field(0, ge=0, description="정렬 순서 (낮을수록 앞)")
    icon: Optional[str] = Field(None, max_length=50, description="아이콘")
    color: Optional[str] = Field(
        None, max_length=20, description="색상 (HEX, 예: #FF0000)"
    )
    read_permission: str = Field(
        "all",
        description="읽기 권한 (all/members/admin)",
    )
    write_permission: str = Field(
        "all",
        description="쓰기 권한 (all/members/admin)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "board_id": 1,
                "parent_id": None,
                "category_name": "일반",
                "category_code": "general",
                "description": "일반 공지사항",
                "sort_order": 0,
                "icon": "folder",
                "color": "#1976d2",
                "read_permission": "all",
                "write_permission": "members",
            }
        }
    )


class CategoryUpdate(BaseModel):
    """카테고리 수정 요청"""

    parent_id: Optional[int] = Field(
        None, ge=0, description="상위 카테고리 ID"
    )
    category_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="카테고리명"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="설명"
    )
    sort_order: Optional[int] = Field(
        None, ge=0, description="정렬 순서"
    )
    icon: Optional[str] = Field(None, max_length=50, description="아이콘")
    color: Optional[str] = Field(
        None, max_length=20, description="색상 (HEX)"
    )
    read_permission: Optional[str] = Field(
        None, description="읽기 권한"
    )
    write_permission: Optional[str] = Field(
        None, description="쓰기 권한"
    )
    is_active: Optional[bool] = Field(None, description="활성 여부")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category_name": "긴급 공지",
                "description": "긴급한 내용",
                "is_active": True,
            }
        }
    )


class CategoryResponse(BaseModel):
    """카테고리 응답"""

    id: int
    tenant_id: int
    board_id: int
    parent_id: Optional[int]
    depth: int
    path: Optional[str]
    category_name: str
    category_code: str
    description: Optional[str]
    sort_order: int
    icon: Optional[str]
    color: Optional[str]
    read_permission: str
    write_permission: str
    post_count: int
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]
    is_active: bool
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class CategoryWithChildren(CategoryResponse):
    """자식 카테고리가 포함된 카테고리 응답 (계층형 트리용)"""

    children: List["CategoryWithChildren"] = Field(
        default_factory=list, description="하위 카테고리"
    )


# Forward reference 업데이트
CategoryWithChildren.model_rebuild()


class CategoryReorder(BaseModel):
    """카테고리 순서/계층 변경 요청"""

    category_id: int = Field(..., gt=0, description="카테고리 ID")
    parent_id: Optional[int] = Field(
        None, description="새로운 상위 카테고리 ID"
    )
    sort_order: int = Field(0, ge=0, description="새로운 정렬 순서")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category_id": 3,
                "parent_id": 1,
                "sort_order": 5,
            }
        }
    )


class CategoryBulkMove(BaseModel):
    """여러 카테고리 순서 변경 요청"""

    reorders: List[CategoryReorder] = Field(
        ..., description="순서 변경 목록"
    )


# ============================================================
# 공통 응답 스키마
# ============================================================
class CategoryListResponse(BaseModel):
    """카테고리 목록 응답 (계층형 트리)"""

    success: bool = True
    data: List[CategoryWithChildren] = Field(
        default_factory=list, description="카테고리 계층형 트리"
    )
    total: int = 0
    message: Optional[str] = None


class CategoryFlatResponse(BaseModel):
    """카테고리 목록 응답 (평면)"""

    success: bool = True
    data: List[CategoryResponse] = Field(
        default_factory=list, description="카테고리 평면 리스트"
    )
    total: int = 0
    message: Optional[str] = None


class CategoryDetailResponse(BaseModel):
    """카테고리 상세 조회 응답"""

    success: bool = True
    data: CategoryResponse
    message: Optional[str] = None


class SuccessMessageResponse(BaseModel):
    """성공 응답 (메시지만)"""

    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """실패 응답"""

    success: bool = False
    error_code: str
    message: str
