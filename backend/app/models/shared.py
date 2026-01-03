"""
Shared Database Models
Common models used across multiple domains (tenants, users, roles, permissions, etc.)
"""
from datetime import datetime
from sqlalchemy import (
    BigInteger, String, Text, DateTime, Boolean, JSON, ForeignKey,
    UniqueConstraint, Index, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from enum import Enum
from app.db.session import Base


# Enums
class TenantStatusEnum(str, Enum):
    """Tenant status enumeration"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class UserStatusEnum(str, Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class UserGroupTypeEnum(str, Enum):
    """User group type enumeration"""
    SYSTEM = "system"
    CUSTOM = "custom"


class RoleTypeEnum(str, Enum):
    """Role type enumeration"""
    ADMIN = "admin"
    USER = "user"
    BOTH = "both"


class PermissionResourceEnum(str, Enum):
    """Permission resource enumeration"""
    TENANT = "tenant"
    USER = "user"
    MENU = "menu"
    BOARD = "board"
    CATEGORY = "category"
    ROLE = "role"
    PERMISSION = "permission"


class PermissionActionEnum(str, Enum):
    """Permission action enumeration"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    MANAGE = "manage"


# Base Models
class AuditMixin:
    """Audit trail mixin for all models"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    created_by: Mapped[str] = mapped_column(String(100), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Tenant(Base, AuditMixin):
    """
    Tenant model - represents a site/organization in multi-tenant architecture
    """
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Basic Information
    tenant_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="Tenant code (subdomain, etc)"
    )
    tenant_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Tenant name (site name)"
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Domain Settings
    domain: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        comment="Custom domain (e.g., siteA.com)"
    )
    subdomain: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        comment="Subdomain (e.g., siteA)"
    )

    # Settings (JSON)
    settings: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,
        comment="Tenant-specific settings (theme, logo, language, etc)"
    )

    # Contact Information
    admin_email: Mapped[str] = mapped_column(String(255), nullable=True)
    admin_name: Mapped[str] = mapped_column(String(100), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        SQLEnum(TenantStatusEnum, values_callable=lambda x: [e.value for e in x]),
        default=TenantStatusEnum.ACTIVE,
        nullable=False
    )

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    user_groups = relationship("UserGroup", back_populates="tenant", cascade="all, delete-orphan")
    menus = relationship("Menu", back_populates="tenant", cascade="all, delete-orphan")
    boards = relationship("BoardExtended", back_populates="tenant", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_tenant_code", "tenant_code"),
        Index("idx_domain", "domain"),
        Index("idx_subdomain", "subdomain"),
        Index("idx_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, code={self.tenant_code}, name={self.tenant_name})>"


class User(Base, AuditMixin):
    """
    User model - represents a user in the system
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Tenant
    tenant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False
    )

    # Basic Information
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)

    # Authentication
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # Profile
    profile_image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        SQLEnum(UserStatusEnum, values_callable=lambda x: [e.value for e in x]),
        default=UserStatusEnum.ACTIVE,
        nullable=False
    )

    # Verification
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    user_groups = relationship(
        "UserGroup",
        secondary="user_group_members",
        back_populates="users"
    )
    roles = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users"
    )
    group_memberships = relationship(
        "UserGroupMember",
        back_populates="user",
        cascade="all, delete-orphan",
        overlaps="user_groups,users"
    )
    role_assignments = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        overlaps="roles,users"
    )

    # Indexes
    __table_args__ = (
        UniqueConstraint("tenant_id", "username", name="uk_tenant_username"),
        UniqueConstraint("tenant_id", "email", name="uk_tenant_email"),
        Index("idx_tenant_id", "tenant_id"),
        Index("idx_email", "email"),
        Index("idx_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class UserGroup(Base, AuditMixin):
    """
    User Group model - represents a group of users for permission/segment management
    """
    __tablename__ = "user_groups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Tenant (NULL for global groups)
    tenant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
        comment="NULL for system-wide groups"
    )

    # Basic Information
    group_name: Mapped[str] = mapped_column(String(100), nullable=False)
    group_code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Group Settings
    priority: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        comment="Higher priority means higher precedence"
    )
    group_type: Mapped[str] = mapped_column(
        SQLEnum(UserGroupTypeEnum, values_callable=lambda x: [e.value for e in x]),
        default=UserGroupTypeEnum.CUSTOM,
        comment="system: built-in (immutable), custom: admin-created"
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="user_groups")
    users = relationship(
        "User",
        secondary="user_group_members",
        back_populates="user_groups",
        overlaps="group_memberships"
    )
    members = relationship(
        "UserGroupMember",
        back_populates="group",
        cascade="all, delete-orphan",
        overlaps="user_groups,users"
    )

    # Indexes
    __table_args__ = (
        UniqueConstraint("tenant_id", "group_code", name="uk_tenant_group_code"),
        Index("idx_tenant_id", "tenant_id"),
        Index("idx_group_code", "group_code"),
        Index("idx_priority", "priority"),
    )

    def __repr__(self) -> str:
        return f"<UserGroup(id={self.id}, code={self.group_code}, name={self.group_name})>"


