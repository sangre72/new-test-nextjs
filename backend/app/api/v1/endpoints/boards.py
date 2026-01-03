"""
Board Management API Endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.board import (
    BoardCreate, BoardUpdate, BoardResponse,
    BoardCategoryCreate, BoardCategoryUpdate, BoardCategoryResponse,
    BoardPostCreate, BoardPostUpdate, BoardPostListResponse, BoardPostDetailResponse,
    BoardPostListRequest, BoardPostListPaginated,
    BoardCommentCreate, BoardCommentUpdate, BoardCommentResponse,
    BoardLikeCreate, BoardLikeResponse,
)
from app.services.board import (
    BoardService, BoardCategoryService, BoardPostService,
    BoardCommentService, BoardLikeService
)
from app.models.shared import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/boards", tags=["Boards"])


# ========== Board Management ==========

@router.get("/", response_model=List[BoardResponse])
def get_boards(
    tenant_id: int = Query(..., description="Tenant ID"),
    include_inactive: bool = Query(False),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all boards for a tenant

    Args:
        tenant_id: Tenant ID
        include_inactive: Include inactive boards
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of boards
    """
    try:
        # Verify user has access to tenant
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        boards = BoardService.get_boards(
            tenant_id=tenant_id,
            session=db,
            include_inactive=include_inactive
        )

        return boards

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting boards: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{board_code}", response_model=BoardResponse)
def get_board(
    board_code: str,
    tenant_id: int = Query(..., description="Tenant ID"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a board by code

    Args:
        board_code: Board code
        tenant_id: Tenant ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Board response
    """
    try:
        # Verify user has access to tenant
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        board = BoardService.get_board_by_code(
            board_code=board_code,
            tenant_id=tenant_id,
            session=db
        )

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found"
            )

        return board

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting board {board_code}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
def create_board(
    board_create: BoardCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new board (admin only)

    Args:
        board_create: Board creation schema
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created board response
    """
    try:
        # Verify user has access to tenant
        if current_user.get("tenant_id") != board_create.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        # Check for admin role (simplified - adjust based on your auth)
        if not current_user.get("is_superuser"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permission required"
            )

        created_by = current_user.get("user_id") or current_user.get("username")
        board = BoardService.create_board(
            board_create=board_create,
            created_by=str(created_by),
            session=db
        )

        return board

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating board: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{board_id}", response_model=BoardResponse)
def update_board(
    board_id: int,
    board_update: BoardUpdate,
    tenant_id: int = Query(..., description="Tenant ID"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a board (admin only)

    Args:
        board_id: Board ID
        board_update: Board update schema
        tenant_id: Tenant ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated board response
    """
    try:
        # Verify user has access to tenant
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        # Check for admin role
        if not current_user.get("is_superuser"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permission required"
            )

        updated_by = current_user.get("user_id") or current_user.get("username")
        board = BoardService.update_board(
            board_id=board_id,
            tenant_id=tenant_id,
            board_update=board_update,
            updated_by=str(updated_by),
            session=db
        )

        return board

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating board {board_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(
    board_id: int,
    tenant_id: int = Query(..., description="Tenant ID"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a board (admin only)

    Args:
        board_id: Board ID
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

        # Check for admin role
        if not current_user.get("is_superuser"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permission required"
            )

        BoardService.delete_board(
            board_id=board_id,
            tenant_id=tenant_id,
            session=db
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting board {board_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ========== Board Categories ==========

@router.get("/{board_id}/categories", response_model=List[BoardCategoryResponse])
def get_board_categories(
    board_id: int,
    tenant_id: int = Query(..., description="Tenant ID"),
    include_inactive: bool = Query(False),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get categories for a board"""
    try:
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        categories = BoardCategoryService.get_categories(
            board_id=board_id,
            tenant_id=tenant_id,
            session=db,
            include_inactive=include_inactive
        )

        return categories

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{board_id}/categories", response_model=BoardCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_board_category(
    board_id: int,
    category_create: BoardCategoryCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a board category (admin only)"""
    try:
        if current_user.get("tenant_id") != category_create.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        if not current_user.get("is_superuser"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permission required"
            )

        # Ensure board_id matches
        category_create.board_id = board_id

        created_by = str(current_user.get("user_id") or current_user.get("username"))
        category = BoardCategoryService.create_category(
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


# ========== Board Posts ==========

@router.get("/{board_code}/posts", response_model=BoardPostListPaginated)
def get_board_posts(
    board_code: str,
    tenant_id: int = Query(..., description="Tenant ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: int = Query(None),
    search: str = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get posts for a board with pagination"""
    try:
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        # Get board
        board = BoardService.get_board_by_code(board_code, tenant_id, db)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found"
            )

        # Check read permission
        # TODO: Implement permission check based on board.read_permission

        # Build request
        request = BoardPostListRequest(
            page=page,
            page_size=page_size,
            category_id=category_id,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )

        posts, total = BoardPostService.get_posts(
            board_id=board.id,
            tenant_id=tenant_id,
            request=request,
            session=db,
            user_id=current_user.get("user_id")
        )

        # Build response
        items = []
        for post in posts:
            items.append(BoardPostListResponse(
                id=post.id,
                board_id=post.board_id,
                category_id=post.category_id,
                category_name=post.category.category_name if post.category else None,
                author_id=post.author_id,
                author_name=post.author.username if post.author else "Unknown",
                title=post.title,
                status=post.status,
                is_secret=post.is_secret,
                is_pinned=post.is_pinned,
                is_notice=post.is_notice,
                is_answered=post.is_answered,
                rating=post.rating,
                view_count=post.view_count,
                like_count=post.like_count,
                comment_count=post.comment_count,
                created_at=post.created_at,
                updated_at=post.updated_at
            ))

        total_pages = (total + page_size - 1) // page_size

        return BoardPostListPaginated(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting posts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{board_code}/posts/{post_id}", response_model=BoardPostDetailResponse)
def get_board_post(
    board_code: str,
    post_id: int,
    tenant_id: int = Query(..., description="Tenant ID"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single post with details"""
    try:
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        # Get board
        board = BoardService.get_board_by_code(board_code, tenant_id, db)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found"
            )

        # Get post (increment view count)
        post = BoardPostService.get_post_by_id(
            post_id=post_id,
            board_id=board.id,
            tenant_id=tenant_id,
            session=db,
            increment_view=True
        )

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        # Check permissions
        user_id = current_user.get("user_id")
        can_edit = post.author_id == user_id or current_user.get("is_superuser", False)
        can_delete = can_edit

        # Check if user has liked
        has_liked = False
        if user_id:
            from app.models.board import BoardLike
            like = db.query(BoardLike).filter(
                BoardLike.post_id == post_id,
                BoardLike.user_id == user_id
            ).first()
            has_liked = like is not None

        # Build response
        response = BoardPostDetailResponse(
            id=post.id,
            board_id=post.board_id,
            tenant_id=post.tenant_id,
            category_id=post.category_id,
            category_name=post.category.category_name if post.category else None,
            author_id=post.author_id,
            author_name=post.author.username if post.author else "Unknown",
            author_email=post.author.email if post.author else None,
            title=post.title,
            content=post.content,
            status=post.status,
            is_secret=post.is_secret,
            is_pinned=post.is_pinned,
            is_notice=post.is_notice,
            is_answered=post.is_answered,
            accepted_answer_id=post.accepted_answer_id,
            rating=post.rating,
            view_count=post.view_count,
            like_count=post.like_count,
            comment_count=post.comment_count,
            metadata=post.metadata,
            published_at=post.published_at,
            created_at=post.created_at,
            created_by=post.created_by,
            updated_at=post.updated_at,
            updated_by=post.updated_by,
            is_active=post.is_active,
            can_edit=can_edit,
            can_delete=can_delete,
            has_liked=has_liked
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting post {post_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{board_code}/posts", response_model=BoardPostDetailResponse, status_code=status.HTTP_201_CREATED)
def create_board_post(
    board_code: str,
    post_create: BoardPostCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new post"""
    try:
        if current_user.get("tenant_id") != post_create.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        # Get board
        board = BoardService.get_board_by_code(board_code, post_create.tenant_id, db)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found"
            )

        # Ensure board_id matches
        post_create.board_id = board.id

        # Check write permission
        # TODO: Implement permission check based on board.write_permission

        user_id = current_user.get("user_id")
        created_by = str(user_id or current_user.get("username"))

        post = BoardPostService.create_post(
            post_create=post_create,
            author_id=user_id,
            created_by=created_by,
            session=db
        )

        # Refresh to get relations
        db.refresh(post)

        # Build response (similar to get_board_post)
        response = BoardPostDetailResponse(
            id=post.id,
            board_id=post.board_id,
            tenant_id=post.tenant_id,
            category_id=post.category_id,
            category_name=post.category.category_name if post.category else None,
            author_id=post.author_id,
            author_name=post.author.username if post.author else "Unknown",
            author_email=post.author.email if post.author else None,
            title=post.title,
            content=post.content,
            status=post.status,
            is_secret=post.is_secret,
            is_pinned=post.is_pinned,
            is_notice=post.is_notice,
            is_answered=post.is_answered,
            accepted_answer_id=post.accepted_answer_id,
            rating=post.rating,
            view_count=post.view_count,
            like_count=post.like_count,
            comment_count=post.comment_count,
            metadata=post.metadata,
            published_at=post.published_at,
            created_at=post.created_at,
            created_by=post.created_by,
            updated_at=post.updated_at,
            updated_by=post.updated_by,
            is_active=post.is_active,
            can_edit=True,
            can_delete=True,
            has_liked=False
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{board_code}/posts/{post_id}", response_model=BoardPostDetailResponse)
def update_board_post(
    board_code: str,
    post_id: int,
    post_update: BoardPostUpdate,
    tenant_id: int = Query(..., description="Tenant ID"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a post"""
    try:
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        # Get board
        board = BoardService.get_board_by_code(board_code, tenant_id, db)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found"
            )

        user_id = current_user.get("user_id")
        updated_by = str(user_id or current_user.get("username"))
        is_admin = current_user.get("is_superuser", False)

        post = BoardPostService.update_post(
            post_id=post_id,
            board_id=board.id,
            tenant_id=tenant_id,
            author_id=user_id,
            post_update=post_update,
            updated_by=updated_by,
            session=db,
            is_admin=is_admin
        )

        # Refresh and build response
        db.refresh(post)

        response = BoardPostDetailResponse(
            id=post.id,
            board_id=post.board_id,
            tenant_id=post.tenant_id,
            category_id=post.category_id,
            category_name=post.category.category_name if post.category else None,
            author_id=post.author_id,
            author_name=post.author.username if post.author else "Unknown",
            author_email=post.author.email if post.author else None,
            title=post.title,
            content=post.content,
            status=post.status,
            is_secret=post.is_secret,
            is_pinned=post.is_pinned,
            is_notice=post.is_notice,
            is_answered=post.is_answered,
            accepted_answer_id=post.accepted_answer_id,
            rating=post.rating,
            view_count=post.view_count,
            like_count=post.like_count,
            comment_count=post.comment_count,
            metadata=post.metadata,
            published_at=post.published_at,
            created_at=post.created_at,
            created_by=post.created_by,
            updated_at=post.updated_at,
            updated_by=post.updated_by,
            is_active=post.is_active,
            can_edit=True,
            can_delete=True,
            has_liked=False
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating post {post_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{board_code}/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board_post(
    board_code: str,
    post_id: int,
    tenant_id: int = Query(..., description="Tenant ID"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a post"""
    try:
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        # Get board
        board = BoardService.get_board_by_code(board_code, tenant_id, db)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found"
            )

        user_id = current_user.get("user_id")
        is_admin = current_user.get("is_superuser", False)

        BoardPostService.delete_post(
            post_id=post_id,
            board_id=board.id,
            tenant_id=tenant_id,
            author_id=user_id,
            session=db,
            is_admin=is_admin
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting post {post_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ========== Post Likes ==========

@router.post("/{board_code}/posts/{post_id}/like")
def toggle_post_like(
    board_code: str,
    post_id: int,
    tenant_id: int = Query(..., description="Tenant ID"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle like on a post"""
    try:
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        is_liked, like_count = BoardLikeService.toggle_like(
            post_id=post_id,
            user_id=user_id,
            tenant_id=tenant_id,
            session=db
        )

        return {
            "is_liked": is_liked,
            "like_count": like_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling like on post {post_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ========== Post Comments ==========

@router.get("/{board_code}/posts/{post_id}/comments", response_model=List[BoardCommentResponse])
def get_post_comments(
    board_code: str,
    post_id: int,
    tenant_id: int = Query(..., description="Tenant ID"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comments for a post"""
    try:
        if current_user.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        comments = BoardCommentService.get_comments(
            post_id=post_id,
            session=db
        )

        # Build tree structure (parent-child)
        comment_map = {}
        root_comments = []

        user_id = current_user.get("user_id")
        is_admin = current_user.get("is_superuser", False)

        for comment in comments:
            can_edit = comment.author_id == user_id or is_admin
            can_delete = can_edit

            comment_response = BoardCommentResponse(
                id=comment.id,
                post_id=comment.post_id,
                tenant_id=comment.tenant_id,
                author_id=comment.author_id,
                author_name=comment.author.username if comment.author else "Unknown",
                parent_id=comment.parent_id,
                content=comment.content,
                status=comment.status,
                is_secret=comment.is_secret,
                is_answer=comment.is_answer,
                like_count=comment.like_count,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                is_active=comment.is_active,
                can_edit=can_edit,
                can_delete=can_delete,
                replies=[]
            )

            comment_map[comment.id] = comment_response

            if comment.parent_id is None:
                root_comments.append(comment_response)

        # Build tree
        for comment in comments:
            if comment.parent_id and comment.parent_id in comment_map:
                parent = comment_map[comment.parent_id]
                parent.replies.append(comment_map[comment.id])

        return root_comments

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting comments for post {post_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{board_code}/posts/{post_id}/comments", response_model=BoardCommentResponse, status_code=status.HTTP_201_CREATED)
def create_post_comment(
    board_code: str,
    post_id: int,
    comment_create: BoardCommentCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a comment on a post"""
    try:
        if current_user.get("tenant_id") != comment_create.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )

        # Ensure post_id matches
        comment_create.post_id = post_id

        user_id = current_user.get("user_id")
        created_by = str(user_id or current_user.get("username"))

        comment = BoardCommentService.create_comment(
            comment_create=comment_create,
            author_id=user_id,
            created_by=created_by,
            session=db
        )

        # Refresh to get author relation
        db.refresh(comment)

        response = BoardCommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            tenant_id=comment.tenant_id,
            author_id=comment.author_id,
            author_name=comment.author.username if comment.author else "Unknown",
            parent_id=comment.parent_id,
            content=comment.content,
            status=comment.status,
            is_secret=comment.is_secret,
            is_answer=comment.is_answer,
            like_count=comment.like_count,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            is_active=comment.is_active,
            can_edit=True,
            can_delete=True,
            replies=[]
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating comment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
