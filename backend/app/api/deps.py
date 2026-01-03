"""
API Dependencies
Common dependencies for API endpoints
"""
from typing import Generator
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.shared import Tenant
from app.api.tenant_middleware import TenantContext, get_tenant_context


def get_current_tenant(
    request: Request,
    db: Session = Depends(get_db)
) -> TenantContext:
    """
    Get current tenant from request state
    Middleware must have run first to populate request.state

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        TenantContext with tenant information

    Raises:
        HTTPException: If tenant not found or invalid
    """
    try:
        tenant_context = get_tenant_context(request)
        return tenant_context
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


def get_tenant_from_header(
    x_tenant_code: str = None,
    db: Session = Depends(get_db)
) -> Tenant:
    """
    Get tenant from X-Tenant-Code header (for admin operations)

    Args:
        x_tenant_code: Tenant code from header
        db: Database session

    Returns:
        Tenant object

    Raises:
        HTTPException: If tenant not found
    """
    if not x_tenant_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-Code header is required"
        )

    tenant = db.query(Tenant).filter(
        Tenant.tenant_code == x_tenant_code,
        Tenant.is_active == True,
        Tenant.is_deleted == False
    ).first()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{x_tenant_code}' not found"
        )

    return tenant


def validate_tenant_exists(
    tenant_id: int,
    db: Session = Depends(get_db)
) -> Tenant:
    """
    Validate that a tenant exists and is active

    Args:
        tenant_id: Tenant ID
        db: Database session

    Returns:
        Tenant object

    Raises:
        HTTPException: If tenant not found or inactive
    """
    tenant = db.query(Tenant).filter(
        Tenant.id == tenant_id,
        Tenant.is_active == True,
        Tenant.is_deleted == False
    ).first()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found or is inactive"
        )

    return tenant
