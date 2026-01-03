"""
Database Models
"""
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
    TenantStatusEnum,
    UserStatusEnum,
    UserGroupTypeEnum,
    RoleTypeEnum,
    PermissionResourceEnum,
    PermissionActionEnum,
    MenuTypeEnum,
    MenuPermissionTypeEnum,
    MenuLinkTypeEnum,
)
from app.models.category import Category
from app.models.board import (
    BoardExtended as Board,
    BoardCategory,
    BoardPost,
    BoardComment,
    BoardAttachment,
    BoardLike,
    BoardTypeEnum,
    PermissionLevelEnum,
    PostStatusEnum,
    CommentStatusEnum,
)

__all__ = [
    # Core Models
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
    "BoardCategory",
    "BoardPost",
    "BoardComment",
    "BoardAttachment",
    "BoardLike",
    # Domain Models
    "Category",
    # Enums
    "TenantStatusEnum",
    "UserStatusEnum",
    "UserGroupTypeEnum",
    "RoleTypeEnum",
    "PermissionResourceEnum",
    "PermissionActionEnum",
    "MenuTypeEnum",
    "MenuPermissionTypeEnum",
    "MenuLinkTypeEnum",
    "BoardTypeEnum",
    "PermissionLevelEnum",
    "PostStatusEnum",
    "CommentStatusEnum",
]
