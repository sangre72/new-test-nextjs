"""
Menu API Endpoints
RESTful API for menu management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_superuser, get_optional_current_user
from app.models.shared import User, MenuTypeEnum
from app.schemas.menu import (
    MenuCreate,
    MenuUpdate,
    MenuResponse,
    MenuTreeNode,
    MenuListResponse,
    MenuTreeResponse,
    MenuBulkDeleteRequest,
    MenuBulkReorder,
    MenuMove,
    MenuQueryParams
)
from app.services.menu import MenuService

router = APIRouter(prefix="/menus", tags=["Menus"])


# ============================================================================
# Public Endpoints (Menu Retrieval)
# ============================================================================

@router.get("/public/tree", response_model=MenuTreeResponse)
def get_public_menu_tree(
    menu_type: MenuTypeEnum = Query(..., description="Menu type to retrieve"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Get public menu tree (hierarchical structure)

    Security: Public endpoint, no authentication required
    Returns menus based on permission_type and user authentication status

    Args:
        menu_type: Menu type (user, site, admin)
        db: Database session
        current_user: Optional current user

    Returns:
        Menu tree with nested children
    """
    try:
        # Get tenant from current user or default
        tenant_id = current_user.tenant_id if current_user else 1  # TODO: Get from request context

        # Get menu tree based on user permissions
        root_menus = MenuService.get_menus_by_user(
            db=db,
            tenant_id=tenant_id,
            user=current_user,
            menu_type=menu_type
        )

        # Build tree structure
        menu_map = {}
        tree_nodes = []

        # First pass: create all nodes
        for menu in root_menus:
            node = MenuTreeNode.from_orm(menu)
            node.children = []
            menu_map[menu.id] = node

            if menu.parent_id is None:
                tree_nodes.append(node)

        # Second pass: build tree
        for menu in root_menus:
            if menu.parent_id and menu.parent_id in menu_map:
                menu_map[menu.parent_id].children.append(menu_map[menu.id])

        return MenuTreeResponse(
            total=len(root_menus),
            items=tree_nodes
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve menu tree: {str(e)}"
        )


# ============================================================================
# Admin Endpoints (CRUD Operations)
# ============================================================================

