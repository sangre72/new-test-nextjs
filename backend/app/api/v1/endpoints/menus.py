"""
Menu API Endpoints - 메뉴 관리 API

사용자용 메뉴 조회 및 관리자용 메뉴 CRUD API
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session, get_current_user_id
from app.models.menu import MenuTypeEnum
from app.services.menu import MenuService
from app.schemas.menu import (
    MenuCreateRequest,
    MenuUpdateRequest,
    MenuMoveRequest,
    MenuReorderRequest,
    MenuResponse,
    MenuListResponse,
    MenuTreeResponse,
    MenuSuccessResponse,
    MenuListSuccessResponse,
    MenuTreeSuccessResponse,
    MenuErrorResponse,
)

router = APIRouter()


# ============================================================
# 에러 헬퍼
# ============================================================
def error_response(error_code: str, message: str, status_code: int = 400):
    """에러 응답 생성"""
    return HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "error_code": error_code,
            "message": message,
        },
    )


# ============================================================
# 사용자용 메뉴 조회 API
# ============================================================
@router.get(
    "/menus/type/{menu_type}",
    response_model=MenuTreeSuccessResponse,
    summary="메뉴 타입별 트리 조회",
    description="사용자가 접근 가능한 메뉴를 트리 구조로 조회합니다.",
    responses={
        200: {"description": "성공"},
        400: {"model": MenuErrorResponse, "description": "잘못된 요청"},
        500: {"model": MenuErrorResponse, "description": "서버 오류"},
    },
)
async def get_menus_by_type(
    menu_type: MenuTypeEnum,
    tenant_id: Optional[int] = Query(None, description="테넌트 ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    메뉴 타입별 트리 조회

    메뉴 타입:
    - site: 사이트 메뉴 (GNB)
    - user: 마이페이지 메뉴
    - admin: 관리자 메뉴
    - header_utility: 헤더 유틸리티
    - footer_utility: 푸터 유틸리티
    - quick_menu: 퀵 메뉴
    """
    try:
        service = MenuService(session)

        # 메뉴 조회 (활성화된 메뉴만)
        menus = await service.get_menus_by_type(
            menu_type=menu_type,
            tenant_id=tenant_id,
            include_invisible=False,
            include_inactive=False,
        )

        # 트리 구조로 변환
        tree = await service.build_menu_tree(menus)

        return {
            "success": True,
            "data": {
                "total": len(menus),
                "tree": tree,
            },
        }

    except Exception as e:
        raise error_response(
            error_code="INTERNAL_ERROR",
            message=f"메뉴 조회 중 오류가 발생했습니다: {str(e)}",
            status_code=500,
        )


