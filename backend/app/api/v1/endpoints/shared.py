"""
API Endpoints for Shared Models
Includes CRUD operations for tenants, users, roles, permissions, etc.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.shared import (
    TenantCreate, TenantUpdate, TenantResponse, TenantDetailResponse,
    UserCreate, UserUpdate, UserResponse, UserDetailResponse,
    UserGroupCreate, UserGroupUpdate, UserGroupResponse, UserGroupDetailResponse,
    UserGroupMemberCreate, UserGroupMemberResponse,
    RoleCreate, RoleUpdate, RoleResponse, RoleDetailResponse,
    UserRoleCreate, UserRoleResponse,
    PermissionCreate, PermissionUpdate, PermissionResponse,
    RolePermissionCreate, RolePermissionResponse,
    MenuCreate, MenuUpdate, MenuResponse,
    BoardCreate, BoardUpdate, BoardResponse,
)
from app.services.shared import (
    TenantService, UserService, UserGroupService, RoleService,
    PermissionService, UserRoleService, MenuService, BoardService
)
from app.api.tenant_middleware import TenantContext
from app.api.deps import get_current_tenant

router = APIRouter()


# ==================== Tenant Endpoints ====================

@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED, tags=["Tenants"])
def create_tenant(
    tenant_in: TenantCreate,
    db: Session = Depends(get_db)
):
    """Create a new tenant"""
    service = TenantService(db)
    try:
        tenant = service.create(tenant_in)
        return tenant
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create tenant: {str(e)}"
        )


@router.get("/tenants", response_model=List[TenantResponse], tags=["Tenants"])
def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all tenants"""
    service = TenantService(db)
    return service.get_all(skip, limit)


@router.get("/tenants/{tenant_id}", response_model=TenantDetailResponse, tags=["Tenants"])
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db)
):
    """Get tenant by ID"""
    service = TenantService(db)
    tenant = service.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.get("/tenants/code/{code}", response_model=TenantResponse, tags=["Tenants"])
def get_tenant_by_code(
    code: str,
    db: Session = Depends(get_db)
):
    """Get tenant by code"""
    service = TenantService(db)
    tenant = service.get_by_code(code)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.patch("/tenants/{tenant_id}", response_model=TenantResponse, tags=["Tenants"])
def update_tenant(
    tenant_id: int,
    tenant_in: TenantUpdate,
    db: Session = Depends(get_db)
):
    """Update tenant"""
    service = TenantService(db)
    tenant = service.update(tenant_id, tenant_in)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.delete("/tenants/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tenants"])
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db)
):
    """Delete (soft delete) tenant"""
    service = TenantService(db)
    if not service.delete(tenant_id):
        raise HTTPException(status_code=404, detail="Tenant not found")


@router.get("/tenants/current/info", response_model=dict, tags=["Tenants"])
def get_current_tenant_info(
    request: Request,
    current_tenant: TenantContext = Depends(get_current_tenant)
):
    """
    Get current tenant information from request context
    This is populated by the tenant middleware
    """
    return {
        "tenant_id": current_tenant.tenant_id,
        "tenant_code": current_tenant.tenant_code,
        "tenant_name": current_tenant.tenant_name,
        "settings": current_tenant.settings,
    }


# ==================== User Endpoints ====================

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user"""
    service = UserService(db)
    try:
        user = service.create(user_in)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )


@router.get("/users", response_model=List[UserResponse], tags=["Users"])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all users"""
    service = UserService(db)
    return service.get_all(skip, limit)


@router.get("/users/{user_id}", response_model=UserDetailResponse, tags=["Users"])
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    service = UserService(db)
    user = service.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/tenants/{tenant_id}/users", response_model=List[UserResponse], tags=["Users"])
