"""
테넌트 미들웨어 (Tenant Detection Middleware)

요청에서 테넌트를 식별하고 request 객체에 테넌트 정보를 추가합니다.

테넌트 식별 우선순위:
1. X-Tenant-ID 헤더 (API, 슈퍼 관리자용)
2. 서브도메인 (siteA.example.com)
3. 커스텀 도메인 (siteA.com)
4. 세션 정보
5. 기본값 (default)

사용 예시:
```python
from fastapi import Request

async def get_items(request: Request):
    tenant = request.state.tenant
    tenant_id = request.state.tenant_id
    tenant_code = request.state.tenant_code
```
"""

import logging
from typing import Optional
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.services.shared import TenantService

logger = logging.getLogger(__name__)


class TenantDetectionMiddleware:
    """테넌트 감지 미들웨어"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next):
        """미들웨어 실행"""
        # 테넌트 감지
        async with AsyncSessionLocal() as session:
            tenant_code = await self._detect_tenant(request, session)
            tenant = await TenantService.get_tenant_by_code(session, tenant_code)

        if tenant:
            request.state.tenant = tenant
            request.state.tenant_id = tenant.id
            request.state.tenant_code = tenant.tenant_code
            request.state.tenant_settings = tenant.settings or {}
        else:
            logger.warning(f"테넌트를 찾을 수 없음: {tenant_code}")
            request.state.tenant = None
            request.state.tenant_id = None
            request.state.tenant_code = None
            request.state.tenant_settings = {}

        response = await call_next(request)
        return response

    async def _detect_tenant(self, request: Request, session: AsyncSession) -> str:
        """테넌트 코드 감지"""
        # 1. X-Tenant-ID 헤더
        tenant_code = request.headers.get("x-tenant-id")
        if tenant_code:
            logger.debug(f"헤더에서 테넌트 감지: {tenant_code}")
            return tenant_code

        # 2. 세션에서 감지
        if hasattr(request.state, "tenant_code"):
            tenant_code = request.state.tenant_code
            if tenant_code:
                logger.debug(f"세션에서 테넌트 감지: {tenant_code}")
                return tenant_code

        # 3. 도메인/서브도메인으로 감지
        hostname = request.url.hostname or request.headers.get("host", "")
        tenant_code = await self._detect_by_domain(hostname, session)
        if tenant_code:
            logger.debug(f"도메인에서 테넌트 감지: {tenant_code} (host: {hostname})")
            return tenant_code

        # 4. 기본값
        logger.debug(f"기본 테넌트 사용: default")
        return "default"

    async def _detect_by_domain(
        self, hostname: str, session: AsyncSession
    ) -> Optional[str]:
        """도메인으로 테넌트 감지"""
        if not hostname:
            return None

        # 포트 제거
        hostname = hostname.split(":")[0]

        # 1. 서브도메인 확인 (siteA.example.com)
        parts = hostname.split(".")
        if len(parts) >= 3:
            subdomain = parts[0]
            tenant = await TenantService.get_tenant_by_domain(session, subdomain)
            if tenant:
                return tenant.tenant_code

        # 2. 전체 도메인 확인 (siteA.com)
        tenant = await TenantService.get_tenant_by_domain(session, hostname)
        if tenant:
            return tenant.tenant_code

        return None


def get_current_tenant_code(request: Request) -> str:
    """현재 테넌트 코드 획득"""
    return getattr(request.state, "tenant_code", "default")


def get_current_tenant_id(request: Request) -> Optional[int]:
    """현재 테넌트 ID 획득"""
    return getattr(request.state, "tenant_id", None)


def get_current_tenant_settings(request: Request) -> dict:
    """현재 테넌트 설정 획득"""
    return getattr(request.state, "tenant_settings", {})
