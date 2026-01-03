"""
Tenant Identification Middleware
Identifies and sets tenant context for each request
"""
from typing import Optional
from fastapi import Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.shared import Tenant
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class TenantContext:
    """Tenant context for request"""
    def __init__(self, tenant_id: int, tenant_code: str, tenant_name: str, settings_dict: dict):
        self.tenant_id = tenant_id
        self.tenant_code = tenant_code
        self.tenant_name = tenant_name
        self.settings = settings_dict or {}


async def identify_tenant(request: Request, db: Session) -> Optional[TenantContext]:
    """
    Identify tenant from request
    Priority: header > subdomain > path > default
    """
    tenant = None
    tenant_code = None

    try:
        # 1. Check X-Tenant-Code header (for API calls)
        tenant_code = request.headers.get("X-Tenant-Code")
        if tenant_code:
            tenant = db.query(Tenant).filter(
                Tenant.tenant_code == tenant_code,
                Tenant.is_active == True,
                Tenant.is_deleted == False
            ).first()
            if tenant:
                return TenantContext(
                    tenant_id=tenant.id,
                    tenant_code=tenant.tenant_code,
                    tenant_name=tenant.tenant_name,
                    settings_dict=tenant.settings
                )

        # 2. Check subdomain (for web requests)
        host = request.headers.get("host", "")
        if host:
            # Extract subdomain from host (e.g., "shop-a.localhost" -> "shop-a")
            parts = host.split(".")
            if len(parts) >= 2:
                subdomain = parts[0]
                # Skip if it's localhost, 127.0.0.1, or IP address
                if subdomain not in ["localhost", "127", "0"] and not subdomain.isdigit():
                    tenant = db.query(Tenant).filter(
                        Tenant.subdomain == subdomain,
                        Tenant.is_active == True,
                        Tenant.is_deleted == False
                    ).first()
                    if tenant:
                        return TenantContext(
                            tenant_id=tenant.id,
                            tenant_code=tenant.tenant_code,
                            tenant_name=tenant.tenant_name,
                            settings_dict=tenant.settings
                        )

            # 3. Check domain (custom domain)
            tenant = db.query(Tenant).filter(
                Tenant.domain == host,
                Tenant.is_active == True,
                Tenant.is_deleted == False
            ).first()
            if tenant:
                return TenantContext(
                    tenant_id=tenant.id,
                    tenant_code=tenant.tenant_code,
                    tenant_name=tenant.tenant_name,
                    settings_dict=tenant.settings
                )

        # 4. Fallback to default tenant
        default_tenant = db.query(Tenant).filter(
            Tenant.tenant_code == "default",
            Tenant.is_active == True,
            Tenant.is_deleted == False
        ).first()

        if default_tenant:
            return TenantContext(
                tenant_id=default_tenant.id,
                tenant_code=default_tenant.tenant_code,
                tenant_name=default_tenant.tenant_name,
                settings_dict=default_tenant.settings
            )

        logger.warning(f"No tenant found for host: {host}")
        return None

    except Exception as e:
        logger.error(f"Error identifying tenant: {str(e)}")
        return None


async def tenant_middleware(request: Request, call_next):
    """
    Middleware to identify and inject tenant context into request
    """
    db = next(get_db())
    try:
        tenant_context = await identify_tenant(request, db)
        if tenant_context:
            request.state.tenant_id = tenant_context.tenant_id
            request.state.tenant_code = tenant_context.tenant_code
            request.state.tenant_name = tenant_context.tenant_name
            request.state.tenant_settings = tenant_context.settings
        else:
            # If no tenant found, use default values
            request.state.tenant_id = None
            request.state.tenant_code = None
            request.state.tenant_name = None
            request.state.tenant_settings = {}

        response = await call_next(request)
        return response
    finally:
        db.close()


def get_tenant_context(request: Request) -> TenantContext:
    """
    Get tenant context from request
    Used as dependency in FastAPI endpoints
    """
    tenant_id = getattr(request.state, "tenant_id", None)
    tenant_code = getattr(request.state, "tenant_code", None)
    tenant_name = getattr(request.state, "tenant_name", None)
    tenant_settings = getattr(request.state, "tenant_settings", {})

    if tenant_id is None:
        raise ValueError("Tenant context not found in request")

    return TenantContext(
        tenant_id=tenant_id,
        tenant_code=tenant_code,
        tenant_name=tenant_name,
        settings_dict=tenant_settings
    )