# ============================================================
# 관리자용 메뉴 CRUD API
# ============================================================
@router.get(
    "/admin/menus",
    response_model=MenuListSuccessResponse,
    summary="메뉴 목록 조회 (관리자)",
    description="전체 메뉴를 조회합니다. (관리자 전용)",
    responses={
        200: {"description": "성공"},
        403: {"model": MenuErrorResponse, "description": "권한 없음"},
        500: {"model": MenuErrorResponse, "description": "서버 오류"},
    },
)
async def get_all_menus(
    tenant_id: Optional[int] = Query(None, description="테넌트 ID"),
    menu_type: Optional[MenuTypeEnum] = Query(None, description="메뉴 타입"),
    session: AsyncSession = Depends(get_session),
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    """
    메뉴 목록 조회 (관리자)

    TODO: 관리자 권한 검증 추가 (auth-backend 에이전트 구현 후)
    """
    try:
        service = MenuService(session)

        # 전체 메뉴 조회
        menus = await service.get_all_menus(
            tenant_id=tenant_id,
            menu_type=menu_type,
        )

        return {
            "success": True,
            "data": {
                "total": len(menus),
                "menus": [MenuResponse.model_validate(menu) for menu in menus],
            },
        }

    except Exception as e:
        raise error_response(
            error_code="INTERNAL_ERROR",
            message=f"메뉴 조회 중 오류가 발생했습니다: {str(e)}",
            status_code=500,
        )


@router.get(
    "/admin/menus/tree",
    response_model=MenuTreeSuccessResponse,
    summary="메뉴 트리 조회 (관리자)",
    description="전체 메뉴를 트리 구조로 조회합니다. (관리자 전용)",
    responses={
        200: {"description": "성공"},
        403: {"model": MenuErrorResponse, "description": "권한 없음"},
        500: {"model": MenuErrorResponse, "description": "서버 오류"},
    },
)
async def get_menu_tree(
    tenant_id: Optional[int] = Query(None, description="테넌트 ID"),
    menu_type: Optional[MenuTypeEnum] = Query(None, description="메뉴 타입"),
    session: AsyncSession = Depends(get_session),
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    """
    메뉴 트리 조회 (관리자)

    TODO: 관리자 권한 검증 추가 (auth-backend 에이전트 구현 후)
    """
    try:
        service = MenuService(session)

        # 전체 메뉴 조회
        menus = await service.get_all_menus(
            tenant_id=tenant_id,
            menu_type=menu_type,
        )

        # 트리 구조로 변환
        tree = await service.build_menu_tree(menus)

        return {
            "success": True,
            "data": {
                "total": len(menus),
                "tree": tree,
            },
        }

    except Exception as e:
        raise error_response(
            error_code="INTERNAL_ERROR",
            message=f"메뉴 트리 조회 중 오류가 발생했습니다: {str(e)}",
            status_code=500,
        )


@router.get(
    "/admin/menus/{menu_id}",
    response_model=MenuSuccessResponse,
    summary="메뉴 상세 조회 (관리자)",
    description="특정 메뉴를 조회합니다. (관리자 전용)",
    responses={
        200: {"description": "성공"},
        404: {"model": MenuErrorResponse, "description": "메뉴 없음"},
        500: {"model": MenuErrorResponse, "description": "서버 오류"},
    },
)
async def get_menu_by_id(
    menu_id: int,
    session: AsyncSession = Depends(get_session),
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    """
    메뉴 상세 조회 (관리자)

    TODO: 관리자 권한 검증 추가 (auth-backend 에이전트 구현 후)
    """
    try:
        service = MenuService(session)

        menu = await service.get_menu_by_id(menu_id)
        if not menu:
            raise error_response(
                error_code="NOT_FOUND",
                message="메뉴를 찾을 수 없습니다.",
                status_code=404,
            )

        return {
            "success": True,
            "data": MenuResponse.model_validate(menu),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise error_response(
            error_code="INTERNAL_ERROR",
            message=f"메뉴 조회 중 오류가 발생했습니다: {str(e)}",
            status_code=500,
        )


@router.post(
    "/admin/menus",
    response_model=MenuSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="메뉴 생성 (관리자)",
    description="새로운 메뉴를 생성합니다. (관리자 전용)",
    responses={
        201: {"description": "생성 성공"},
        400: {"model": MenuErrorResponse, "description": "잘못된 요청"},
        403: {"model": MenuErrorResponse, "description": "권한 없음"},
        500: {"model": MenuErrorResponse, "description": "서버 오류"},
    },
)
async def create_menu(
    request: MenuCreateRequest,
    session: AsyncSession = Depends(get_session),
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    """
    메뉴 생성 (관리자)

    TODO: 관리자 권한 검증 추가 (auth-backend 에이전트 구현 후)
    """
    try:
        service = MenuService(session)

        menu = await service.create_menu(
            request=request,
            created_by=current_user_id or "admin",
        )

        return {
            "success": True,
            "data": MenuResponse.model_validate(menu),
        }

    except ValueError as e:
        raise error_response(
            error_code="INVALID_INPUT",
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        raise error_response(
            error_code="INTERNAL_ERROR",
            message=f"메뉴 생성 중 오류가 발생했습니다: {str(e)}",
            status_code=500,
        )


@router.put(
    "/admin/menus/{menu_id}",
    response_model=MenuSuccessResponse,
    summary="메뉴 수정 (관리자)",
    description="메뉴 정보를 수정합니다. (관리자 전용)",
    responses={
        200: {"description": "수정 성공"},
        400: {"model": MenuErrorResponse, "description": "잘못된 요청"},
        404: {"model": MenuErrorResponse, "description": "메뉴 없음"},
        500: {"model": MenuErrorResponse, "description": "서버 오류"},
    },
)
async def update_menu(
    menu_id: int,
    request: MenuUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    """
    메뉴 수정 (관리자)

    TODO: 관리자 권한 검증 추가 (auth-backend 에이전트 구현 후)
    """
    try:
        service = MenuService(session)

        menu = await service.update_menu(
            menu_id=menu_id,
            request=request,
            updated_by=current_user_id or "admin",
        )

        return {
            "success": True,
            "data": MenuResponse.model_validate(menu),
        }

    except ValueError as e:
        raise error_response(
            error_code="INVALID_INPUT",
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        raise error_response(
            error_code="INTERNAL_ERROR",
            message=f"메뉴 수정 중 오류가 발생했습니다: {str(e)}",
            status_code=500,
        )


@router.delete(
    "/admin/menus/{menu_id}",
    summary="메뉴 삭제 (관리자)",
    description="메뉴를 삭제합니다. (소프트 삭제, 관리자 전용)",
    responses={
        200: {"description": "삭제 성공"},
        400: {"model": MenuErrorResponse, "description": "잘못된 요청"},
        404: {"model": MenuErrorResponse, "description": "메뉴 없음"},
        500: {"model": MenuErrorResponse, "description": "서버 오류"},
    },
)
async def delete_menu(
    menu_id: int,
    hard_delete: bool = Query(False, description="물리적 삭제 여부"),
    session: AsyncSession = Depends(get_session),
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    """
    메뉴 삭제 (관리자)

    기본적으로 소프트 삭제(is_deleted=True)를 수행합니다.
    hard_delete=true 시 물리적으로 삭제합니다.

    TODO: 관리자 권한 검증 추가 (auth-backend 에이전트 구현 후)
    """
    try:
        service = MenuService(session)

        await service.delete_menu(
            menu_id=menu_id,
            deleted_by=current_user_id or "admin",
            hard_delete=hard_delete,
        )

        return {
            "success": True,
            "message": "메뉴가 삭제되었습니다.",
        }

    except ValueError as e:
        raise error_response(
            error_code="INVALID_INPUT",
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        raise error_response(
            error_code="INTERNAL_ERROR",
            message=f"메뉴 삭제 중 오류가 발생했습니다: {str(e)}",
            status_code=500,
        )


@router.put(
    "/admin/menus/{menu_id}/move",
    response_model=MenuSuccessResponse,
    summary="메뉴 이동 (관리자)",
    description="메뉴의 부모를 변경합니다. (관리자 전용)",
    responses={
        200: {"description": "이동 성공"},
        400: {"model": MenuErrorResponse, "description": "잘못된 요청"},
        404: {"model": MenuErrorResponse, "description": "메뉴 없음"},
        500: {"model": MenuErrorResponse, "description": "서버 오류"},
    },
)
async def move_menu(
    menu_id: int,
    request: MenuMoveRequest,
    session: AsyncSession = Depends(get_session),
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    """
    메뉴 이동 (관리자)

    메뉴의 부모를 변경하여 트리 구조를 재구성합니다.
    parent_id를 null로 설정하면 최상위 메뉴로 이동합니다.

    TODO: 관리자 권한 검증 추가 (auth-backend 에이전트 구현 후)
    """
    try:
        service = MenuService(session)

        menu = await service.move_menu(
            menu_id=menu_id,
            request=request,
            updated_by=current_user_id or "admin",
        )

        return {
            "success": True,
            "data": MenuResponse.model_validate(menu),
        }

    except ValueError as e:
        raise error_response(
            error_code="INVALID_INPUT",
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        raise error_response(
            error_code="INTERNAL_ERROR",
            message=f"메뉴 이동 중 오류가 발생했습니다: {str(e)}",
            status_code=500,
        )


@router.put(
    "/admin/menus/reorder",
    summary="메뉴 순서 변경 (관리자)",
    description="메뉴 순서를 일괄 변경합니다. (관리자 전용)",
    responses={
        200: {"description": "순서 변경 성공"},
        400: {"model": MenuErrorResponse, "description": "잘못된 요청"},
        500: {"model": MenuErrorResponse, "description": "서버 오류"},
    },
)
async def reorder_menus(
    request: MenuReorderRequest,
    session: AsyncSession = Depends(get_session),
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    """
    메뉴 순서 일괄 변경 (관리자)

    menu_ids 배열의 순서대로 메뉴의 sort_order를 변경합니다.

    TODO: 관리자 권한 검증 추가 (auth-backend 에이전트 구현 후)
    """
    try:
        service = MenuService(session)

        await service.reorder_menus(
            menu_ids=request.menu_ids,
            updated_by=current_user_id or "admin",
        )

        return {
            "success": True,
            "message": "메뉴 순서가 변경되었습니다.",
        }

    except Exception as e:
        raise error_response(
            error_code="INTERNAL_ERROR",
            message=f"메뉴 순서 변경 중 오류가 발생했습니다: {str(e)}",
            status_code=500,
        )
