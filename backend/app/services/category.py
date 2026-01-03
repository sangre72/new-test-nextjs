"""
Category Service
Business logic for category management
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.board import BoardExtended as Board
from app.models.category import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryTreeResponse,
    CategoryReorderRequest,
)
import logging

logger = logging.getLogger(__name__)


class CategoryService:
    """Service for category management operations"""

    @staticmethod
    def _build_category_path(parent_id: Optional[int], category_id: int) -> str:
        """Build hierarchical path for a category"""
        if parent_id is None:
            return f"/{category_id}/"
        return f"/{category_id}/"  # Full path will be constructed in the database

    @staticmethod
    def _calculate_depth(parent_id: Optional[int], session: Session) -> int:
        """Calculate depth level based on parent"""
        if parent_id is None:
            return 0

        parent = session.query(Category).filter(Category.id == parent_id).first()
        if parent is None:
            return 0
        return parent.depth + 1

    @staticmethod
    def get_categories_tree(
        board_id: int,
        tenant_id: int,
        session: Session,
        include_inactive: bool = False
    ) -> List[CategoryTreeResponse]:
        """
        Get categories in hierarchical tree structure

        Args:
            board_id: Board ID
            tenant_id: Tenant ID
            session: Database session
            include_inactive: Include inactive categories

        Returns:
            List of categories in tree structure
        """
        try:
            query = session.query(Category).filter(
                and_(
                    Category.board_id == board_id,
                    Category.tenant_id == tenant_id,
                    Category.is_deleted == False
                )
            )

            if not include_inactive:
                query = query.filter(Category.is_active == True)

            query = query.order_by(Category.sort_order, Category.category_name)
            categories = query.all()

            # Build tree structure
            root_categories = [c for c in categories if c.parent_id is None]

            def build_tree(parent_list: List[Category]) -> List[Dict]:
                result = []
                for category in parent_list:
                    children = [c for c in categories if c.parent_id == category.id]
                    cat_dict = CategoryTreeResponse.model_validate(category)
                    cat_dict.children = build_tree(children) if children else []
                    result.append(cat_dict)
                return result

            return build_tree(root_categories)

        except Exception as e:
            logger.error(f"Error getting categories tree: {str(e)}")
            raise

    @staticmethod
    def get_categories_flat(
        board_id: int,
        tenant_id: int,
        session: Session,
        include_inactive: bool = False
    ) -> List[CategoryResponse]:
        """
        Get categories as flat list (with depth info)

        Args:
            board_id: Board ID
            tenant_id: Tenant ID
            session: Database session
            include_inactive: Include inactive categories

        Returns:
            Flat list of categories
        """
        try:
            query = session.query(Category).filter(
                and_(
                    Category.board_id == board_id,
                    Category.tenant_id == tenant_id,
                    Category.is_deleted == False
                )
            )

            if not include_inactive:
                query = query.filter(Category.is_active == True)

            query = query.order_by(Category.path, Category.sort_order)
            categories = query.all()

            return [CategoryResponse.model_validate(c) for c in categories]

        except Exception as e:
            logger.error(f"Error getting categories flat: {str(e)}")
            raise

    @staticmethod
    def get_category_by_id(
        category_id: int,
        tenant_id: int,
        session: Session
    ) -> Optional[CategoryResponse]:
        """Get a single category by ID"""
        try:
            category = session.query(Category).filter(
                and_(
                    Category.id == category_id,
                    Category.tenant_id == tenant_id,
                    Category.is_deleted == False
                )
            ).first()

            if not category:
                return None

            return CategoryResponse.model_validate(category)

        except Exception as e:
            logger.error(f"Error getting category {category_id}: {str(e)}")
            raise

    @staticmethod
    def create_category(
        category_create: CategoryCreate,
        created_by: str,
        session: Session
    ) -> CategoryResponse:
        """
        Create a new category

        Args:
            category_create: Category creation schema
            created_by: User ID or name who created
            session: Database session

        Returns:
            Created category response
        """
        try:
            # Verify board exists and belongs to tenant
            board = session.query(Board).filter(
                and_(
                    Board.id == category_create.board_id,
                    Board.tenant_id == category_create.tenant_id
                )
            ).first()

            if not board:
                raise ValueError(f"Board {category_create.board_id} not found in tenant {category_create.tenant_id}")

            # Check for duplicate category code in board
            existing = session.query(Category).filter(
                and_(
                    Category.board_id == category_create.board_id,
                    Category.category_code == category_create.category_code,
                    Category.is_deleted == False
                )
            ).first()

            if existing:
                raise ValueError(f"Category code '{category_create.category_code}' already exists in this board")

            # Validate parent if provided
            if category_create.parent_id:
                parent = session.query(Category).filter(
                    and_(
                        Category.id == category_create.parent_id,
                        Category.board_id == category_create.board_id,
                        Category.is_deleted == False
                    )
                ).first()

                if not parent:
                    raise ValueError(f"Parent category {category_create.parent_id} not found")

            # Calculate depth and path
            depth = CategoryService._calculate_depth(category_create.parent_id, session)

            # Create category
            category = Category(
                tenant_id=category_create.tenant_id,
                board_id=category_create.board_id,
                parent_id=category_create.parent_id,
                category_name=category_create.category_name,
                category_code=category_create.category_code,
                description=category_create.description,
                depth=depth,
                sort_order=category_create.sort_order,
                icon=category_create.icon,
                color=category_create.color,
                read_permission=category_create.read_permission,
                write_permission=category_create.write_permission,
                created_by=created_by
            )

            session.add(category)
            session.flush()  # Get the ID

            # Build path
            if category_create.parent_id:
                parent = session.query(Category).filter(
                    Category.id == category_create.parent_id
                ).first()
                path = f"{parent.path}{category.id}/"
            else:
                path = f"/{category.id}/"

            category.path = path
            session.commit()

            return CategoryResponse.model_validate(category)

        except IntegrityError as e:
            session.rollback()
            logger.error(f"Integrity error creating category: {str(e)}")
            raise ValueError("Category creation failed due to constraint violation")

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error creating category: {str(e)}")
            raise

        except Exception as e:
            session.rollback()
            logger.error(f"Error creating category: {str(e)}")
            raise

    @staticmethod
    def update_category(
        category_id: int,
        tenant_id: int,
        category_update: CategoryUpdate,
        updated_by: str,
        session: Session
    ) -> CategoryResponse:
        """
        Update a category

        Args:
            category_id: Category ID to update
            tenant_id: Tenant ID
            category_update: Update schema
            updated_by: User ID or name who updated
            session: Database session

        Returns:
            Updated category response
        """
        try:
            category = session.query(Category).filter(
                and_(
                    Category.id == category_id,
                    Category.tenant_id == tenant_id,
                    Category.is_deleted == False
                )
            ).first()

            if not category:
                raise ValueError(f"Category {category_id} not found")

            # Validate parent if changing
            if category_update.parent_id is not None and category_update.parent_id != category.parent_id:
                # Prevent circular references
                if category_update.parent_id == category_id:
                    raise ValueError("Category cannot be its own parent")

                # Prevent creating cycles (parent cannot be a descendant)
                parent = session.query(Category).filter(
                    Category.id == category_update.parent_id
                ).first()

                if parent:
                    # Check if parent is a descendant of this category
                    if parent.path and category.path and parent.path.startswith(category.path):
                        raise ValueError("Cannot set a descendant category as parent")
                else:
                    raise ValueError(f"Parent category {category_update.parent_id} not found")

            # Update fields
            if category_update.category_name is not None:
                category.category_name = category_update.category_name
            if category_update.description is not None:
                category.description = category_update.description
            if category_update.sort_order is not None:
                category.sort_order = category_update.sort_order
            if category_update.icon is not None:
                category.icon = category_update.icon
            if category_update.color is not None:
                category.color = category_update.color
            if category_update.read_permission is not None:
                category.read_permission = category_update.read_permission
            if category_update.write_permission is not None:
                category.write_permission = category_update.write_permission
            if category_update.is_active is not None:
                category.is_active = category_update.is_active

            # Handle parent change
            if category_update.parent_id is not None and category_update.parent_id != category.parent_id:
                category.parent_id = category_update.parent_id
                new_depth = CategoryService._calculate_depth(category_update.parent_id, session)
                category.depth = new_depth

                # Update path and all descendants
                if category_update.parent_id:
                    parent = session.query(Category).filter(
                        Category.id == category_update.parent_id
                    ).first()
                    new_path = f"{parent.path}{category_id}/"
                else:
                    new_path = f"/{category_id}/"

                category.path = new_path
                CategoryService._update_descendants_path(category_id, new_path, session)

            category.updated_by = updated_by
            session.commit()

            return CategoryResponse.model_validate(category)

        except IntegrityError as e:
            session.rollback()
            logger.error(f"Integrity error updating category: {str(e)}")
            raise ValueError("Category update failed due to constraint violation")

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error updating category: {str(e)}")
            raise

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating category: {str(e)}")
            raise

    @staticmethod
    def delete_category(
        category_id: int,
        tenant_id: int,
        session: Session
    ) -> bool:
        """
        Soft delete a category

        Args:
            category_id: Category ID to delete
            tenant_id: Tenant ID
            session: Database session

        Returns:
            True if deleted successfully
        """
        try:
            category = session.query(Category).filter(
                and_(
                    Category.id == category_id,
                    Category.tenant_id == tenant_id,
                    Category.is_deleted == False
                )
            ).first()

            if not category:
                raise ValueError(f"Category {category_id} not found")

            # Check for child categories
            children = session.query(Category).filter(
                and_(
                    Category.parent_id == category_id,
                    Category.is_deleted == False
                )
            ).count()

            if children > 0:
                raise ValueError(
                    f"Cannot delete category with {children} subcategories. "
                    "Delete subcategories first."
                )

            # Check for posts (you'll implement this when Post model exists)
            # post_count = session.query(Post).filter(
            #     and_(
            #         Post.category_id == category_id,
            #         Post.is_deleted == False
            #     )
            # ).count()
            #
            # if post_count > 0:
            #     raise ValueError(
            #         f"Cannot delete category with {post_count} posts. "
            #         "Move posts to another category first."
            #     )

            # Soft delete
            category.is_deleted = True
            session.commit()

            return True

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error deleting category: {str(e)}")
            raise

        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting category: {str(e)}")
            raise

    @staticmethod
    def reorder_categories(
        reorder_request: CategoryReorderRequest,
        tenant_id: int,
        session: Session
    ) -> bool:
        """
        Reorder category (for drag and drop)

        Args:
            reorder_request: Reorder request with category_id, new_parent_id, new_sort_order
            tenant_id: Tenant ID
            session: Database session

        Returns:
            True if reordered successfully
        """
        try:
            category = session.query(Category).filter(
                and_(
                    Category.id == reorder_request.category_id,
                    Category.tenant_id == tenant_id,
                    Category.is_deleted == False
                )
            ).first()

            if not category:
                raise ValueError(f"Category {reorder_request.category_id} not found")

            # Prevent circular references
            if reorder_request.new_parent_id == reorder_request.category_id:
                raise ValueError("Category cannot be its own parent")

            # Update parent if changed
            if reorder_request.new_parent_id != category.parent_id:
                if reorder_request.new_parent_id:
                    parent = session.query(Category).filter(
                        Category.id == reorder_request.new_parent_id
                    ).first()

                    if not parent:
                        raise ValueError(f"Parent category {reorder_request.new_parent_id} not found")

                    # Check for cycles
                    if parent.path and category.path and parent.path.startswith(category.path):
                        raise ValueError("Cannot create circular hierarchy")

                category.parent_id = reorder_request.new_parent_id
                new_depth = CategoryService._calculate_depth(reorder_request.new_parent_id, session)
                category.depth = new_depth

                # Update path
                if reorder_request.new_parent_id:
                    parent = session.query(Category).filter(
                        Category.id == reorder_request.new_parent_id
                    ).first()
                    new_path = f"{parent.path}{reorder_request.category_id}/"
                else:
                    new_path = f"/{reorder_request.category_id}/"

                category.path = new_path
                CategoryService._update_descendants_path(
                    reorder_request.category_id,
                    new_path,
                    session
                )

            # Update sort order
            category.sort_order = reorder_request.new_sort_order

            session.commit()
            return True

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error reordering category: {str(e)}")
            raise

        except Exception as e:
            session.rollback()
            logger.error(f"Error reordering category: {str(e)}")
            raise

    @staticmethod
    def _update_descendants_path(
        category_id: int,
        new_parent_path: str,
        session: Session
    ) -> None:
        """
        Update path for all descendants of a category

        Args:
            category_id: Category ID
            new_parent_path: New parent path
            session: Database session
        """
        descendants = session.query(Category).filter(
            Category.parent_id == category_id
        ).all()

        for descendant in descendants:
            descendant.path = f"{new_parent_path}{descendant.id}/"
            descendant.depth = new_parent_path.count('/') - 1
            CategoryService._update_descendants_path(descendant.id, descendant.path, session)

    @staticmethod
    def get_category_breadcrumb(
        category_id: int,
        session: Session
    ) -> List[Dict[str, Any]]:
        """
        Get breadcrumb path for a category

        Args:
            category_id: Category ID
            session: Database session

        Returns:
            List of categories from root to target
        """
        try:
            breadcrumb = []
            current_id = category_id

            while current_id:
                category = session.query(Category).filter(
                    Category.id == current_id
                ).first()

                if not category:
                    break

                breadcrumb.insert(0, {
                    "id": category.id,
                    "name": category.category_name,
                    "code": category.category_code
                })

                current_id = category.parent_id

            return breadcrumb

        except Exception as e:
            logger.error(f"Error getting breadcrumb for category {category_id}: {str(e)}")
            raise