@router.get("", response_model=MenuListResponse)
def get_menus(
    menu_type: Optional[MenuTypeEnum] = Query(None, description="Filter by menu type"),
    parent_id: Optional[int] = Query(None, description="Filter by parent ID"),
    is_visible: Optional[bool] = Query(None, description="Filter by visibility"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, max_length=100, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get list of menus with filtering and pagination

    Security: Requires superuser authentication

    Args:
        menu_type: Optional menu type filter
        parent_id: Optional parent ID filter
        is_visible: Optional visibility filter
        is_active: Optional active status filter
        search: Optional search query
        skip: Pagination offset
        limit: Pagination limit
        db: Database session
        current_user: Current authenticated superuser

    Returns:
        Paginated list of menus
    """
    try:
        # Build query params
        params = MenuQueryParams(
            menu_type=menu_type,
            parent_id=parent_id,
            is_visible=is_visible,
            is_active=is_active,
            search=search,
            skip=skip,
            limit=limit
        )

        # Get menus
        menus, total = MenuService.get_menus(
            db=db,
            tenant_id=current_user.tenant_id,
            params=params
        )

        # Convert to response models
        menu_responses = [MenuResponse.from_orm(menu) for menu in menus]

        return MenuListResponse(
            total=total,
            items=menu_responses
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve menus: {str(e)}"
        )


@router.get("/tree", response_model=MenuTreeResponse)
def get_menu_tree_admin(
    menu_type: Optional[MenuTypeEnum] = Query(None, description="Filter by menu type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get menu tree structure (admin view - all menus)

    Security: Requires superuser authentication

    Args:
        menu_type: Optional menu type filter
        db: Database session
        current_user: Current authenticated superuser

    Returns:
        Menu tree with nested children
    """
    try:
        # Get menu tree
        root_menus = MenuService.get_menu_tree(
            db=db,
            tenant_id=current_user.tenant_id,
            menu_type=menu_type
        )

        # Convert to response models with children
        def build_tree_node(menu) -> MenuTreeNode:
            node = MenuTreeNode.from_orm(menu)
            if hasattr(menu, 'children'):
                node.children = [build_tree_node(child) for child in menu.children]
            else:
                node.children = []
            return node

        tree_nodes = [build_tree_node(menu) for menu in root_menus]

        return MenuTreeResponse(
            total=len(root_menus),
            items=tree_nodes
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve menu tree: {str(e)}"
        )


@router.get("/{menu_id}", response_model=MenuResponse)
def get_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get menu by ID

    Security: Requires superuser authentication

    Args:
        menu_id: Menu ID
        db: Database session
        current_user: Current authenticated superuser

    Returns:
        Menu details
    """
    try:
        menu = MenuService.get_menu_by_id(
            db=db,
            menu_id=menu_id,
            tenant_id=current_user.tenant_id
        )

        return MenuResponse.from_orm(menu)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve menu: {str(e)}"
        )


@router.post("", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
def create_menu(
    menu_data: MenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Create a new menu

    Security: Requires superuser authentication
    Input Validation: All fields validated via Pydantic schema

    Args:
        menu_data: Menu creation data
        db: Database session
        current_user: Current authenticated superuser

    Returns:
        Created menu
    """
    try:
        menu = MenuService.create_menu(
            db=db,
            tenant_id=current_user.tenant_id,
            menu_data=menu_data,
            current_user=current_user
        )

        return MenuResponse.from_orm(menu)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create menu: {str(e)}"
        )


@router.put("/{menu_id}", response_model=MenuResponse)
def update_menu(
    menu_id: int,
    menu_data: MenuUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Update an existing menu

    Security: Requires superuser authentication
    Input Validation: All fields validated via Pydantic schema

    Args:
        menu_id: Menu ID to update
        menu_data: Menu update data
        db: Database session
        current_user: Current authenticated superuser

    Returns:
        Updated menu
    """
    try:
        menu = MenuService.update_menu(
            db=db,
            menu_id=menu_id,
            tenant_id=current_user.tenant_id,
            menu_data=menu_data,
            current_user=current_user
        )

        return MenuResponse.from_orm(menu)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update menu: {str(e)}"
        )


@router.delete("/{menu_id}", response_model=MenuResponse)
def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Delete a menu (soft delete)

    Security: Requires superuser authentication
    Note: Also deletes all child menus (cascading soft delete)

    Args:
        menu_id: Menu ID to delete
        db: Database session
        current_user: Current authenticated superuser

    Returns:
        Deleted menu
    """
    try:
        menu = MenuService.delete_menu(
            db=db,
            menu_id=menu_id,
            tenant_id=current_user.tenant_id,
            current_user=current_user
        )

        return MenuResponse.from_orm(menu)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete menu: {str(e)}"
        )


@router.post("/bulk-delete", status_code=status.HTTP_200_OK)
def bulk_delete_menus(
    request: MenuBulkDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Bulk delete menus (soft delete)

    Security: Requires superuser authentication

    Args:
        request: Bulk delete request with menu IDs
        db: Database session
        current_user: Current authenticated superuser

    Returns:
        Number of deleted menus
    """
    try:
        deleted_count = MenuService.bulk_delete_menus(
            db=db,
            menu_ids=request.menu_ids,
            tenant_id=current_user.tenant_id,
            current_user=current_user
        )

        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Successfully deleted {deleted_count} menus"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk delete menus: {str(e)}"
        )


@router.put("/reorder", response_model=List[MenuResponse])
def reorder_menus(
    reorder_data: MenuBulkReorder,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Bulk reorder menus (for drag-and-drop)

    Security: Requires superuser authentication

    Args:
        reorder_data: Reorder data with menu IDs and new orders
        db: Database session
        current_user: Current authenticated superuser

    Returns:
        List of updated menus
    """
    try:
        menus = MenuService.reorder_menus(
            db=db,
            tenant_id=current_user.tenant_id,
            reorder_data=reorder_data,
            current_user=current_user
        )

        return [MenuResponse.from_orm(menu) for menu in menus]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder menus: {str(e)}"
        )


@router.put("/{menu_id}/move", response_model=MenuResponse)
def move_menu(
    menu_id: int,
    move_data: MenuMove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Move menu to a different parent

    Security: Requires superuser authentication
    Validation: Prevents circular references

    Args:
        menu_id: Menu ID to move
        move_data: Move data with new parent ID and order
        db: Database session
        current_user: Current authenticated superuser

    Returns:
        Updated menu
    """
    try:
        menu = MenuService.move_menu(
            db=db,
            menu_id=menu_id,
            tenant_id=current_user.tenant_id,
            move_data=move_data,
            current_user=current_user
        )

        return MenuResponse.from_orm(menu)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to move menu: {str(e)}"
        )
