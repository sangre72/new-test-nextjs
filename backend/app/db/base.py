"""
Database base imports
Import all models here for Alembic autogenerate
"""
from app.db.session import Base

# Import all models here for Alembic to detect them
from app.models.shared import (
    Tenant,
    User,
    UserGroup,
    UserGroupMember,
    Role,
    UserRole,
    Permission,
    RolePermission,
    Menu,
    Board,
)

__all__ = [
    "Base",
    "Tenant",
    "User",
    "UserGroup",
    "UserGroupMember",
    "Role",
    "UserRole",
    "Permission",
    "RolePermission",
    "Menu",
    "Board",
]