def get_tenant_users(
    tenant_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all users in tenant"""
    service = UserService(db)
    return service.get_by_tenant(tenant_id, skip, limit)


@router.patch("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user"""
    service = UserService(db)
    user = service.update(user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Delete (soft delete) user"""
    service = UserService(db)
    if not service.delete(user_id):
        raise HTTPException(status_code=404, detail="User not found")


# ==================== User Group Endpoints ====================

@router.post("/user-groups", response_model=UserGroupResponse, status_code=status.HTTP_201_CREATED, tags=["User Groups"])
def create_user_group(
    group_in: UserGroupCreate,
    db: Session = Depends(get_db)
):
    """Create a new user group"""
    service = UserGroupService(db)
    try:
        group = service.create(group_in)
        return group
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create group: {str(e)}"
        )


@router.get("/user-groups", response_model=List[UserGroupResponse], tags=["User Groups"])
def list_user_groups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all user groups"""
    service = UserGroupService(db)
    return service.get_all(skip, limit)


@router.get("/user-groups/{group_id}", response_model=UserGroupDetailResponse, tags=["User Groups"])
def get_user_group(
    group_id: int,
    db: Session = Depends(get_db)
):
    """Get user group by ID"""
    service = UserGroupService(db)
    group = service.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="User group not found")
    return group


@router.get("/tenants/{tenant_id}/user-groups", response_model=List[UserGroupResponse], tags=["User Groups"])
def get_tenant_user_groups(
    tenant_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all user groups in tenant"""
    service = UserGroupService(db)
    return service.get_by_tenant(tenant_id, skip, limit)


@router.patch("/user-groups/{group_id}", response_model=UserGroupResponse, tags=["User Groups"])
def update_user_group(
    group_id: int,
    group_in: UserGroupUpdate,
    db: Session = Depends(get_db)
):
    """Update user group"""
    service = UserGroupService(db)
    group = service.update(group_id, group_in.model_dump(exclude_unset=True))
    if not group:
        raise HTTPException(status_code=404, detail="User group not found")
    return group


@router.delete("/user-groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["User Groups"])
def delete_user_group(
    group_id: int,
    db: Session = Depends(get_db)
):
    """Delete (soft delete) user group"""
    service = UserGroupService(db)
    if not service.delete(group_id):
        raise HTTPException(status_code=404, detail="User group not found")


# ==================== User Group Member Endpoints ====================

@router.post("/user-groups/{group_id}/members", response_model=UserGroupMemberResponse, status_code=status.HTTP_201_CREATED, tags=["User Groups"])
def add_group_member(
    group_id: int,
    member_in: UserGroupMemberCreate,
    db: Session = Depends(get_db)
):
    """Add user to group"""
    service = UserGroupService(db)
    try:
        membership = service.add_user(group_id, member_in.user_id)
        return membership
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add member: {str(e)}"
        )


@router.delete("/user-groups/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["User Groups"])
def remove_group_member(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Remove user from group"""
    service = UserGroupService(db)
    if not service.remove_user(group_id, user_id):
        raise HTTPException(status_code=404, detail="User group membership not found")


@router.get("/user-groups/{group_id}/members", response_model=List[UserResponse], tags=["User Groups"])
def get_group_members(
    group_id: int,
    db: Session = Depends(get_db)
):
    """Get all members of group"""
    service = UserGroupService(db)
    return service.get_group_members(group_id)


@router.get("/users/{user_id}/groups", response_model=List[UserGroupResponse], tags=["User Groups"])
def get_user_groups(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get all groups for user"""
    service = UserGroupService(db)
    return service.get_user_groups(user_id)


# ==================== Role Endpoints ====================

@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED, tags=["Roles"])
def create_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db)
):
    """Create a new role"""
    service = RoleService(db)
    try:
        role = service.create(role_in)
        return role
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create role: {str(e)}"
        )


@router.get("/roles", response_model=List[RoleResponse], tags=["Roles"])
def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all roles"""
    service = RoleService(db)
    return service.get_all(skip, limit)


@router.get("/roles/{role_id}", response_model=RoleDetailResponse, tags=["Roles"])
def get_role(
    role_id: int,
    db: Session = Depends(get_db)
):
    """Get role by ID"""
    service = RoleService(db)
    role = service.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.patch("/roles/{role_id}", response_model=RoleResponse, tags=["Roles"])
def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: Session = Depends(get_db)
):
    """Update role"""
    service = RoleService(db)
    role = service.update(role_id, role_in.model_dump(exclude_unset=True))
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Roles"])
def delete_role(
    role_id: int,
    db: Session = Depends(get_db)
):
    """Delete (soft delete) role"""
    service = RoleService(db)
    if not service.delete(role_id):
        raise HTTPException(status_code=404, detail="Role not found")


# ==================== Role Permission Endpoints ====================

@router.post("/roles/{role_id}/permissions", response_model=RolePermissionResponse, status_code=status.HTTP_201_CREATED, tags=["Roles"])
def add_role_permission(
    role_id: int,
    perm_in: RolePermissionCreate,
    db: Session = Depends(get_db)
):
    """Add permission to role"""
    service = RoleService(db)
    try:
        role_perm = service.add_permission(role_id, perm_in.permission_id)
        return role_perm
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add permission: {str(e)}"
        )


@router.delete("/roles/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Roles"])
def remove_role_permission(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_db)
):
    """Remove permission from role"""
    service = RoleService(db)
    if not service.remove_permission(role_id, permission_id):
        raise HTTPException(status_code=404, detail="Role permission not found")


@router.get("/roles/{role_id}/permissions", response_model=List[PermissionResponse], tags=["Roles"])
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db)
):
    """Get all permissions for role"""
    service = RoleService(db)
    return service.get_role_permissions(role_id)


# ==================== User Role Endpoints ====================

@router.post("/users/{user_id}/roles", response_model=UserRoleResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def assign_role_to_user(
    user_id: int,
    role_in: UserRoleCreate,
    db: Session = Depends(get_db)
):
    """Assign role to user"""
    service = UserRoleService(db)
    try:
        user_role = service.assign_role(user_id, role_in.role_id)
        return user_role
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to assign role: {str(e)}"
        )


@router.delete("/users/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def revoke_role_from_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db)
):
    """Revoke role from user"""
    service = UserRoleService(db)
    if not service.revoke_role(user_id, role_id):
        raise HTTPException(status_code=404, detail="User role not found")