class UserGroupMember(Base):
    """
    User-Group membership mapping
    """
    __tablename__ = "user_group_members"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    group_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user_groups.id", ondelete="CASCADE"),
        nullable=False
    )

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    created_by: Mapped[str] = mapped_column(String(100), nullable=True)

    # Relationships
    user = relationship("User", back_populates="group_memberships", overlaps="user_groups,users")
    group = relationship("UserGroup", back_populates="members", overlaps="user_groups,users")

    # Indexes
    __table_args__ = (
        UniqueConstraint("user_id", "group_id", name="uk_user_group"),
        Index("idx_user_id", "user_id"),
        Index("idx_group_id", "group_id"),
    )

    def __repr__(self) -> str:
        return f"<UserGroupMember(user_id={self.user_id}, group_id={self.group_id})>"


class Role(Base, AuditMixin):
    """
    Role model - represents a role in the system
    """
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Basic Information
    role_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Role Settings
    priority: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        comment="Higher priority means higher authority"
    )
    role_type: Mapped[str] = mapped_column(
        SQLEnum(RoleTypeEnum, values_callable=lambda x: [e.value for e in x]),
        default=RoleTypeEnum.BOTH,
        comment="admin: admin-only, user: user-only, both: both"
    )

    # Relationships
    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        overlaps="role_assignments"
    )
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        overlaps="role_permissions"
    )
    role_assignments = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
        overlaps="roles,users"
    )
    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        overlaps="permissions,roles"
    )

    # Indexes
    __table_args__ = (
        Index("idx_role_code", "role_code"),
        Index("idx_priority", "priority"),
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, code={self.role_code}, name={self.role_name})>"


class UserRole(Base):
    """
    User-Role assignment mapping
    """
    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False
    )

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    created_by: Mapped[str] = mapped_column(String(100), nullable=True)

    # Relationships
    user = relationship("User", back_populates="role_assignments", overlaps="roles,users")
    role = relationship("Role", back_populates="role_assignments", overlaps="roles,users")

    # Indexes
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uk_user_role"),
        Index("idx_user_id", "user_id"),
        Index("idx_role_id", "role_id"),
    )

    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


class Permission(Base, AuditMixin):
    """
    Permission model - represents a permission in the system
    """
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Basic Information
    permission_name: Mapped[str] = mapped_column(String(100), nullable=False)
    permission_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Permission Details
    resource: Mapped[str] = mapped_column(
        SQLEnum(PermissionResourceEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        comment="Resource this permission applies to"
    )
    action: Mapped[str] = mapped_column(
        SQLEnum(PermissionActionEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        comment="Action allowed on the resource"
    )

    # Relationships
    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        overlaps="role_permissions"
    )
    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
        overlaps="permissions,roles"
    )

    # Indexes
    __table_args__ = (
        Index("idx_permission_code", "permission_code"),
        Index("idx_resource_action", "resource", "action"),
    )

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, code={self.permission_code})>"


