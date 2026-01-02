"""
API v1 - Shared Schema Endpoints (예시)

이 파일은 공유 테이블을 사용하는 API 엔드포인트의 예시입니다.
실제 사용 시 이를 참고하여 엔드포인트를 구현하면 됩니다.

주의: 이것은 예시일 뿐 실제 프로젝트에서는 사용하지 마세요.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_session, get_current_tenant_id
from app.models.shared import (
    Tenant,
    UserGroup,
    Role,
)
from app.schemas.shared import (
    TenantResponse,
    UserGroupResponse,
    RoleResponse,
    ListResponse,
    SuccessResponse,
)
from app.services.shared import (
    TenantService,
    UserGroupService,
    RoleService,
)

# 라우터 생성
router = APIRouter(prefix="/api/v1", tags=["shared"])


# ============================================================
# Tenant Endpoints (예시)
# ============================================================
@router.get("/tenants", response_model=ListResponse)
async def list_tenants(
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """모든 테넌트 조회"""
    tenants, total = await TenantService.list_tenants(
        session, skip=skip, limit=limit
    )
    return ListResponse(
        data=[TenantResponse.model_validate(t) for t in tenants],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
    )


@router.get("/tenants/{tenant_code}", response_model=SuccessResponse)
async def get_tenant(
    tenant_code: str,
    session: AsyncSession = Depends(get_session),
):
    """특정 테넌트 조회"""
    tenant = await TenantService.get_tenant_by_code(session, tenant_code)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="테넌트를 찾을 수 없습니다",
        )

    return SuccessResponse(data=TenantResponse.model_validate(tenant).model_dump())


# ============================================================
# UserGroup Endpoints (예시)
# ============================================================
@router.get("/groups", response_model=ListResponse)
async def list_groups(
    session: AsyncSession = Depends(get_session),
    tenant_id: int = Depends(get_current_tenant_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """테넌트의 사용자 그룹 조회"""
    groups, total = await UserGroupService.list_groups(
        session, tenant_id=tenant_id, skip=skip, limit=limit
    )

    # 각 그룹의 멤버 수 계산
    responses = []
    for group in groups:
        group_dict = UserGroupResponse.model_validate(group).model_dump()
        member_count = await UserGroupService.get_group_member_count(
            session, group.id
        )
        group_dict["member_count"] = member_count
        responses.append(group_dict)

    return ListResponse(
        data=responses,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
    )


@router.get("/users/{user_id}/groups")
async def get_user_groups(
    user_id: str,
    session: AsyncSession = Depends(get_session),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """사용자가 속한 그룹 조회"""
    groups = await UserGroupService.get_user_groups(
        session, user_id=user_id, tenant_id=tenant_id
    )

    return SuccessResponse(
        data=[UserGroupResponse.model_validate(g).model_dump() for g in groups]
    )


# ============================================================
# Role Endpoints (예시)
# ============================================================
@router.get("/roles", response_model=ListResponse)
async def list_roles(
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """모든 역할 조회"""
    roles, total = await RoleService.list_roles(
        session, skip=skip, limit=limit
    )

    return ListResponse(
        data=[RoleResponse.model_validate(r).model_dump() for r in roles],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
    )


@router.get("/users/{user_id}/roles")
async def get_user_roles(
    user_id: str,
    session: AsyncSession = Depends(get_session),
):
    """사용자가 가진 역할 조회"""
    roles = await RoleService.get_user_roles(session, user_id=user_id)

    return SuccessResponse(
        data=[RoleResponse.model_validate(r).model_dump() for r in roles]
    )


@router.get("/users/{user_id}/is-admin")
async def is_user_admin(
    user_id: str,
    session: AsyncSession = Depends(get_session),
):
    """사용자가 관리자인지 확인"""
    is_admin = await RoleService.is_user_admin(session, user_id=user_id)

    return SuccessResponse(
        data={"user_id": user_id, "is_admin": is_admin}
    )


# ============================================================
# 주의사항
# ============================================================
"""
이 파일은 공유 테이블을 사용하는 API 엔드포인트의 예시입니다.

실제 프로젝트에서는:

1. 인증 미들웨어를 추가하세요:
   from app.api.deps import get_current_user_id

   @router.post("/groups")
   async def create_group(
       ...,
       current_user: str = Depends(get_current_user_id),
   ):
       # 관리자만 생성 가능
       if not await RoleService.is_user_admin(...):
           raise HTTPException(403, "권한이 없습니다")

2. 에러 처리를 추가하세요:
   try:
       ...
   except Exception as e:
       logger.error(f"그룹 조회 실패: {e}")
       raise HTTPException(500, "서버 오류")

3. 입력값 검증을 추가하세요:
   from pydantic import validator

4. 로깅을 추가하세요:
   import logging
   logger = logging.getLogger(__name__)

5. 테스트를 작성하세요:
   pytest로 각 엔드포인트 테스트
"""
