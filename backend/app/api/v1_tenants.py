"""
테넌트 API 엔드포인트

FastAPI v0.109+ 기반
SQLAlchemy 2.0 AsyncIO 사용

엔드포인트:
- GET /api/v1/tenants - 테넌트 목록
- GET /api/v1/tenants/{tenant_id} - 테넌트 상세
- POST /api/v1/tenants - 테넌트 생성
- PUT /api/v1/tenants/{tenant_id} - 테넌트 수정
- DELETE /api/v1/tenants/{tenant_id} - 테넌트 삭제
- GET /api/v1/tenants/{tenant_id}/settings - 테넌트 설정 조회
- PATCH /api/v1/tenants/{tenant_id}/settings - 테넌트 설정 수정
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from app.api.deps import get_session, get_current_user_id
from app.schemas.shared import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantSettings,
    ListResponse,
    SuccessResponse,
    ErrorResponse,
)
from app.services.shared import TenantService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])


# ============================================================
# 입력 검증 및 보안
# ============================================================
def validate_tenant_code(tenant_code: str) -> bool:
    """테넌트 코드 검증 (영문, 숫자, 언더스코어만)"""
    import re

    if not tenant_code or len(tenant_code) < 1 or len(tenant_code) > 50:
        return False
    return bool(re.match(r"^[a-z0-9_]+$", tenant_code))


def validate_domain(domain: str) -> bool:
    """도메인 형식 검증"""
    import re

    if not domain:
        return True
    return bool(re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}$", domain))


def validate_email(email: str) -> bool:
    """이메일 검증"""
    import re

    if not email:
        return True
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email))


# ============================================================
# API 엔드포인트
# ============================================================


@router.get("", response_model=ListResponse)
async def list_tenants(
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
) -> ListResponse:
    """
    테넌트 목록 조회

    Query Parameters:
    - skip: 스킵할 개수 (기본: 0)
    - limit: 조회할 개수 (기본: 20, 최대: 100)
    - is_active: 활성 여부 (선택)

    Returns:
    - success: 성공 여부
    - data: 테넌트 목록
    - total: 전체 개수
    - page: 페이지 번호
    - page_size: 페이지 크기
    """
    try:
        tenants, total = await TenantService.list_tenants(
            session=session, skip=skip, limit=limit, is_active=is_active
        )

        data = [TenantResponse.from_attributes(t) for t in tenants]

        return ListResponse(
            success=True,
            data=data,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit,
        )
    except Exception as e:
        logger.error(f"테넌트 목록 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="테넌트 목록을 조회하는데 실패했습니다.",
        )


@router.get("/{tenant_id}", response_model=SuccessResponse)
async def get_tenant(
    tenant_id: int,
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse:
    """
    테넌트 상세 조회

    Parameters:
    - tenant_id: 테넌트 ID

    Returns:
    - success: 성공 여부
    - data: 테넌트 정보
    """
    try:
        tenant = await TenantService.get_tenant_by_id(session, tenant_id)

        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="테넌트를 찾을 수 없습니다.",
            )

        return SuccessResponse(
            success=True,
            data=TenantResponse.from_attributes(tenant).model_dump(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"테넌트 조회 실패 (ID: {tenant_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="테넌트를 조회하는데 실패했습니다.",
        )


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    request: TenantCreate,
    session: AsyncSession = Depends(get_session),
    user_id: Optional[str] = Depends(get_current_user_id),
) -> SuccessResponse:
    """
    테넌트 생성

    Body:
    - tenant_code: 테넌트 코드 (필수, 영문 소문자/숫자/언더스코어)
    - tenant_name: 테넌트 이름 (필수)
    - description: 설명 (선택)
    - domain: 커스텀 도메인 (선택)
    - subdomain: 서브도메인 (선택)
    - admin_email: 관리자 이메일 (선택)
    - admin_name: 관리자 이름 (선택)
    - settings: 테넌트 설정 (선택)

    Returns:
    - success: 성공 여부
    - data: 생성된 테넌트 정보
    """
    try:
        # 입력 검증
        if not validate_tenant_code(request.tenant_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="테넌트 코드는 영문 소문자, 숫자, 언더스코어만 사용 가능합니다.",
            )

        if request.domain and not validate_domain(request.domain):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="도메인 형식이 올바르지 않습니다.",
            )

        if request.admin_email and not validate_email(request.admin_email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이메일 형식이 올바르지 않습니다.",
            )

        # 중복 체크
        existing = await TenantService.get_tenant_by_code(session, request.tenant_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 테넌트 코드입니다.",
            )

        # settings 변환
        settings_dict = None
        if request.settings:
            settings_dict = request.settings.model_dump(exclude_none=False)

        # 테넌트 생성
        tenant = await TenantService.create_tenant(
            session=session,
            tenant_code=request.tenant_code,
            tenant_name=request.tenant_name,
            description=request.description,
            domain=request.domain,
            subdomain=request.subdomain,
            admin_email=request.admin_email,
            admin_name=request.admin_name,
            settings=settings_dict,
            created_by=user_id or "system",
        )

        return SuccessResponse(
            success=True,
            data=TenantResponse.from_attributes(tenant).model_dump(),
            message="테넌트가 생성되었습니다.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"테넌트 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="테넌트를 생성하는데 실패했습니다.",
        )


@router.put("/{tenant_id}", response_model=SuccessResponse)
async def update_tenant(
    tenant_id: int,
    request: TenantUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: Optional[str] = Depends(get_current_user_id),
) -> SuccessResponse:
    """
    테넌트 수정

    Parameters:
    - tenant_id: 테넌트 ID

    Body:
    - tenant_name: 테넌트 이름 (선택)
    - description: 설명 (선택)
    - domain: 커스텀 도메인 (선택)
    - subdomain: 서브도메인 (선택)
    - admin_email: 관리자 이메일 (선택)
    - admin_name: 관리자 이름 (선택)
    - settings: 테넌트 설정 (선택)
    - is_active: 활성 여부 (선택)

    Returns:
    - success: 성공 여부
    - data: 수정된 테넌트 정보
    """
    try:
        # 도메인 검증
        if request.domain and not validate_domain(request.domain):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="도메인 형식이 올바르지 않습니다.",
            )

        if request.admin_email and not validate_email(request.admin_email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이메일 형식이 올바르지 않습니다.",
            )

        # settings 변환
        settings_dict = None
        if request.settings:
            settings_dict = request.settings.model_dump(exclude_none=False)

        # 테넌트 수정
        tenant = await TenantService.update_tenant(
            session=session,
            tenant_id=tenant_id,
            tenant_name=request.tenant_name,
            description=request.description,
            domain=request.domain,
            subdomain=request.subdomain,
            admin_email=request.admin_email,
            admin_name=request.admin_name,
            settings=settings_dict,
            is_active=request.is_active,
            updated_by=user_id or "system",
        )

        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="테넌트를 찾을 수 없습니다.",
            )

        return SuccessResponse(
            success=True,
            data=TenantResponse.from_attributes(tenant).model_dump(),
            message="테넌트가 수정되었습니다.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"테넌트 수정 실패 (ID: {tenant_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="테넌트를 수정하는데 실패했습니다.",
        )


@router.delete("/{tenant_id}", response_model=SuccessResponse)
async def delete_tenant(
    tenant_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: Optional[str] = Depends(get_current_user_id),
) -> SuccessResponse:
    """
    테넌트 삭제 (소프트 삭제)

    Parameters:
    - tenant_id: 테넌트 ID

    Returns:
    - success: 성공 여부

    주의:
    - 기본 테넌트(default)는 삭제할 수 없습니다.
    """
    try:
        success = await TenantService.delete_tenant(
            session=session,
            tenant_id=tenant_id,
            updated_by=user_id or "system",
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="테넌트를 삭제할 수 없습니다. (기본 테넌트는 삭제 불가)",
            )

        return SuccessResponse(
            success=True,
            message="테넌트가 삭제되었습니다.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"테넌트 삭제 실패 (ID: {tenant_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="테넌트를 삭제하는데 실패했습니다.",
        )


# ============================================================
# 테넌트 설정 관련 엔드포인트
# ============================================================


@router.get("/{tenant_id}/settings", response_model=SuccessResponse)
async def get_tenant_settings(
    tenant_id: int,
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse:
    """
    테넌트 설정 조회

    Parameters:
    - tenant_id: 테넌트 ID

    Returns:
    - success: 성공 여부
    - data: 테넌트 설정
    """
    try:
        settings = await TenantService.get_tenant_settings(session, tenant_id)

        if settings is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="테넌트를 찾을 수 없습니다.",
            )

        return SuccessResponse(
            success=True,
            data=settings,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"테넌트 설정 조회 실패 (ID: {tenant_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="테넌트 설정을 조회하는데 실패했습니다.",
        )


@router.patch("/{tenant_id}/settings", response_model=SuccessResponse)
async def update_tenant_settings(
    tenant_id: int,
    request: TenantSettings,
    session: AsyncSession = Depends(get_session),
    user_id: Optional[str] = Depends(get_current_user_id),
) -> SuccessResponse:
    """
    테넌트 설정 수정 (부분 업데이트)

    Parameters:
    - tenant_id: 테넌트 ID

    Body:
    - theme: 테마 (선택)
    - logo: 로고 URL (선택)
    - favicon: 파비콘 URL (선택)
    - language: 언어 (선택)
    - timezone: 시간대 (선택)
    - primary_color: 기본 색상 (선택)
    - company_name: 회사명 (선택)
    - contact_email: 연락처 이메일 (선택)
    - contact_phone: 연락처 전화 (선택)

    Returns:
    - success: 성공 여부
    - data: 수정된 설정
    """
    try:
        # 이메일 검증
        if request.contact_email and not validate_email(request.contact_email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이메일 형식이 올바르지 않습니다.",
            )

        # 설정 변환 (None 값 제외)
        settings_dict = request.model_dump(exclude_none=True)

        # 설정 업데이트
        updated_settings = await TenantService.update_tenant_settings(
            session=session,
            tenant_id=tenant_id,
            settings=settings_dict,
            updated_by=user_id or "system",
        )

        if updated_settings is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="테넌트를 찾을 수 없습니다.",
            )

        return SuccessResponse(
            success=True,
            data=updated_settings,
            message="테넌트 설정이 수정되었습니다.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"테넌트 설정 수정 실패 (ID: {tenant_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="테넌트 설정을 수정하는데 실패했습니다.",
        )
