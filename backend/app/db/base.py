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
)

# Import board models
from app.models.board import (
    BoardExtended,
    BoardCategory,
    BoardPost,
    BoardComment,
    BoardAttachment,
    BoardLike,
)

# Import category model
from app.models.category import Category

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
    "BoardExtended",
    "BoardCategory",
    "BoardPost",
    "BoardComment",
    "BoardAttachment",
    "BoardLike",
    "Category",
]
