"""
API Dependencies
Common dependencies for API endpoints
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db


def get_current_tenant(
    tenant_id: str = None,
    db: Session = Depends(get_db)
) -> str:
    """
    Get current tenant from header or subdomain

    Args:
        tenant_id: Tenant identifier from header
        db: Database session

    Returns:
        Tenant identifier

    Raises:
        HTTPException: If tenant not found or invalid
    """
    if not tenant_id:
        # Default tenant
        return "public"

    # TODO: Validate tenant exists in database
    # tenant = db.query(Tenant).filter(Tenant.identifier == tenant_id).first()
    # if not tenant:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Tenant not found"
    #     )

    return tenant_id


# Example: Current user dependency
# def get_current_user(
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2_scheme)
# ) -> User:
#     """Get current authenticated user"""
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
#
#     user = db.query(User).filter(User.id == user_id).first()
#     if user is None:
#         raise credentials_exception
#     return user
