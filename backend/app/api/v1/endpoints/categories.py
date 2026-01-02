"""
카테고리 관리 API

엔드포인트:
- GET /api/v1/categories/board/{board_id} - 카테고리 목록 조회 (계층형 트리)
- GET /api/v1/categories/board/{board_id}/flat - 카테고리 목록 조회 (평면)
- GET /api/v1/categories/{category_id} - 카테고리 상세 조회
- POST /api/v1/categories - 카테고리 생성
- PUT /api/v1/categories/{category_id} - 카테고리 수정
- DELETE /api/v1/categories/{category_id} - 카테고리 삭제
- PUT /api/v1/categories/{category_id}/move - 카테고리 계층 변경
- PUT /api/v1/categories/reorder - 카테고리 순서 변경

권한:
- 조회: Public
- 생성/수정/삭제: Admin
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import get_session, get_current_user_id, get_current_tenant_id
from app.services.category import CategoryService
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithChildren,
    CategoryReorder,
    CategoryListResponse,
    CategoryFlatResponse,
    CategoryDetailResponse,
    SuccessMessageResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/categories", tags=["categories"])


# ============================================================
# 헬퍼 함수
# ============================================================
def _to_category_with_children(category) -> CategoryWithChildren:
    """Category 모델을 CategoryWithChildren 스키마로 변환"""
    data = CategoryWithChildren.model_validate(category)
    if hasattr(category, "children") and category.children:
        data.children = [_to_category_with_children(child) for child in category.children]
    else:
        data.children = []
    return data


async def _check_admin_permission(
    user_id: Optional[str] = Depends(get_current_user_id),
) -> str:
    """관리자 권한 확인 (임시 구현)"""
    # TODO: auth-backend에서 제공하는 권한 확인 로직으로 대체
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다.",
        )
    return user_id


# ============================================================
# 조회 API
# ============================================================
@router.get(
    "/board/{board_id}",
    response_model=CategoryListResponse,
    summary="카테고리 목록 조회 (계층형 트리)",
    responses={
        200: {"description": "성공"},
        404: {"description": "게시판을 찾을 수 없음"},
    },
)
async def list_categories_tree(
    board_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
) -> CategoryListResponse:
    """
    게시판의 모든 카테고리를 계층형 트리 구조로 반환합니다.

    - **board_id**: 게시판 ID
    - **결과**: 최상위 카테고리들과 그 하위 카테고리들

    예시:
    ```json
    {
      "success": true,
      "data": [
        {
          "id": 1,
          "category_name": "공지사항",
          "category_code": "notice",
          "children": [
            {
              "id": 2,
              "category_name": "일반",
              "category_code": "general",
              "children": []
            }
          ]
        }
      ]
    }
    ```
    """
    try:
        # 최상위 카테고리들 조회
        categories = await CategoryService.get_categories_tree(
            session=session,
            tenant_id=tenant_id,
            board_id=board_id,
        )

        # 계층형 트리로 변환
        tree_data = [_to_category_with_children(cat) for cat in categories]

        return CategoryListResponse(
            success=True,
            data=tree_data,
            total=len(categories),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리 목록 조회 실패: {str(e)}",
        )


@router.get(
    "/board/{board_id}/flat",
    response_model=CategoryFlatResponse,
    summary="카테고리 목록 조회 (평면)",
    responses={
        200: {"description": "성공"},
    },
)
async def list_categories_flat(
    board_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> CategoryFlatResponse:
    """
    게시판의 모든 카테고리를 평면(flat) 리스트로 반환합니다.

    - **board_id**: 게시판 ID
    - **skip**: 건너뛸 개수 (페이징)
    - **limit**: 반환할 최대 개수 (기본값: 100, 최대: 1000)
    """
    try:
        categories, total = await CategoryService.list_categories_flat(
            session=session,
            tenant_id=tenant_id,
            board_id=board_id,
            skip=skip,
            limit=limit,
        )

        data = [CategoryResponse.model_validate(cat) for cat in categories]

        return CategoryFlatResponse(
            success=True,
            data=data,
            total=total,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리 목록 조회 실패: {str(e)}",
        )


@router.get(
    "/{category_id}",
    response_model=CategoryDetailResponse,
    summary="카테고리 상세 조회",
    responses={
        200: {"description": "성공"},
        404: {"description": "카테고리를 찾을 수 없음"},
    },
)
async def get_category(
    category_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
) -> CategoryDetailResponse:
    """
    특정 카테고리의 상세 정보를 조회합니다.

    - **category_id**: 카테고리 ID
    """
    try:
        category = await CategoryService.get_category_by_id(
            session=session,
            category_id=category_id,
            tenant_id=tenant_id,
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다.",
            )

        data = CategoryResponse.model_validate(category)

        return CategoryDetailResponse(
            success=True,
            data=data,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리 조회 실패: {str(e)}",
        )


# ============================================================
# 생성 API
# ============================================================
@router.post(
    "",
    response_model=CategoryDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="카테고리 생성",
    responses={
        201: {"description": "생성됨"},
        400: {"description": "요청이 올바르지 않음"},
        401: {"description": "인증 필요"},
        409: {"description": "이미 존재하는 카테고리 코드"},
    },
)
async def create_category(
    request: CategoryCreate,
    tenant_id: int = Depends(get_current_tenant_id),
    user_id: str = Depends(_check_admin_permission),
    session: AsyncSession = Depends(get_session),
) -> CategoryDetailResponse:
    """
    새 카테고리를 생성합니다.

    - **board_id**: 게시판 ID (필수)
    - **category_name**: 카테고리명 (필수)
    - **category_code**: 카테고리 코드 (필수, 영문/숫자/언더스코어)
    - **parent_id**: 상위 카테고리 ID (선택)
    - **description**: 설명 (선택)

    권한: Admin만 가능
    """
    try:
        # 권한 확인 (TODO: 게시판별 관리자 권한 확인)
        category = await CategoryService.create_category(
            session=session,
            tenant_id=tenant_id,
            board_id=request.board_id,
            category_name=request.category_name,
            category_code=request.category_code,
            parent_id=request.parent_id,
            description=request.description,
            sort_order=request.sort_order,
            icon=request.icon,
            color=request.color,
            read_permission=request.read_permission,
            write_permission=request.write_permission,
            created_by=user_id,
        )

        data = CategoryResponse.model_validate(category)

        return CategoryDetailResponse(
            success=True,
            data=data,
        )
    except ValueError as e:
        if "이미 존재" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리 생성 실패: {str(e)}",
        )


# ============================================================
# 수정 API
# ============================================================
@router.put(
    "/{category_id}",
    response_model=CategoryDetailResponse,
    summary="카테고리 수정",
    responses={
        200: {"description": "성공"},
        400: {"description": "요청이 올바르지 않음"},
        401: {"description": "인증 필요"},
        404: {"description": "카테고리를 찾을 수 없음"},
    },
)
async def update_category(
    category_id: int,
    request: CategoryUpdate,
    tenant_id: int = Depends(get_current_tenant_id),
    user_id: str = Depends(_check_admin_permission),
    session: AsyncSession = Depends(get_session),
) -> CategoryDetailResponse:
    """
    기존 카테고리를 수정합니다.

    - **category_id**: 카테고리 ID
    - **category_name**: 카테고리명 (선택)
    - **description**: 설명 (선택)
    - **is_active**: 활성 여부 (선택)

    권한: Admin만 가능

    주의: 카테고리 코드와 부모 변경은 별도의 엔드포인트에서 처리합니다.
    """
    try:
        category = await CategoryService.update_category(
            session=session,
            category_id=category_id,
            tenant_id=tenant_id,
            category_name=request.category_name,
            description=request.description,
            sort_order=request.sort_order,
            icon=request.icon,
            color=request.color,
            read_permission=request.read_permission,
            write_permission=request.write_permission,
            is_active=request.is_active,
            updated_by=user_id,
        )

        data = CategoryResponse.model_validate(category)

        return CategoryDetailResponse(
            success=True,
            data=data,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리 수정 실패: {str(e)}",
        )


# ============================================================
# 이동 API
# ============================================================
@router.put(
    "/{category_id}/move",
    response_model=CategoryDetailResponse,
    summary="카테고리 계층 변경 (부모 변경)",
    responses={
        200: {"description": "성공"},
        400: {"description": "요청이 올바르지 않음"},
        401: {"description": "인증 필요"},
        404: {"description": "카테고리를 찾을 수 없음"},
    },
)
async def move_category(
    category_id: int,
    parent_id: Optional[int] = Query(None),
    tenant_id: int = Depends(get_current_tenant_id),
    user_id: str = Depends(_check_admin_permission),
    session: AsyncSession = Depends(get_session),
) -> CategoryDetailResponse:
    """
    카테고리의 상위 카테고리를 변경합니다.

    - **category_id**: 카테고리 ID
    - **parent_id**: 새로운 상위 카테고리 ID (NULL이면 최상위)

    권한: Admin만 가능

    주의: 하위 카테고리의 depth와 path가 자동으로 업데이트됩니다.
    """
    try:
        category = await CategoryService.move_category(
            session=session,
            category_id=category_id,
            new_parent_id=parent_id,
            tenant_id=tenant_id,
            updated_by=user_id,
        )

        data = CategoryResponse.model_validate(category)

        return CategoryDetailResponse(
            success=True,
            data=data,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리 이동 실패: {str(e)}",
        )


# ============================================================
# 순서 변경 API (드래그앤드롭)
# ============================================================
@router.put(
    "/reorder",
    response_model=SuccessMessageResponse,
    summary="카테고리 순서 변경 (드래그앤드롭)",
    responses={
        200: {"description": "성공"},
        400: {"description": "요청이 올바르지 않음"},
        401: {"description": "인증 필요"},
        404: {"description": "카테고리를 찾을 수 없음"},
    },
)
async def reorder_category(
    request: CategoryReorder,
    tenant_id: int = Depends(get_current_tenant_id),
    user_id: str = Depends(_check_admin_permission),
    session: AsyncSession = Depends(get_session),
) -> SuccessMessageResponse:
    """
    카테고리의 순서와 계층을 변경합니다. (드래그앤드롭 용도)

    - **category_id**: 카테고리 ID
    - **parent_id**: 새로운 상위 카테고리 ID (선택)
    - **sort_order**: 새로운 정렬 순서

    권한: Admin만 가능
    """
    try:
        await CategoryService.reorder_categories(
            session=session,
            category_id=request.category_id,
            new_parent_id=request.parent_id,
            new_sort_order=request.sort_order,
            tenant_id=tenant_id,
            updated_by=user_id,
        )

        return SuccessMessageResponse(
            success=True,
            message="카테고리 순서가 변경되었습니다.",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리 순서 변경 실패: {str(e)}",
        )


# ============================================================
# 삭제 API
# ============================================================
@router.delete(
    "/{category_id}",
    response_model=SuccessMessageResponse,
    summary="카테고리 삭제",
    responses={
        200: {"description": "성공"},
        400: {"description": "요청이 올바르지 않음 (하위 카테고리/게시글 존재)"},
        401: {"description": "인증 필요"},
        404: {"description": "카테고리를 찾을 수 없음"},
    },
)
async def delete_category(
    category_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    user_id: str = Depends(_check_admin_permission),
    session: AsyncSession = Depends(get_session),
) -> SuccessMessageResponse:
    """
    카테고리를 삭제합니다. (소프트 삭제)

    - **category_id**: 카테고리 ID

    권한: Admin만 가능

    주의:
    - 하위 카테고리가 있으면 삭제 불가
    - 게시글이 있으면 삭제 불가
    """
    try:
        await CategoryService.delete_category(
            session=session,
            category_id=category_id,
            tenant_id=tenant_id,
            updated_by=user_id,
        )

        return SuccessMessageResponse(
            success=True,
            message="카테고리가 삭제되었습니다.",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리 삭제 실패: {str(e)}",
        )