class RolePermission(Base):
    """
    Role-Permission assignment mapping
    """
    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign Keys
    role_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False
    )
    permission_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False
    )

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    created_by: Mapped[str] = mapped_column(String(100), nullable=True)

    # Relationships
    role = relationship("Role", back_populates="role_permissions", overlaps="permissions,roles")
    permission = relationship("Permission", back_populates="role_permissions", overlaps="permissions,roles")

    # Indexes
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uk_role_permission"),
        Index("idx_role_id", "role_id"),
        Index("idx_permission_id", "permission_id"),
    )

    def __repr__(self) -> str:
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"


class MenuTypeEnum(str, Enum):
    """Menu type enumeration"""
    USER = "user"
    SITE = "site"
    ADMIN = "admin"


class MenuPermissionTypeEnum(str, Enum):
    """Menu permission type enumeration"""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    ROLE_BASED = "role_based"
    PERMISSION_BASED = "permission_based"


class MenuLinkTypeEnum(str, Enum):
    """Menu link type enumeration"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    NEW_TAB = "new_tab"
    MODAL = "modal"
    NONE = "none"


# Placeholder models for domain-specific features
class Menu(Base, AuditMixin):
    """
    Menu model - hierarchical menu management with role-based access control
    Supports multi-level tree structure with parent-child relationships
    """
    __tablename__ = "menus"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Tenant
    tenant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        comment="Tenant ID for multi-tenancy"
    )

    # Basic Information
    menu_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Menu display name"
    )
    menu_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Unique menu code within tenant"
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Menu Type
    menu_type: Mapped[str] = mapped_column(
        SQLEnum(MenuTypeEnum, values_callable=lambda x: [e.value for e in x]),
        default=MenuTypeEnum.USER,
        nullable=False,
        comment="Menu type: user, site, admin"
    )

    # URL and Icon
    menu_url: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        comment="Menu URL or route path"
    )
    menu_icon: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="Icon class or name (e.g., fa-home)"
    )

    # Link Behavior
    link_type: Mapped[str] = mapped_column(
        SQLEnum(MenuLinkTypeEnum, values_callable=lambda x: [e.value for e in x]),
        default=MenuLinkTypeEnum.INTERNAL,
        nullable=False,
        comment="How the link should be opened"
    )

    # Hierarchy
    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("menus.id", ondelete="CASCADE"),
        nullable=True,
        comment="Parent menu ID for hierarchical structure"
    )
    depth: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
        comment="Depth level in hierarchy (0=root)"
    )
    path: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        comment="Materialized path (e.g., /1/3/5)"
    )

    # Display Order
    display_order: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
        comment="Display order within same parent"
    )

    # Permission Settings
    permission_type: Mapped[str] = mapped_column(
        SQLEnum(MenuPermissionTypeEnum, values_callable=lambda x: [e.value for e in x]),
        default=MenuPermissionTypeEnum.PUBLIC,
        nullable=False,
        comment="Permission requirement type"
    )

    # Visibility
    is_visible: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether menu is visible"
    )

    # Metadata (JSON)
    menu_metadata: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional metadata (badge, tooltip, etc.)"
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="menus")
    parent = relationship(
        "Menu",
        remote_side=[id],
        backref="children"
    )

    # Indexes
    __table_args__ = (
        UniqueConstraint("tenant_id", "menu_code", name="uk_tenant_menu_code"),
        Index("idx_tenant_id", "tenant_id"),
        Index("idx_menu_code", "menu_code"),
        Index("idx_menu_type", "menu_type"),
        Index("idx_parent_id", "parent_id"),
        Index("idx_display_order", "display_order"),
        Index("idx_tenant_type_parent", "tenant_id", "menu_type", "parent_id"),
    )

    def __repr__(self) -> str:
        return f"<Menu(id={self.id}, code={self.menu_code}, name={self.menu_name})>"


# Board model moved to app.models.board (BoardExtended)
