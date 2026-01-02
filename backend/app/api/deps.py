"""
API Dependencies

FastAPI 의존성: 데이터베이스 세션, 인증 정보, 테넌트 등

사용법:
    @app.get("/items")
    async def list_items(
        session: AsyncSession = Depends(get_session),
        tenant: Tenant = Depends(get_current_tenant),
        user_id: str = Depends(get_current_user_id),
    ):
        ...
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.shared import Tenant


async def get_session() -> AsyncSession:
    """
    데이터베이스 세션 제공자

    Usage:
        async def get_items(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user_id() -> Optional[str]:
    """
    현재 사용자 ID 제공자

    주의: 실제 구현은 auth-backend 에이전트에서 JWT 검증을 통해 구현됩니다.
    여기서는 임시로 None을 반환합니다.

    Usage:
        async def get_user_groups(user_id: str = Depends(get_current_user_id)):
            ...
    """
    # TODO: JWT 검증 구현 (auth-backend 에이전트)
    return None


async def get_current_tenant(
    session: AsyncSession = Depends(get_session),
) -> Tenant:
    """
    현재 테넌트 정보 제공자

    테넌트 식별 방식:
    1. 서브도메인 (예: siteA.example.com)
    2. 헤더 (X-Tenant-ID)
    3. 세션
    4. 기본값 (default)

    TODO: 실제 테넌트 식별 로직 구현

    Usage:
        async def get_menus(tenant: Tenant = Depends(get_current_tenant)):
            ...
    """
    # 임시: 기본 테넌트 반환
    result = await session.execute(
        select(Tenant).where(Tenant.tenant_code == "default")
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="테넌트를 찾을 수 없습니다",
        )

    return tenant


async def get_current_tenant_id(
    tenant: Tenant = Depends(get_current_tenant),
) -> int:
    """
    현재 테넌트 ID 제공자

    Usage:
        async def get_items(tenant_id: int = Depends(get_current_tenant_id)):
            ...
    """
    return tenant.id
