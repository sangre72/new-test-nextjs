"""
Initial seed data for shared schema
This script creates default tenants, users, roles, and permissions
"""
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.shared import (
    Tenant, User, UserGroup, UserGroupMember, Role, UserRole,
    Permission, RolePermission, TenantStatusEnum, UserStatusEnum,
    UserGroupTypeEnum, RoleTypeEnum, PermissionResourceEnum, PermissionActionEnum
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_tenants(db: Session) -> Tenant:
    """Create default tenant"""
    default_tenant = db.query(Tenant).filter(
        Tenant.tenant_code == "default"
    ).first()

    if not default_tenant:
        default_tenant = Tenant(
            tenant_code="default",
            tenant_name="Default Tenant",
            description="Default tenant for single-site deployment",
            domain="localhost",
            subdomain="localhost",
            admin_email="admin@localhost.com",
            admin_name="System Admin",
            status=TenantStatusEnum.ACTIVE,
            settings={
                "theme": "light",
                "language": "en",
                "timezone": "UTC"
            },
            created_by="system"
        )
        db.add(default_tenant)
        db.commit()
        db.refresh(default_tenant)

    return default_tenant


def seed_user_groups(db: Session, tenant: Tenant) -> None:
    """Create default user groups"""
    groups_data = [
        {
            "group_name": "All Members",
            "group_code": "all_members",
            "description": "All users in the system",
            "priority": 0,
            "group_type": UserGroupTypeEnum.SYSTEM
        },
        {
            "group_name": "Regular Users",
            "group_code": "regular_users",
            "description": "Regular users with standard permissions",
            "priority": 10,
            "group_type": UserGroupTypeEnum.SYSTEM
        },
        {
            "group_name": "VIP Users",
            "group_code": "vip_users",
            "description": "VIP users with extended permissions",
            "priority": 50,
            "group_type": UserGroupTypeEnum.SYSTEM
        },
        {
            "group_name": "Premium Users",
            "group_code": "premium_users",
            "description": "Premium users with all permissions",
            "priority": 80,
            "group_type": UserGroupTypeEnum.SYSTEM
        }
    ]

    for group_data in groups_data:
        existing = db.query(UserGroup).filter(
            UserGroup.tenant_id == tenant.id,
            UserGroup.group_code == group_data["group_code"]
        ).first()

        if not existing:
            group = UserGroup(
                tenant_id=tenant.id,
                **group_data,
                created_by="system"
            )
            db.add(group)

    db.commit()


def seed_permissions(db: Session) -> dict:
    """Create default permissions"""
    permissions_data = [
        # Tenant permissions
        {"permission_name": "Create Tenant", "permission_code": "tenant_create", "resource": PermissionResourceEnum.TENANT, "action": PermissionActionEnum.CREATE},
        {"permission_name": "Read Tenant", "permission_code": "tenant_read", "resource": PermissionResourceEnum.TENANT, "action": PermissionActionEnum.READ},
        {"permission_name": "Update Tenant", "permission_code": "tenant_update", "resource": PermissionResourceEnum.TENANT, "action": PermissionActionEnum.UPDATE},
        {"permission_name": "Delete Tenant", "permission_code": "tenant_delete", "resource": PermissionResourceEnum.TENANT, "action": PermissionActionEnum.DELETE},
        {"permission_name": "Manage Tenant", "permission_code": "tenant_manage", "resource": PermissionResourceEnum.TENANT, "action": PermissionActionEnum.MANAGE},

        # User permissions
        {"permission_name": "Create User", "permission_code": "user_create", "resource": PermissionResourceEnum.USER, "action": PermissionActionEnum.CREATE},
        {"permission_name": "Read User", "permission_code": "user_read", "resource": PermissionResourceEnum.USER, "action": PermissionActionEnum.READ},
        {"permission_name": "Update User", "permission_code": "user_update", "resource": PermissionResourceEnum.USER, "action": PermissionActionEnum.UPDATE},
        {"permission_name": "Delete User", "permission_code": "user_delete", "resource": PermissionResourceEnum.USER, "action": PermissionActionEnum.DELETE},
        {"permission_name": "Manage User", "permission_code": "user_manage", "resource": PermissionResourceEnum.USER, "action": PermissionActionEnum.MANAGE},

        # Menu permissions
        {"permission_name": "Create Menu", "permission_code": "menu_create", "resource": PermissionResourceEnum.MENU, "action": PermissionActionEnum.CREATE},
        {"permission_name": "Read Menu", "permission_code": "menu_read", "resource": PermissionResourceEnum.MENU, "action": PermissionActionEnum.READ},
        {"permission_name": "Update Menu", "permission_code": "menu_update", "resource": PermissionResourceEnum.MENU, "action": PermissionActionEnum.UPDATE},
        {"permission_name": "Delete Menu", "permission_code": "menu_delete", "resource": PermissionResourceEnum.MENU, "action": PermissionActionEnum.DELETE},
        {"permission_name": "Manage Menu", "permission_code": "menu_manage", "resource": PermissionResourceEnum.MENU, "action": PermissionActionEnum.MANAGE},

        # Board permissions
        {"permission_name": "Create Board", "permission_code": "board_create", "resource": PermissionResourceEnum.BOARD, "action": PermissionActionEnum.CREATE},
        {"permission_name": "Read Board", "permission_code": "board_read", "resource": PermissionResourceEnum.BOARD, "action": PermissionActionEnum.READ},
        {"permission_name": "Update Board", "permission_code": "board_update", "resource": PermissionResourceEnum.BOARD, "action": PermissionActionEnum.UPDATE},
        {"permission_name": "Delete Board", "permission_code": "board_delete", "resource": PermissionResourceEnum.BOARD, "action": PermissionActionEnum.DELETE},
        {"permission_name": "Manage Board", "permission_code": "board_manage", "resource": PermissionResourceEnum.BOARD, "action": PermissionActionEnum.MANAGE},

        # Role permissions
        {"permission_name": "Create Role", "permission_code": "role_create", "resource": PermissionResourceEnum.ROLE, "action": PermissionActionEnum.CREATE},
        {"permission_name": "Read Role", "permission_code": "role_read", "resource": PermissionResourceEnum.ROLE, "action": PermissionActionEnum.READ},
        {"permission_name": "Update Role", "permission_code": "role_update", "resource": PermissionResourceEnum.ROLE, "action": PermissionActionEnum.UPDATE},
        {"permission_name": "Delete Role", "permission_code": "role_delete", "resource": PermissionResourceEnum.ROLE, "action": PermissionActionEnum.DELETE},
        {"permission_name": "Manage Role", "permission_code": "role_manage", "resource": PermissionResourceEnum.ROLE, "action": PermissionActionEnum.MANAGE},
    ]

    permissions = {}
    for perm_data in permissions_data:
        existing = db.query(Permission).filter(
            Permission.permission_code == perm_data["permission_code"]
        ).first()

        if not existing:
            perm = Permission(
                **perm_data,
                created_by="system"
            )
            db.add(perm)
            db.flush()
            permissions[perm_data["permission_code"]] = perm
        else:
            permissions[perm_data["permission_code"]] = existing

    db.commit()
    return permissions


def seed_roles(db: Session, permissions: dict) -> dict:
    """Create default roles"""
    roles_data = [
        {
            "role_name": "Super Admin",
            "role_code": "super_admin",
            "description": "Full system access",
            "priority": 100,
            "role_type": RoleTypeEnum.ADMIN,
            "permissions": [
                "tenant_create", "tenant_read", "tenant_update", "tenant_delete", "tenant_manage",
                "user_create", "user_read", "user_update", "user_delete", "user_manage",
                "menu_create", "menu_read", "menu_update", "menu_delete", "menu_manage",
                "board_create", "board_read", "board_update", "board_delete", "board_manage",
                "role_create", "role_read", "role_update", "role_delete", "role_manage",
            ]
        },
        {
            "role_name": "Admin",
            "role_code": "admin",
            "description": "Administrative access",
            "priority": 50,
            "role_type": RoleTypeEnum.ADMIN,
            "permissions": [
                "user_read", "user_update",
                "menu_create", "menu_read", "menu_update", "menu_delete",
                "board_create", "board_read", "board_update", "board_delete",
            ]
        },
        {
            "role_name": "Manager",
            "role_code": "manager",
            "description": "Manager access",
            "priority": 30,
            "role_type": RoleTypeEnum.ADMIN,
            "permissions": [
                "user_read",
                "menu_read",
                "board_read", "board_update",
            ]
        },
        {
            "role_name": "Editor",
            "role_code": "editor",
            "description": "Editor access",
            "priority": 20,
            "role_type": RoleTypeEnum.BOTH,
            "permissions": [
                "menu_read",
                "board_read", "board_update",
            ]
        },
        {
            "role_name": "Viewer",
            "role_code": "viewer",
            "description": "View-only access",
            "priority": 10,
            "role_type": RoleTypeEnum.BOTH,
            "permissions": [
                "menu_read",
                "board_read",
            ]
        }
    ]

    roles = {}
    for role_data in roles_data:
        perm_codes = role_data.pop("permissions")

        existing = db.query(Role).filter(
            Role.role_code == role_data["role_code"]
        ).first()

        if not existing:
            role = Role(**role_data, created_by="system")
            db.add(role)
            db.flush()
            roles[role_data["role_code"]] = role
        else:
            role = existing
            roles[role_data["role_code"]] = role

        # Add permissions
        for perm_code in perm_codes:
            if perm_code in permissions:
                existing_perm = db.query(RolePermission).filter(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permissions[perm_code].id
                ).first()

                if not existing_perm:
                    role_perm = RolePermission(
                        role_id=role.id,
                        permission_id=permissions[perm_code].id,
                        created_by="system"
                    )
                    db.add(role_perm)

    db.commit()
    return roles


def seed_users(db: Session, tenant: Tenant, roles: dict) -> None:
    """Create default users"""
    users_data = [
        {
            "username": "superadmin",
            "email": "superadmin@localhost.com",
            "full_name": "Super Administrator",
            "password": "superadmin123",
            "is_superuser": True,
            "status": UserStatusEnum.ACTIVE,
            "is_email_verified": True,
            "role_code": "super_admin"
        },
        {
            "username": "admin",
            "email": "admin@localhost.com",
            "full_name": "Administrator",
            "password": "admin123",
            "is_superuser": False,
            "status": UserStatusEnum.ACTIVE,
            "is_email_verified": True,
            "role_code": "admin"
        },
        {
            "username": "manager",
            "email": "manager@localhost.com",
            "full_name": "Manager",
            "password": "manager123",
            "is_superuser": False,
            "status": UserStatusEnum.ACTIVE,
            "is_email_verified": True,
            "role_code": "manager"
        },
        {
            "username": "editor",
            "email": "editor@localhost.com",
            "full_name": "Editor",
            "password": "editor123",
            "is_superuser": False,
            "status": UserStatusEnum.ACTIVE,
            "is_email_verified": True,
            "role_code": "editor"
        },
        {
            "username": "viewer",
            "email": "viewer@localhost.com",
            "full_name": "Viewer",
            "password": "viewer123",
            "is_superuser": False,
            "status": UserStatusEnum.ACTIVE,
            "is_email_verified": True,
            "role_code": "viewer"
        }
    ]

    for user_data in users_data:
        role_code = user_data.pop("role_code")
        password = user_data.pop("password")

        existing = db.query(User).filter(
            User.tenant_id == tenant.id,
            User.username == user_data["username"]
        ).first()

        if not existing:
            user = User(
                tenant_id=tenant.id,
                **user_data,
                hashed_password=pwd_context.hash(password),
                created_by="system"
            )
            db.add(user)
            db.flush()

            # Assign role
            if role_code in roles:
                user_role = UserRole(
                    user_id=user.id,
                    role_id=roles[role_code].id,
                    created_by="system"
                )
                db.add(user_role)

    db.commit()


def init_db(db: Session) -> None:
    """Initialize database with seed data"""
    try:
        # Create default tenant
        tenant = seed_tenants(db)

        # Create user groups
        seed_user_groups(db, tenant)

        # Create permissions
        permissions = seed_permissions(db)

        # Create roles with permissions
        roles = seed_roles(db, permissions)

        # Create users with roles
        seed_users(db, tenant, roles)

        print("Database seed data created successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {str(e)}")
        raise
