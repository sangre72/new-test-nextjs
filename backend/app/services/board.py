"""
Board Service Layer
Business logic for board operations
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from fastapi import HTTPException, status
import logging

from app.models.board import (
    BoardExtended, BoardCategory, BoardPost, BoardComment,
    BoardAttachment, BoardLike, PostStatusEnum, CommentStatusEnum
)
from app.models.shared import User
from app.schemas.board import (
    BoardCreate, BoardUpdate, BoardResponse,
    BoardCategoryCreate, BoardCategoryUpdate,
    BoardPostCreate, BoardPostUpdate, BoardPostListRequest,
    BoardCommentCreate, BoardCommentUpdate,
    BoardAttachmentCreate,
)

logger = logging.getLogger(__name__)


class BoardService:
    """Service for board operations"""

    @staticmethod
    def get_boards(
        tenant_id: int,
        session: Session,
        include_inactive: bool = False
    ) -> List[BoardExtended]:
        """Get all boards for a tenant"""
        try:
            query = session.query(BoardExtended).filter(
                BoardExtended.tenant_id == tenant_id,
                BoardExtended.is_deleted == False
            )

            if not include_inactive:
                query = query.filter(BoardExtended.is_active == True)

            boards = query.order_by(BoardExtended.display_order, BoardExtended.created_at).all()
            return boards

        except Exception as e:
            logger.error(f"Error getting boards: {str(e)}")
            raise

    @staticmethod
    def get_board_by_id(
        board_id: int,
        tenant_id: int,
        session: Session
    ) -> Optional[BoardExtended]:
        """Get board by ID"""
        try:
            board = session.query(BoardExtended).filter(
                BoardExtended.id == board_id,
                BoardExtended.tenant_id == tenant_id,
                BoardExtended.is_deleted == False
            ).first()

            return board

        except Exception as e:
            logger.error(f"Error getting board {board_id}: {str(e)}")
            raise

    @staticmethod
    def get_board_by_code(
        board_code: str,
        tenant_id: int,
        session: Session
    ) -> Optional[BoardExtended]:
        """Get board by code"""
        try:
            board = session.query(BoardExtended).filter(
                BoardExtended.board_code == board_code,
                BoardExtended.tenant_id == tenant_id,
                BoardExtended.is_deleted == False
            ).first()

            return board

        except Exception as e:
            logger.error(f"Error getting board by code {board_code}: {str(e)}")
            raise

    @staticmethod
    def create_board(
        board_create: BoardCreate,
        created_by: str,
        session: Session
    ) -> BoardExtended:
        """Create a new board"""
        try:
            # Check if board code already exists
            existing = session.query(BoardExtended).filter(
                BoardExtended.board_code == board_create.board_code,
                BoardExtended.tenant_id == board_create.tenant_id,
                BoardExtended.is_deleted == False
            ).first()

            if existing:
                raise ValueError(f"Board with code '{board_create.board_code}' already exists")

            # Create board
            board = BoardExtended(
                **board_create.model_dump(),
                created_by=created_by,
                updated_by=created_by
            )

            session.add(board)
            session.commit()
            session.refresh(board)

            logger.info(f"Created board: {board.id} ({board.board_code})")
            return board

        except ValueError:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating board: {str(e)}")
            raise

    @staticmethod
    def update_board(
        board_id: int,
        tenant_id: int,
        board_update: BoardUpdate,
        updated_by: str,
        session: Session
    ) -> BoardExtended:
        """Update a board"""
        try:
            board = BoardService.get_board_by_id(board_id, tenant_id, session)
            if not board:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Board not found"
                )

            # Update fields
            update_data = board_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(board, field, value)

            board.updated_by = updated_by

            session.commit()
            session.refresh(board)

            logger.info(f"Updated board: {board.id}")
            return board

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating board {board_id}: {str(e)}")
            raise

    @staticmethod
    def delete_board(
        board_id: int,
        tenant_id: int,
        session: Session
    ) -> None:
        """Delete (soft delete) a board"""
        try:
            board = BoardService.get_board_by_id(board_id, tenant_id, session)
            if not board:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Board not found"
                )

            board.is_deleted = True
            session.commit()

            logger.info(f"Deleted board: {board.id}")

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting board {board_id}: {str(e)}")
            raise


class BoardCategoryService:
    """Service for board category operations"""

    @staticmethod
    def get_categories(
        board_id: int,
        tenant_id: int,
        session: Session,
        include_inactive: bool = False
    ) -> List[BoardCategory]:
        """Get all categories for a board"""
        try:
            query = session.query(BoardCategory).filter(
                BoardCategory.board_id == board_id,
                BoardCategory.tenant_id == tenant_id,
                BoardCategory.is_deleted == False
            )

            if not include_inactive:
                query = query.filter(BoardCategory.is_active == True)

            categories = query.order_by(BoardCategory.display_order).all()
            return categories

        except Exception as e:
            logger.error(f"Error getting categories for board {board_id}: {str(e)}")
            raise

    @staticmethod
    def create_category(
        category_create: BoardCategoryCreate,
        created_by: str,
        session: Session
    ) -> BoardCategory:
        """Create a new category"""
        try:
            # Check if category code already exists in this board
            existing = session.query(BoardCategory).filter(
                BoardCategory.board_id == category_create.board_id,
                BoardCategory.category_code == category_create.category_code,
                BoardCategory.is_deleted == False
            ).first()

            if existing:
                raise ValueError(f"Category with code '{category_create.category_code}' already exists in this board")

            category = BoardCategory(
                **category_create.model_dump(),
                created_by=created_by,
                updated_by=created_by
            )

            session.add(category)
            session.commit()
            session.refresh(category)

            logger.info(f"Created category: {category.id}")
            return category

        except ValueError:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating category: {str(e)}")
            raise


class BoardPostService:
    """Service for board post operations"""

    @staticmethod
    def get_posts(
        board_id: int,
        tenant_id: int,
        request: BoardPostListRequest,
        session: Session,
        user_id: Optional[int] = None
    ) -> Tuple[List[BoardPost], int]:
        """Get posts with pagination and filtering"""
        try:
            # Base query
            query = session.query(BoardPost).filter(
                BoardPost.board_id == board_id,
                BoardPost.tenant_id == tenant_id,
                BoardPost.is_deleted == False
            )

            # Filter by status
            if request.status:
                query = query.filter(BoardPost.status == request.status)
            else:
                query = query.filter(BoardPost.status == PostStatusEnum.PUBLISHED)

            # Filter by category
            if request.category_id:
                query = query.filter(BoardPost.category_id == request.category_id)

            # Search
            if request.search:
                search_term = f"%{request.search}%"
                query = query.filter(
                    or_(
                        BoardPost.title.ilike(search_term),
                        BoardPost.content.ilike(search_term)
                    )
                )

            # Get total count
            total = query.count()

            # Sort
            if request.sort_by == "created_at":
                order_col = BoardPost.created_at
            elif request.sort_by == "view_count":
                order_col = BoardPost.view_count
            elif request.sort_by == "like_count":
                order_col = BoardPost.like_count
            else:
                order_col = BoardPost.created_at

            if request.sort_order == "asc":
                query = query.order_by(asc(order_col))
            else:
                query = query.order_by(desc(order_col))

            # Always show pinned posts first
            query = query.order_by(desc(BoardPost.is_pinned), desc(BoardPost.is_notice))

            # Pagination
            offset = (request.page - 1) * request.page_size
            query = query.offset(offset).limit(request.page_size)

            # Execute with joins for performance
            posts = query.options(
                joinedload(BoardPost.author),
                joinedload(BoardPost.category)
            ).all()

            return posts, total

        except Exception as e:
            logger.error(f"Error getting posts: {str(e)}")
            raise

    @staticmethod
    def get_post_by_id(
        post_id: int,
        board_id: int,
        tenant_id: int,
        session: Session,
        increment_view: bool = False
    ) -> Optional[BoardPost]:
        """Get post by ID"""
        try:
            post = session.query(BoardPost).options(
                joinedload(BoardPost.author),
                joinedload(BoardPost.category),
                joinedload(BoardPost.attachments),
                joinedload(BoardPost.comments)
            ).filter(
                BoardPost.id == post_id,
                BoardPost.board_id == board_id,
                BoardPost.tenant_id == tenant_id,
                BoardPost.is_deleted == False
            ).first()

            if post and increment_view:
                post.view_count += 1
                session.commit()

            return post

        except Exception as e:
            logger.error(f"Error getting post {post_id}: {str(e)}")
            raise

    @staticmethod
    def create_post(
        post_create: BoardPostCreate,
        author_id: int,
        created_by: str,
        session: Session
    ) -> BoardPost:
        """Create a new post"""
        try:
            post = BoardPost(
                **post_create.model_dump(),
                author_id=author_id,
                status=PostStatusEnum.PUBLISHED,
                created_by=created_by,
                updated_by=created_by
            )

            session.add(post)

            # Update board statistics
            board = session.query(BoardExtended).filter(
                BoardExtended.id == post_create.board_id
            ).first()
            if board:
                board.total_posts += 1

            session.commit()
            session.refresh(post)

            logger.info(f"Created post: {post.id}")
            return post

        except Exception as e:
            session.rollback()
            logger.error(f"Error creating post: {str(e)}")
            raise

    @staticmethod
    def update_post(
        post_id: int,
        board_id: int,
        tenant_id: int,
        author_id: int,
        post_update: BoardPostUpdate,
        updated_by: str,
        session: Session,
        is_admin: bool = False
    ) -> BoardPost:
        """Update a post"""
        try:
            post = BoardPostService.get_post_by_id(post_id, board_id, tenant_id, session)
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found"
                )

            # Check permission
            if not is_admin and post.author_id != author_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to edit this post"
                )

            # Update fields
            update_data = post_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(post, field, value)

            post.updated_by = updated_by

            session.commit()
            session.refresh(post)

            logger.info(f"Updated post: {post.id}")
            return post

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating post {post_id}: {str(e)}")
            raise

    @staticmethod
    def delete_post(
        post_id: int,
        board_id: int,
        tenant_id: int,
        author_id: int,
        session: Session,
        is_admin: bool = False
    ) -> None:
        """Delete (soft delete) a post"""
        try:
            post = BoardPostService.get_post_by_id(post_id, board_id, tenant_id, session)
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found"
                )

            # Check permission
            if not is_admin and post.author_id != author_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to delete this post"
                )

            post.is_deleted = True
            post.status = PostStatusEnum.DELETED

            # Update board statistics
            board = session.query(BoardExtended).filter(
                BoardExtended.id == board_id
            ).first()
            if board and board.total_posts > 0:
                board.total_posts -= 1

            session.commit()

            logger.info(f"Deleted post: {post.id}")

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting post {post_id}: {str(e)}")
            raise


class BoardCommentService:
    """Service for board comment operations"""

    @staticmethod
    def get_comments(
        post_id: int,
        session: Session,
        include_deleted: bool = False
    ) -> List[BoardComment]:
        """Get all comments for a post"""
        try:
            query = session.query(BoardComment).options(
                joinedload(BoardComment.author)
            ).filter(
                BoardComment.post_id == post_id,
                BoardComment.is_deleted == False
            )

            if not include_deleted:
                query = query.filter(BoardComment.status != CommentStatusEnum.DELETED)

            comments = query.order_by(BoardComment.created_at).all()
            return comments

        except Exception as e:
            logger.error(f"Error getting comments for post {post_id}: {str(e)}")
            raise

    @staticmethod
    def create_comment(
        comment_create: BoardCommentCreate,
        author_id: int,
        created_by: str,
        session: Session
    ) -> BoardComment:
        """Create a new comment"""
        try:
            comment = BoardComment(
                **comment_create.model_dump(),
                author_id=author_id,
                status=CommentStatusEnum.PUBLISHED,
                created_by=created_by,
                updated_by=created_by
            )

            session.add(comment)

            # Update post comment count
            post = session.query(BoardPost).filter(
                BoardPost.id == comment_create.post_id
            ).first()
            if post:
                post.comment_count += 1

            session.commit()
            session.refresh(comment)

            logger.info(f"Created comment: {comment.id}")
            return comment

        except Exception as e:
            session.rollback()
            logger.error(f"Error creating comment: {str(e)}")
            raise


class BoardLikeService:
    """Service for board like operations"""

    @staticmethod
    def toggle_like(
        post_id: int,
        user_id: int,
        tenant_id: int,
        session: Session
    ) -> Tuple[bool, int]:
        """Toggle like on a post. Returns (is_liked, new_like_count)"""
        try:
            # Check if already liked
            existing = session.query(BoardLike).filter(
                BoardLike.post_id == post_id,
                BoardLike.user_id == user_id
            ).first()

            post = session.query(BoardPost).filter(
                BoardPost.id == post_id
            ).first()

            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found"
                )

            if existing:
                # Unlike
                session.delete(existing)
                post.like_count = max(0, post.like_count - 1)
                is_liked = False
            else:
                # Like
                like = BoardLike(
                    post_id=post_id,
                    user_id=user_id,
                    tenant_id=tenant_id
                )
                session.add(like)
                post.like_count += 1
                is_liked = True

            session.commit()

            logger.info(f"Toggled like on post {post_id} by user {user_id}: {is_liked}")
            return is_liked, post.like_count

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error toggling like: {str(e)}")
            raise
