"""
Category Management API Endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryTreeResponse,
    CategoryReorderRequest,
)
from app.services.category import CategoryService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/board/{board_id}/tree", response_model=List[CategoryTreeResponse])
def get_categories_tree(
    board_id: int,
    tenant_id: int = Query(..., description="Tenant ID"),
    include_inactive: bool = Query(False),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get categories in hierarchical tree structure

    Args:
        board_id: Board ID
        tenant_id: Tenant ID
        include_inactive: Include inactive categories
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of categories in tree structure
    """
    try:
        # Verify user has access to tenant
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        categories = CategoryService.get_categories_tree(
            board_id=board_id,
            tenant_id=tenant_id,
            session=db,
            include_inactive=include_inactive
        )

        return categories

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error getting categories tree: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/board/{board_id}/flat", response_model=List[CategoryResponse])
def get_categories_flat(
    board_id: int,
    tenant_id: int = Query(..., description="Tenant ID"),
    include_inactive: bool = Query(False),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get categories as flat list

    Args:
        board_id: Board ID
        tenant_id: Tenant ID
        include_inactive: Include inactive categories
        current_user: Current authenticated user
        db: Database session

    Returns:
        Flat list of categories
    """
    try:
        # Verify user has access to tenant
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        categories = CategoryService.get_categories_flat(
            board_id=board_id,
            tenant_id=tenant_id,
            session=db,
            include_inactive=include_inactive
        )

        return categories

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error getting categories flat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    tenant_id: int = Query(..., description="Tenant ID"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single category by ID

    Args:
        category_id: Category ID
        tenant_id: Tenant ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Category response
    """
    try:
        # Verify user has access to tenant
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        category = CategoryService.get_category_by_id(
            category_id=category_id,
            tenant_id=tenant_id,
            session=db
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        return category

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error getting category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_create: CategoryCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new category

    Args:
        category_create: Category creation schema
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created category response
    """
    try:
        # Verify user has access to tenant and has admin/manager role
        if current_user.get("tenant_id") != category_create.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        # Check for admin/manager role (implementation depends on your auth setup)
        # For now, we'll allow all authenticated users to create categories
        # Modify based on your role-based access control

        created_by = current_user.get("user_id") or current_user.get("username")
        category = CategoryService.create_category(
            category_create=category_create,
            created_by=created_by,
            session=db
        )

        return category

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    tenant_id: int = Query(..., description="Tenant ID"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a category

    Args:
        category_id: Category ID to update
        category_update: Category update schema
        tenant_id: Tenant ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated category response
    """
    try:
        # Verify user has access to tenant
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        updated_by = current_user.get("user_id") or current_user.get("username")
        category = CategoryService.update_category(
            category_id=category_id,
            tenant_id=tenant_id,
            category_update=category_update,
            updated_by=updated_by,
            session=db
        )

        return category

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error updating category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    tenant_id: int = Query(..., description="Tenant ID"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete (soft delete) a category

    Args:
        category_id: Category ID to delete
        tenant_id: Tenant ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        No content
    """
    try:
        # Verify user has access to tenant
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        CategoryService.delete_category(
            category_id=category_id,
            tenant_id=tenant_id,
            session=db
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/reorder", status_code=status.HTTP_204_NO_CONTENT)
def reorder_categories(
    reorder_request: CategoryReorderRequest,
    tenant_id: int = Query(..., description="Tenant ID"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reorder categories (drag and drop support)

    Args:
        reorder_request: Reorder request with category_id, new_parent_id, new_sort_order
        tenant_id: Tenant ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        No content
    """
    try:
        # Verify user has access to tenant
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        CategoryService.reorder_categories(
            reorder_request=reorder_request,
            tenant_id=tenant_id,
            session=db
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error reordering categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{category_id}/breadcrumb")
def get_category_breadcrumb(
    category_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get breadcrumb path for a category

    Args:
        category_id: Category ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of categories from root to target
    """
    try:
        breadcrumb = CategoryService.get_category_breadcrumb(
            category_id=category_id,
            session=db
        )

        return {"breadcrumb": breadcrumb}

    except Exception as e:
        logger.error(f"Error getting breadcrumb for category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