@router.get("/users/{user_id}/roles", response_model=List[RoleResponse], tags=["Users"])
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get all roles for user"""
    service = RoleService(db)
    return service.get_user_roles(user_id)


@router.get("/users/{user_id}/permissions", response_model=List[PermissionResponse], tags=["Users"])
def get_user_permissions(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get all permissions for user through roles"""
    service = UserRoleService(db)
    return service.get_user_permissions(user_id)


# ==================== Permission Endpoints ====================

@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED, tags=["Permissions"])
def create_permission(
    perm_in: PermissionCreate,
    db: Session = Depends(get_db)
):
    """Create a new permission"""
    service = PermissionService(db)
    try:
        perm = service.create(perm_in)
        return perm
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create permission: {str(e)}"
        )


@router.get("/permissions", response_model=List[PermissionResponse], tags=["Permissions"])
def list_permissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all permissions"""
    service = PermissionService(db)
    return service.get_all(skip, limit)


@router.get("/permissions/{permission_id}", response_model=PermissionResponse, tags=["Permissions"])
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db)
):
    """Get permission by ID"""
    service = PermissionService(db)
    perm = service.get(permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    return perm


@router.patch("/permissions/{permission_id}", response_model=PermissionResponse, tags=["Permissions"])
def update_permission(
    permission_id: int,
    perm_in: PermissionUpdate,
    db: Session = Depends(get_db)
):
    """Update permission"""
    service = PermissionService(db)
    perm = service.update(permission_id, perm_in.model_dump(exclude_unset=True))
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    return perm


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Permissions"])
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db)
):
    """Delete (soft delete) permission"""
    service = PermissionService(db)
    if not service.delete(permission_id):
        raise HTTPException(status_code=404, detail="Permission not found")


# ==================== Menu Endpoints ====================

@router.post("/menus", response_model=MenuResponse, status_code=status.HTTP_201_CREATED, tags=["Menus"])
def create_menu(
    menu_in: MenuCreate,
    db: Session = Depends(get_db)
):
    """Create a new menu"""
    service = MenuService(db)
    try:
        menu = service.create(menu_in.model_dump())
        return menu
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create menu: {str(e)}"
        )


@router.get("/menus", response_model=List[MenuResponse], tags=["Menus"])
def list_menus(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all menus"""
    service = MenuService(db)
    return service.get_all(skip, limit)


@router.get("/menus/{menu_id}", response_model=MenuResponse, tags=["Menus"])
def get_menu(
    menu_id: int,
    db: Session = Depends(get_db)
):
    """Get menu by ID"""
    service = MenuService(db)
    menu = service.get(menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu


@router.get("/tenants/{tenant_id}/menus", response_model=List[MenuResponse], tags=["Menus"])
def get_tenant_menus(
    tenant_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all menus in tenant"""
    service = MenuService(db)
    return service.get_by_tenant(tenant_id, skip, limit)


@router.patch("/menus/{menu_id}", response_model=MenuResponse, tags=["Menus"])
def update_menu(
    menu_id: int,
    menu_in: MenuUpdate,
    db: Session = Depends(get_db)
):
    """Update menu"""
    service = MenuService(db)
    menu = service.update(menu_id, menu_in.model_dump(exclude_unset=True))
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu


@router.delete("/menus/{menu_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Menus"])
def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db)
):
    """Delete (soft delete) menu"""
    service = MenuService(db)
    if not service.delete(menu_id):
        raise HTTPException(status_code=404, detail="Menu not found")


# ==================== Board Endpoints ====================

@router.post("/boards", response_model=BoardResponse, status_code=status.HTTP_201_CREATED, tags=["Boards"])
def create_board(
    board_in: BoardCreate,
    db: Session = Depends(get_db)
):
    """Create a new board"""
    service = BoardService(db)
    try:
        board = service.create(board_in.model_dump())
        return board
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create board: {str(e)}"
        )


@router.get("/boards", response_model=List[BoardResponse], tags=["Boards"])
def list_boards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all boards"""
    service = BoardService(db)
    return service.get_all(skip, limit)


@router.get("/boards/{board_id}", response_model=BoardResponse, tags=["Boards"])
def get_board(
    board_id: int,
    db: Session = Depends(get_db)
):
    """Get board by ID"""
    service = BoardService(db)
    board = service.get(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@router.get("/tenants/{tenant_id}/boards", response_model=List[BoardResponse], tags=["Boards"])
def get_tenant_boards(
    tenant_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all boards in tenant"""
    service = BoardService(db)
    return service.get_by_tenant(tenant_id, skip, limit)


@router.patch("/boards/{board_id}", response_model=BoardResponse, tags=["Boards"])
def update_board(
    board_id: int,
    board_in: BoardUpdate,
    db: Session = Depends(get_db)
):
    """Update board"""
    service = BoardService(db)
    board = service.update(board_id, board_in.model_dump(exclude_unset=True))
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@router.delete("/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Boards"])
def delete_board(
    board_id: int,
    db: Session = Depends(get_db)
):
    """Delete (soft delete) board"""
    service = BoardService(db)
    if not service.delete(board_id):
        raise HTTPException(status_code=404, detail="Board not found")
