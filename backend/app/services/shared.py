"""
Business Logic Services for Shared Models
Handles CRUD operations and business logic
"""
from typing import Optional, List, Generic, TypeVar
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.shared import (
    Tenant, User, UserGroup, UserGroupMember, Role, UserRole,
    Permission, RolePermission, Menu, Board
)
from app.schemas.shared import (
    TenantCreate, TenantUpdate, UserCreate, UserUpdate, UserGroupCreate, UserGroupUpdate,
    RoleCreate, RoleUpdate, PermissionCreate, PermissionUpdate,
    UserGroupMemberCreate, UserRoleCreate, RolePermissionCreate
)

T = TypeVar('T')


# ==================== Base Service Class ====================

class BaseService(Generic[T]):
    """Base service for CRUD operations"""

    def __init__(self, db: Session, model: type[T]):
        self.db = db
        self.model = model

    def get(self, id: int) -> Optional[T]:
        """Get single record by id"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination"""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: dict) -> T:
        """Create new record"""
        obj = self.model(**obj_in)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: int, obj_in: dict) -> Optional[T]:
        """Update existing record"""
        obj = self.get(id)
        if not obj:
            return None
        for key, value in obj_in.items():
            if hasattr(obj, key) and value is not None:
                setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        """Soft delete record"""
        obj = self.get(id)
        if not obj:
            return False
        obj.is_deleted = True
        self.db.commit()
        return True

    def hard_delete(self, id: int) -> bool:
        """Hard delete record"""
        obj = self.get(id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True


# ==================== Tenant Service ====================

class TenantService(BaseService[Tenant]):
    """Service for tenant management"""

    def __init__(self, db: Session):
        super().__init__(db, Tenant)

    def get_by_code(self, code: str) -> Optional[Tenant]:
        """Get tenant by code"""
        return self.db.query(Tenant).filter(Tenant.tenant_code == code).first()

    def get_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain"""
        return self.db.query(Tenant).filter(Tenant.domain == domain).first()

    def get_by_subdomain(self, subdomain: str) -> Optional[Tenant]:
        """Get tenant by subdomain"""
        return self.db.query(Tenant).filter(Tenant.subdomain == subdomain).first()

    def create(self, obj_in: TenantCreate) -> Tenant:
        """Create new tenant"""
        try:
            tenant = Tenant(**obj_in.model_dump())
            self.db.add(tenant)
            self.db.commit()
            self.db.refresh(tenant)
            return tenant
        except IntegrityError:
            self.db.rollback()
            raise

    def update(self, id: int, obj_in: TenantUpdate) -> Optional[Tenant]:
        """Update tenant"""
        return super().update(id, obj_in.model_dump(exclude_unset=True))

    def get_active_tenants(self) -> List[Tenant]:
        """Get all active tenants"""
        return self.db.query(Tenant).filter(
            Tenant.is_active == True,
            Tenant.is_deleted == False
        ).all()


# ==================== User Service ====================

class UserService(BaseService[User]):
    """Service for user management"""

    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_username(self, tenant_id: int, username: str) -> Optional[User]:
        """Get user by username within tenant"""
        return self.db.query(User).filter(
            User.tenant_id == tenant_id,
            User.username == username
        ).first()

    def get_by_email(self, tenant_id: int, email: str) -> Optional[User]:
        """Get user by email within tenant"""
        return self.db.query(User).filter(
            User.tenant_id == tenant_id,
            User.email == email
        ).first()

    def get_by_tenant(self, tenant_id: int, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users in tenant"""
        return self.db.query(User).filter(User.tenant_id == tenant_id).offset(skip).limit(limit).all()

    def create(self, obj_in: UserCreate) -> User:
        """Create new user with password hashing"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        user_data = obj_in.model_dump(exclude={'password'})
        user_data['hashed_password'] = pwd_context.hash(obj_in.password)

        try:
            user = User(**user_data)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise

    def update(self, id: int, obj_in: UserUpdate) -> Optional[User]:
        """Update user"""
        return super().update(id, obj_in.model_dump(exclude_unset=True))

    def get_active_users(self, tenant_id: int) -> List[User]:
        """Get all active users in tenant"""
        return self.db.query(User).filter(
            User.tenant_id == tenant_id,
            User.is_active == True,
            User.is_deleted == False
        ).all()

    def verify_password(self, user: User, password: str) -> bool:
        """Verify user password"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(password, user.hashed_password)


# ==================== User Group Service ====================

class UserGroupService(BaseService[UserGroup]):
    """Service for user group management"""

    def __init__(self, db: Session):
        super().__init__(db, UserGroup)

    def get_by_code(self, code: str, tenant_id: Optional[int] = None) -> Optional[UserGroup]:
        """Get group by code"""
        query = self.db.query(UserGroup).filter(UserGroup.group_code == code)
        if tenant_id:
            query = query.filter(UserGroup.tenant_id == tenant_id)
        return query.first()

    def get_by_tenant(self, tenant_id: int, skip: int = 0, limit: int = 100) -> List[UserGroup]:
        """Get all groups in tenant"""
        return self.db.query(UserGroup).filter(
            UserGroup.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()

    def create(self, obj_in: UserGroupCreate) -> UserGroup:
        """Create new user group"""
        try:
            group = UserGroup(**obj_in.model_dump())
            self.db.add(group)
            self.db.commit()
            self.db.refresh(group)
            return group
        except IntegrityError:
            self.db.rollback()
            raise

    def add_user(self, group_id: int, user_id: int) -> UserGroupMember:
        """Add user to group"""
        try:
            membership = UserGroupMember(user_id=user_id, group_id=group_id)
            self.db.add(membership)
            self.db.commit()
            self.db.refresh(membership)
            return membership
        except IntegrityError:
            self.db.rollback()
            raise

    def remove_user(self, group_id: int, user_id: int) -> bool:
        """Remove user from group"""
        membership = self.db.query(UserGroupMember).filter(
            UserGroupMember.group_id == group_id,
            UserGroupMember.user_id == user_id
        ).first()
        if not membership:
            return False
        self.db.delete(membership)
        self.db.commit()
        return True

    def get_group_members(self, group_id: int) -> List[User]:
        """Get all users in group"""
        return self.db.query(User).join(
            UserGroupMember,
            User.id == UserGroupMember.user_id
        ).filter(UserGroupMember.group_id == group_id).all()

    def get_user_groups(self, user_id: int) -> List[UserGroup]:
        """Get all groups for user"""
        return self.db.query(UserGroup).join(
            UserGroupMember,
            UserGroup.id == UserGroupMember.group_id
        ).filter(UserGroupMember.user_id == user_id).all()


# ==================== Role Service ====================

class RoleService(BaseService[Role]):
    """Service for role management"""

    def __init__(self, db: Session):
        super().__init__(db, Role)

    def get_by_code(self, code: str) -> Optional[Role]:
        """Get role by code"""
        return self.db.query(Role).filter(Role.role_code == code).first()

    def create(self, obj_in: RoleCreate) -> Role:
        """Create new role"""
        try:
            role = Role(**obj_in.model_dump())
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
            return role
        except IntegrityError:
            self.db.rollback()
            raise

    def add_permission(self, role_id: int, permission_id: int) -> RolePermission:
        """Add permission to role"""
        try:
            role_perm = RolePermission(role_id=role_id, permission_id=permission_id)
            self.db.add(role_perm)
            self.db.commit()
            self.db.refresh(role_perm)
            return role_perm
        except IntegrityError:
            self.db.rollback()
            raise

    def remove_permission(self, role_id: int, permission_id: int) -> bool:
        """Remove permission from role"""
        role_perm = self.db.query(RolePermission).filter(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        ).first()
        if not role_perm:
            return False
        self.db.delete(role_perm)
        self.db.commit()
        return True

    def get_role_permissions(self, role_id: int) -> List[Permission]:
        """Get all permissions for role"""
        return self.db.query(Permission).join(
            RolePermission,
            Permission.id == RolePermission.permission_id
        ).filter(RolePermission.role_id == role_id).all()

    def get_user_roles(self, user_id: int) -> List[Role]:
        """Get all roles for user"""
        return self.db.query(Role).join(
            UserRole,
            Role.id == UserRole.role_id
        ).filter(UserRole.user_id == user_id).all()


# ==================== Permission Service ====================

class PermissionService(BaseService[Permission]):
    """Service for permission management"""

    def __init__(self, db: Session):
        super().__init__(db, Permission)

    def get_by_code(self, code: str) -> Optional[Permission]:
        """Get permission by code"""
        return self.db.query(Permission).filter(Permission.permission_code == code).first()

    def get_by_resource_action(self, resource: str, action: str) -> Optional[Permission]:
        """Get permission by resource and action"""
        return self.db.query(Permission).filter(
            Permission.resource == resource,
            Permission.action == action
        ).first()

    def create(self, obj_in: PermissionCreate) -> Permission:
        """Create new permission"""
        try:
            perm = Permission(**obj_in.model_dump())
            self.db.add(perm)
            self.db.commit()
            self.db.refresh(perm)
            return perm
        except IntegrityError:
            self.db.rollback()
            raise


# ==================== User Role Service ====================

class UserRoleService:
    """Service for user-role assignments"""

    def __init__(self, db: Session):
        self.db = db

    def assign_role(self, user_id: int, role_id: int) -> UserRole:
        """Assign role to user"""
        try:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            self.db.add(user_role)
            self.db.commit()
            self.db.refresh(user_role)
            return user_role
        except IntegrityError:
            self.db.rollback()
            raise

    def revoke_role(self, user_id: int, role_id: int) -> bool:
        """Revoke role from user"""
        user_role = self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()
        if not user_role:
            return False
        self.db.delete(user_role)
        self.db.commit()
        return True

    def has_role(self, user_id: int, role_code: str) -> bool:
        """Check if user has specific role"""
        return self.db.query(UserRole).join(
            Role, UserRole.role_id == Role.id
        ).filter(
            UserRole.user_id == user_id,
            Role.role_code == role_code
        ).first() is not None

    def has_permission(self, user_id: int, permission_code: str) -> bool:
        """Check if user has specific permission through roles"""
        return self.db.query(RolePermission).join(
            UserRole, RolePermission.role_id == UserRole.role_id
        ).join(
            Permission, RolePermission.permission_id == Permission.id
        ).filter(
            UserRole.user_id == user_id,
            Permission.permission_code == permission_code
        ).first() is not None

    def get_user_permissions(self, user_id: int) -> List[Permission]:
        """Get all permissions for user through roles"""
        return self.db.query(Permission).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).join(
            UserRole, RolePermission.role_id == UserRole.role_id
        ).filter(UserRole.user_id == user_id).distinct().all()


# ==================== Menu Service ====================

class MenuService(BaseService[Menu]):
    """Service for menu management"""

    def __init__(self, db: Session):
        super().__init__(db, Menu)

    def get_by_code(self, tenant_id: int, code: str) -> Optional[Menu]:
        """Get menu by code"""
        return self.db.query(Menu).filter(
            Menu.tenant_id == tenant_id,
            Menu.menu_code == code
        ).first()

    def get_by_tenant(self, tenant_id: int, skip: int = 0, limit: int = 100) -> List[Menu]:
        """Get all menus in tenant"""
        return self.db.query(Menu).filter(
            Menu.tenant_id == tenant_id
        ).order_by(Menu.display_order).offset(skip).limit(limit).all()

    def get_top_level_menus(self, tenant_id: int) -> List[Menu]:
        """Get top-level menus (no parent)"""
        return self.db.query(Menu).filter(
            Menu.tenant_id == tenant_id,
            Menu.parent_id.is_(None)
        ).order_by(Menu.display_order).all()

    def get_submenu(self, tenant_id: int, parent_id: int) -> List[Menu]:
        """Get submenus for parent"""
        return self.db.query(Menu).filter(
            Menu.tenant_id == tenant_id,
            Menu.parent_id == parent_id
        ).order_by(Menu.display_order).all()


# ==================== Board Service ====================

class BoardService(BaseService[Board]):
    """Service for board management"""

    def __init__(self, db: Session):
        super().__init__(db, Board)

    def get_by_code(self, tenant_id: int, code: str) -> Optional[Board]:
        """Get board by code"""
        return self.db.query(Board).filter(
            Board.tenant_id == tenant_id,
            Board.board_code == code
        ).first()

    def get_by_tenant(self, tenant_id: int, skip: int = 0, limit: int = 100) -> List[Board]:
        """Get all boards in tenant"""
        return self.db.query(Board).filter(
            Board.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()
