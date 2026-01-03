"""
Menu Service Layer
Business logic for menu management
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.shared import Menu, MenuTypeEnum, User
from app.schemas.menu import (
    MenuCreate,
    MenuUpdate,
    MenuMove,
    MenuReorder,
    MenuBulkReorder,
    MenuQueryParams
)


class MenuService:
    """Service class for menu operations"""

    @staticmethod
    def validate_parent_exists(
        db: Session,
        parent_id: int,
        tenant_id: int
    ) -> Menu:
        """
        Validate that parent menu exists and belongs to same tenant

        Args:
            db: Database session
            parent_id: Parent menu ID
            tenant_id: Tenant ID

        Returns:
            Parent menu object

        Raises:
            HTTPException: If parent not found or belongs to different tenant
        """
        parent = db.query(Menu).filter(
            Menu.id == parent_id,
            Menu.tenant_id == tenant_id,
            Menu.is_deleted == False
        ).first()

        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent menu with ID {parent_id} not found"
            )

        return parent

    @staticmethod
    def validate_no_circular_reference(
        db: Session,
        menu_id: int,
        new_parent_id: Optional[int]
    ) -> None:
        """
        Prevent circular references in menu hierarchy

        Args:
            db: Database session
            menu_id: Menu ID being updated
            new_parent_id: New parent ID

        Raises:
            HTTPException: If circular reference detected
        """
        if new_parent_id is None:
            return

        if menu_id == new_parent_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Menu cannot be its own parent"
            )

        # Check if new_parent_id is a descendant of menu_id
        current_id = new_parent_id
        visited = set()

        while current_id is not None:
            if current_id in visited:
                # Circular reference in existing data
                break

            if current_id == menu_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot move menu to its own descendant"
                )

            visited.add(current_id)

            parent = db.query(Menu).filter(
                Menu.id == current_id,
                Menu.is_deleted == False
            ).first()

            if not parent:
                break

            current_id = parent.parent_id

    @staticmethod
    def calculate_depth_and_path(
        db: Session,
        parent_id: Optional[int],
        menu_id: Optional[int] = None
    ) -> tuple[int, str]:
        """
        Calculate depth and path for menu based on parent

        Args:
            db: Database session
            parent_id: Parent menu ID
            menu_id: Current menu ID (for path generation)

        Returns:
            Tuple of (depth, path)
        """
        if parent_id is None:
            return 0, f"/{menu_id}" if menu_id else "/"

        parent = db.query(Menu).filter(
            Menu.id == parent_id,
            Menu.is_deleted == False
        ).first()

        if not parent:
            return 0, f"/{menu_id}" if menu_id else "/"

        depth = parent.depth + 1
        parent_path = parent.path or f"/{parent_id}"
        path = f"{parent_path}/{menu_id}" if menu_id else parent_path

        return depth, path

    @staticmethod
    def get_menu_by_id(
        db: Session,
        menu_id: int,
        tenant_id: int
    ) -> Menu:
        """
        Get menu by ID with tenant validation

        Args:
            db: Database session
            menu_id: Menu ID
            tenant_id: Tenant ID

        Returns:
            Menu object

        Raises:
            HTTPException: If menu not found
        """
        menu = db.query(Menu).filter(
            Menu.id == menu_id,
            Menu.tenant_id == tenant_id,
            Menu.is_deleted == False
        ).first()

        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu with ID {menu_id} not found"
            )

        return menu

    @staticmethod
    def get_menus(
        db: Session,
        tenant_id: int,
        params: MenuQueryParams
    ) -> tuple[List[Menu], int]:
        """
        Get list of menus with filtering and pagination

        Args:
            db: Database session
            tenant_id: Tenant ID
            params: Query parameters

        Returns:
            Tuple of (menus list, total count)
        """
        # Base query
        query = db.query(Menu).filter(
            Menu.tenant_id == tenant_id,
            Menu.is_deleted == False
        )

        # Apply filters
        if params.menu_type is not None:
            query = query.filter(Menu.menu_type == params.menu_type)

        if params.parent_id is not None:
            query = query.filter(Menu.parent_id == params.parent_id)
        elif hasattr(params, 'parent_id') and params.parent_id == 'null':
            query = query.filter(Menu.parent_id.is_(None))

        if params.is_visible is not None:
            query = query.filter(Menu.is_visible == params.is_visible)

        if params.is_active is not None:
            query = query.filter(Menu.is_active == params.is_active)

        if params.search:
            search_pattern = f"%{params.search}%"
            query = query.filter(
                or_(
                    Menu.menu_name.ilike(search_pattern),
                    Menu.menu_code.ilike(search_pattern)
                )
            )

        # Get total count
        total = query.count()

        # Apply sorting
        query = query.order_by(
            Menu.menu_type,
            Menu.parent_id.nullsfirst(),
            Menu.display_order,
            Menu.id
        )

        # Apply pagination
        query = query.offset(params.skip).limit(params.limit)

        return query.all(), total

    @staticmethod
    def get_menu_tree(
        db: Session,
        tenant_id: int,
        menu_type: Optional[MenuTypeEnum] = None,
        parent_id: Optional[int] = None
    ) -> List[Menu]:
        """
        Get menu tree structure

        Args:
            db: Database session
            tenant_id: Tenant ID
            menu_type: Optional menu type filter
            parent_id: Optional parent ID filter (None for root)

        Returns:
            List of root menus with children populated
        """
        # Build query
        query = db.query(Menu).filter(
            Menu.tenant_id == tenant_id,
            Menu.is_deleted == False,
            Menu.is_active == True
        )

        if menu_type:
            query = query.filter(Menu.menu_type == menu_type)

        # Get all menus (we'll build tree in memory)
        all_menus = query.order_by(Menu.display_order, Menu.id).all()

        # Build tree structure
        menu_map = {menu.id: menu for menu in all_menus}
        root_menus = []

        for menu in all_menus:
            if menu.parent_id is None:
                root_menus.append(menu)
            elif menu.parent_id in menu_map:
                parent = menu_map[menu.parent_id]
                if not hasattr(parent, 'children'):
                    parent.children = []
                parent.children.append(menu)

        return root_menus

    @staticmethod
    def create_menu(
        db: Session,
        tenant_id: int,
        menu_data: MenuCreate,
        current_user: User
    ) -> Menu:
        """
        Create a new menu

        Args:
            db: Database session
            tenant_id: Tenant ID
            menu_data: Menu creation data
            current_user: Current authenticated user

        Returns:
            Created menu object

        Raises:
            HTTPException: If validation fails or duplicate menu_code
        """
        try:
            # Validate parent if specified
            if menu_data.parent_id:
                parent = MenuService.validate_parent_exists(
                    db, menu_data.parent_id, tenant_id
                )

                # Check depth limit (e.g., max 5 levels)
                if parent.depth >= 4:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Maximum menu depth (5 levels) exceeded"
                    )

            # Calculate depth and path (will update path after creation)
            depth, _ = MenuService.calculate_depth_and_path(
                db, menu_data.parent_id, None
            )

            # Create menu object
            menu = Menu(
                tenant_id=tenant_id,
                menu_name=menu_data.menu_name,
                menu_code=menu_data.menu_code,
                description=menu_data.description,
                menu_type=menu_data.menu_type,
                menu_url=menu_data.menu_url,
                menu_icon=menu_data.menu_icon,
                link_type=menu_data.link_type,
                parent_id=menu_data.parent_id,
                depth=depth,
                display_order=menu_data.display_order,
                permission_type=menu_data.permission_type,
                is_visible=menu_data.is_visible,
                is_active=menu_data.is_active,
                metadata=menu_data.metadata,
                created_by=current_user.username,
                updated_by=current_user.username
            )

            db.add(menu)
            db.flush()  # Get ID before commit

            # Update path with actual ID
            _, path = MenuService.calculate_depth_and_path(
                db, menu_data.parent_id, menu.id
            )
            menu.path = path

            db.commit()
            db.refresh(menu)

            return menu

        except IntegrityError as e:
            db.rollback()
            if 'uk_tenant_menu_code' in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Menu with code '{menu_data.menu_code}' already exists"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation"
            )
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create menu: {str(e)}"
            )

    @staticmethod
    def update_menu(
        db: Session,
        menu_id: int,
        tenant_id: int,
        menu_data: MenuUpdate,
        current_user: User
    ) -> Menu:
        """
        Update an existing menu

        Args:
            db: Database session
            menu_id: Menu ID to update
            tenant_id: Tenant ID
            menu_data: Menu update data
            current_user: Current authenticated user

        Returns:
            Updated menu object

        Raises:
            HTTPException: If validation fails
        """
        try:
            # Get existing menu
            menu = MenuService.get_menu_by_id(db, menu_id, tenant_id)

            # Validate parent change
            if menu_data.parent_id is not None:
                if menu_data.parent_id != menu.parent_id:
                    MenuService.validate_no_circular_reference(
                        db, menu_id, menu_data.parent_id
                    )

                    if menu_data.parent_id:
                        parent = MenuService.validate_parent_exists(
                            db, menu_data.parent_id, tenant_id
                        )

                        if parent.depth >= 4:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Maximum menu depth (5 levels) exceeded"
                            )

                    # Recalculate depth and path
                    depth, path = MenuService.calculate_depth_and_path(
                        db, menu_data.parent_id, menu_id
                    )
                    menu.depth = depth
                    menu.path = path

            # Update fields
            update_data = menu_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(menu, field, value)

            menu.updated_by = current_user.username

            db.commit()
            db.refresh(menu)

            return menu

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update menu: {str(e)}"
            )

    @staticmethod
    def delete_menu(
        db: Session,
        menu_id: int,
        tenant_id: int,
        current_user: User
    ) -> Menu:
        """
        Soft delete a menu (and its children)

        Args:
            db: Database session
            menu_id: Menu ID to delete
            tenant_id: Tenant ID
            current_user: Current authenticated user

        Returns:
            Deleted menu object

        Raises:
            HTTPException: If menu not found
        """
        try:
            # Get menu
            menu = MenuService.get_menu_by_id(db, menu_id, tenant_id)

            # Get all descendants
            descendants = db.query(Menu).filter(
                Menu.tenant_id == tenant_id,
                Menu.path.like(f"{menu.path}/%"),
                Menu.is_deleted == False
            ).all()

            # Soft delete menu and all descendants
            menu.is_deleted = True
            menu.is_active = False
            menu.updated_by = current_user.username

            for child in descendants:
                child.is_deleted = True
                child.is_active = False
                child.updated_by = current_user.username

            db.commit()
            db.refresh(menu)

            return menu

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete menu: {str(e)}"
            )

    @staticmethod
    def bulk_delete_menus(
        db: Session,
        menu_ids: List[int],
        tenant_id: int,
        current_user: User
    ) -> int:
        """
        Bulk soft delete menus

        Args:
            db: Database session
            menu_ids: List of menu IDs to delete
            tenant_id: Tenant ID
            current_user: Current authenticated user

        Returns:
            Number of menus deleted
        """
        try:
            deleted_count = 0

            for menu_id in menu_ids:
                try:
                    MenuService.delete_menu(db, menu_id, tenant_id, current_user)
                    deleted_count += 1
                except HTTPException:
                    # Skip if menu not found
                    continue

            return deleted_count

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to bulk delete menus: {str(e)}"
            )

    @staticmethod
    def reorder_menus(
        db: Session,
        tenant_id: int,
        reorder_data: MenuBulkReorder,
        current_user: User
    ) -> List[Menu]:
        """
        Bulk reorder menus

        Args:
            db: Database session
            tenant_id: Tenant ID
            reorder_data: Reorder data
            current_user: Current authenticated user

        Returns:
            List of updated menus
        """
        try:
            updated_menus = []

            for item in reorder_data.items:
                menu = MenuService.get_menu_by_id(db, item.menu_id, tenant_id)
                menu.display_order = item.new_order
                menu.updated_by = current_user.username
                updated_menus.append(menu)

            db.commit()

            for menu in updated_menus:
                db.refresh(menu)

            return updated_menus

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to reorder menus: {str(e)}"
            )

    @staticmethod
    def move_menu(
        db: Session,
        menu_id: int,
        tenant_id: int,
        move_data: MenuMove,
        current_user: User
    ) -> Menu:
        """
        Move menu to a different parent

        Args:
            db: Database session
            menu_id: Menu ID to move
            tenant_id: Tenant ID
            move_data: Move data
            current_user: Current authenticated user

        Returns:
            Updated menu object
        """
        try:
            # Get menu
            menu = MenuService.get_menu_by_id(db, menu_id, tenant_id)

            # Validate circular reference
            MenuService.validate_no_circular_reference(
                db, menu_id, move_data.new_parent_id
            )

            # Validate parent exists
            if move_data.new_parent_id:
                parent = MenuService.validate_parent_exists(
                    db, move_data.new_parent_id, tenant_id
                )

                if parent.depth >= 4:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Maximum menu depth (5 levels) exceeded"
                    )

            # Update parent
            menu.parent_id = move_data.new_parent_id

            # Recalculate depth and path
            depth, path = MenuService.calculate_depth_and_path(
                db, move_data.new_parent_id, menu_id
            )
            menu.depth = depth
            menu.path = path

            # Update order if specified
            if move_data.new_order is not None:
                menu.display_order = move_data.new_order

            menu.updated_by = current_user.username

            # Update all descendants' depth and path
            descendants = db.query(Menu).filter(
                Menu.tenant_id == tenant_id,
                Menu.path.like(f"{path}/%"),
                Menu.is_deleted == False
            ).all()

            for child in descendants:
                # Recalculate child's depth and path
                child_depth, child_path = MenuService.calculate_depth_and_path(
                    db, child.parent_id, child.id
                )
                child.depth = child_depth
                child.path = child_path
                child.updated_by = current_user.username

            db.commit()
            db.refresh(menu)

            return menu

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to move menu: {str(e)}"
            )

    @staticmethod
    def get_menus_by_user(
        db: Session,
        tenant_id: int,
        user: Optional[User],
        menu_type: MenuTypeEnum
    ) -> List[Menu]:
        """
        Get menus visible to a specific user based on permissions

        Args:
            db: Database session
            tenant_id: Tenant ID
            user: Current user (None for public menus)
            menu_type: Menu type to retrieve

        Returns:
            List of menus visible to user
        """
        query = db.query(Menu).filter(
            Menu.tenant_id == tenant_id,
            Menu.menu_type == menu_type,
            Menu.is_deleted == False,
            Menu.is_active == True,
            Menu.is_visible == True
        )

        if user is None:
            # Only public menus
            query = query.filter(Menu.permission_type == 'public')
        else:
            # Public or authenticated menus
            # TODO: Add role-based and permission-based filtering
            query = query.filter(
                or_(
                    Menu.permission_type == 'public',
                    Menu.permission_type == 'authenticated'
                )
            )

        return query.order_by(
            Menu.parent_id.nullsfirst(),
            Menu.display_order,
            Menu.id
        ).all()
