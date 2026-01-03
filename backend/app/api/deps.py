"""
API Dependencies
Common dependencies for API endpoints
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from app.db.session import get_db
from app.models.shared import Tenant, User
from app.api.tenant_middleware import TenantContext, get_tenant_context
from app.core.security import decode_token, validate_token_type

# HTTP Bearer token scheme for JWT authentication
security = HTTPBearer(auto_error=False)


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


# ============================================================================
# Authentication Dependencies
# ============================================================================

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        Current authenticated User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Decode JWT token
        payload = decode_token(token)

        # Validate token type
        if not validate_token_type(payload, "access"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract user ID from token
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    user = db.query(User).filter(
        User.id == user_id,
        User.is_active == True,
        User.is_deleted == False
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Additional status checks
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.status}"
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (additional validation layer)

    Args:
        current_user: Current user from get_current_user

    Returns:
        Current active User object

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active or current_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current superuser (admin only)

    Args:
        current_user: Current user from get_current_user

    Returns:
        Current superuser User object

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Superuser access required."
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise (for optional auth endpoints)

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        Current User object if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = decode_token(token)

        if not validate_token_type(payload, "access"):
            return None

        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            return None

        user = db.query(User).filter(
            User.id == user_id,
            User.is_active == True,
            User.is_deleted == False,
            User.status == "active"
        ).first()

        return user

    except (JWTError, Exception):
        return None
