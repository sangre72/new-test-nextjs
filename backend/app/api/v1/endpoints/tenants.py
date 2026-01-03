"""
Advanced Tenant Management Endpoints
Admin-only endpoints for full tenant lifecycle management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.shared import (
    TenantCreate, TenantUpdate, TenantResponse, TenantDetailResponse
)
from app.services.shared import TenantService
from app.models.shared import Tenant
from app.api.deps import get_current_tenant, validate_tenant_exists
from app.api.tenant_middleware import TenantContext
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/tenants", tags=["Admin - Tenants"])


# ==================== Admin Tenant CRUD ====================

@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tenant",
    description="Create a new tenant (admin only)"
)
def create_tenant_admin(
    tenant_in: TenantCreate,
    db: Session = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant)
):
    """
    Create a new tenant

    Only accessible to super admin users

    Args:
        tenant_in: Tenant creation data
        db: Database session
        current_tenant: Current tenant context

    Returns:
        Created tenant
    """
    # TODO: Add super_admin role check
    # if current_user.role != "super_admin":
    #     raise HTTPException(status_code=403, detail="Only super admins can create tenants")

    try:
        service = TenantService(db)

        # Validate tenant_code format (alphanumeric and underscore only)
        if not _validate_tenant_code(tenant_in.tenant_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant code must contain only lowercase letters, numbers, and underscores"
            )

        # Check if tenant code already exists
        existing = service.get_by_code(tenant_in.tenant_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tenant code '{tenant_in.tenant_code}' already exists"
            )

        # Check if domain already exists
        if tenant_in.domain:
            existing_domain = service.get_by_domain(tenant_in.domain)
            if existing_domain:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Domain '{tenant_in.domain}' is already in use"
                )

        # Check if subdomain already exists
        if tenant_in.subdomain:
            existing_subdomain = service.get_by_subdomain(tenant_in.subdomain)
            if existing_subdomain:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Subdomain '{tenant_in.subdomain}' is already in use"
                )

        # Create tenant
        tenant = service.create(tenant_in)
        logger.info(f"Created tenant: {tenant.tenant_code} (id={tenant.id})")
        return tenant

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tenant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create tenant: {str(e)}"
        )


@router.get(
    "",
    response_model=List[TenantResponse],
    summary="List all tenants",
    description="Get list of all tenants (admin only)"
)
def list_tenants_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None, description="Filter by status (active, suspended, inactive)"),
    db: Session = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant)
):
    """
    List all tenants with optional filtering

    Args:
        skip: Number of records to skip
        limit: Number of records to return
        status_filter: Filter by tenant status
        db: Database session
        current_tenant: Current tenant context

    Returns:
        List of tenants
    """
    try:
        service = TenantService(db)
        query = db.query(Tenant).filter(Tenant.is_deleted == False)

        if status_filter:
            query = query.filter(Tenant.status == status_filter)

        total = query.count()
        tenants = query.offset(skip).limit(limit).all()

        # Add metadata to response
        return tenants

    except Exception as e:
        logger.error(f"Error listing tenants: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list tenants"
        )


@router.get(
    "/{tenant_id}",
    response_model=TenantDetailResponse,
    summary="Get tenant details",
    description="Get detailed information about a specific tenant"
)
def get_tenant_admin(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant)
):
    """
    Get tenant by ID with detailed information

    Args:
        tenant_id: Tenant ID
        db: Database session
        current_tenant: Current tenant context

    Returns:
        Tenant details
    """
    try:
        service = TenantService(db)
        tenant = service.get(tenant_id)

        if not tenant or tenant.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        return tenant

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tenant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tenant details"
        )


@router.get(
    "/by-code/{code}",
    response_model=TenantResponse,
    summary="Get tenant by code",
    description="Get tenant using tenant code"
)
def get_tenant_by_code_admin(
    code: str,
    db: Session = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant)
):
    """
    Get tenant by code

    Args:
        code: Tenant code
        db: Database session
        current_tenant: Current tenant context

    Returns:
        Tenant
    """
    try:
        service = TenantService(db)
        tenant = service.get_by_code(code)

        if not tenant or tenant.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant '{code}' not found"
            )

        return tenant

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tenant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tenant"
        )


@router.patch(
    "/{tenant_id}",
    response_model=TenantResponse,
    summary="Update tenant",
    description="Update tenant information"
)
def update_tenant_admin(
    tenant_id: int,
    tenant_in: TenantUpdate,
    db: Session = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant)
):
    """
    Update tenant information

    Args:
        tenant_id: Tenant ID
        tenant_in: Tenant update data
        db: Database session
        current_tenant: Current tenant context

    Returns:
        Updated tenant
    """
    try:
        service = TenantService(db)
        tenant = service.get(tenant_id)

        if not tenant or tenant.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        # Prevent default tenant deletion/suspension
        if tenant.tenant_code == "default" and tenant_in.status == "inactive":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate the default tenant"
            )

        # Check for domain conflicts
        if tenant_in.domain and tenant_in.domain != tenant.domain:
            existing = service.get_by_domain(tenant_in.domain)
            if existing and existing.id != tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Domain '{tenant_in.domain}' is already in use"
                )

        # Check for subdomain conflicts
        if tenant_in.subdomain and tenant_in.subdomain != tenant.subdomain:
            existing = service.get_by_subdomain(tenant_in.subdomain)
            if existing and existing.id != tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Subdomain '{tenant_in.subdomain}' is already in use"
                )

        # Update tenant
        updated = service.update(tenant_id, tenant_in)
        logger.info(f"Updated tenant: {updated.tenant_code} (id={tenant_id})")
        return updated

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tenant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update tenant: {str(e)}"
        )


@router.delete(
    "/{tenant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete tenant",
    description="Soft delete a tenant"
)
def delete_tenant_admin(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant)
):
    """
    Delete (soft delete) a tenant

    Args:
        tenant_id: Tenant ID
        db: Database session
        current_tenant: Current tenant context
    """
    try:
        service = TenantService(db)
        tenant = service.get(tenant_id)

        if not tenant or tenant.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        # Prevent default tenant deletion
        if tenant.tenant_code == "default":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the default tenant"
            )

        # Soft delete
        service.delete(tenant_id)
        logger.info(f"Deleted tenant: {tenant.tenant_code} (id={tenant_id})")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tenant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete tenant"
        )


# ==================== Tenant Settings Management ====================

@router.get(
    "/{tenant_id}/settings",
    response_model=dict,
    summary="Get tenant settings",
    description="Get tenant-specific settings (theme, logo, language, etc)"
)
def get_tenant_settings(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant)
):
    """
    Get tenant settings

    Args:
        tenant_id: Tenant ID
        db: Database session
        current_tenant: Current tenant context

    Returns:
        Tenant settings dictionary
    """
    try:
        service = TenantService(db)
        tenant = service.get(tenant_id)

        if not tenant or tenant.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        return {
            "tenant_id": tenant.id,
            "settings": tenant.settings or {}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tenant settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tenant settings"
        )


@router.patch(
    "/{tenant_id}/settings",
    response_model=dict,
    summary="Update tenant settings",
    description="Update tenant-specific settings"
)
def update_tenant_settings(
    tenant_id: int,
    settings: dict,
    db: Session = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant)
):
    """
    Update tenant settings

    Allowed settings keys:
    - theme: 'default', 'light', 'dark'
    - language: 'ko', 'en', 'ja', 'zh'
    - timezone: timezone string
    - primaryColor: hex color code
    - companyName: company name
    - logo: logo URL
    - favicon: favicon URL

    Args:
        tenant_id: Tenant ID
        settings: Settings object to update
        db: Database session
        current_tenant: Current tenant context

    Returns:
        Updated settings
    """
    try:
        # Validate allowed settings
        allowed_keys = {
            "theme", "language", "timezone", "primaryColor",
            "companyName", "logo", "favicon", "contactEmail", "contactPhone"
        }

        invalid_keys = set(settings.keys()) - allowed_keys
        if invalid_keys:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid settings keys: {', '.join(invalid_keys)}"
            )

        service = TenantService(db)
        tenant = service.get(tenant_id)

        if not tenant or tenant.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        # Merge with existing settings
        current_settings = tenant.settings or {}
        current_settings.update(settings)

        # Update tenant
        update_data = TenantUpdate(settings=current_settings)
        updated = service.update(tenant_id, update_data)

        logger.info(f"Updated settings for tenant: {updated.tenant_code}")
        return {
            "tenant_id": updated.id,
            "settings": updated.settings or {}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tenant settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update tenant settings: {str(e)}"
        )


# ==================== Helper Functions ====================

def _validate_tenant_code(code: str) -> bool:
    """
    Validate tenant code format
    Must be 3-50 characters, lowercase letters/numbers/underscores only

    Args:
        code: Tenant code to validate

    Returns:
        True if valid, False otherwise
    """
    import re
    pattern = r"^[a-z0-9_]{3,50}$"
    return bool(re.match(pattern, code))
