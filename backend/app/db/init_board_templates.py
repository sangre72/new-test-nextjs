"""
Initialize Board Templates
Creates sample board configurations for different types (notice, free, qna, faq, gallery, review)
"""
from sqlalchemy.orm import Session
from app.models.board import BoardExtended, BoardCategory, BoardTypeEnum, PermissionLevelEnum
from app.models.shared import Tenant
import logging

logger = logging.getLogger(__name__)


BOARD_TEMPLATES = [
    {
        "board_code": "notice",
        "board_name": "공지사항",
        "description": "중요한 공지사항을 확인하세요",
        "board_type": BoardTypeEnum.NOTICE,
        "read_permission": PermissionLevelEnum.PUBLIC,
        "write_permission": PermissionLevelEnum.ADMIN,
        "comment_permission": PermissionLevelEnum.MEMBER,
        "enable_categories": True,
        "enable_secret_post": False,
        "enable_attachments": True,
        "enable_likes": True,
        "enable_comments": True,
        "display_order": 1,
        "settings": {
            "posts_per_page": 20,
            "max_file_size": 10485760,  # 10MB
            "allowed_extensions": ["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"],
            "show_author": True,
            "show_view_count": True
        },
        "categories": [
            {"category_code": "system", "category_name": "시스템", "color": "#ff6b6b", "display_order": 1},
            {"category_code": "update", "category_name": "업데이트", "color": "#4ecdc4", "display_order": 2},
            {"category_code": "event", "category_name": "이벤트", "color": "#45b7d1", "display_order": 3}
        ]
    },
    {
        "board_code": "free",
        "board_name": "자유게시판",
        "description": "자유롭게 이야기를 나누세요",
        "board_type": BoardTypeEnum.FREE,
        "read_permission": PermissionLevelEnum.PUBLIC,
        "write_permission": PermissionLevelEnum.MEMBER,
        "comment_permission": PermissionLevelEnum.MEMBER,
        "enable_categories": True,
        "enable_secret_post": True,
        "enable_attachments": True,
        "enable_likes": True,
        "enable_comments": True,
        "display_order": 2,
        "settings": {
            "posts_per_page": 20,
            "max_file_size": 5242880,  # 5MB
            "allowed_extensions": ["jpg", "jpeg", "png", "gif"],
            "show_author": True,
            "show_view_count": True
        },
        "categories": [
            {"category_code": "general", "category_name": "일반", "color": "#95e1d3", "display_order": 1},
            {"category_code": "humor", "category_name": "유머", "color": "#f38181", "display_order": 2},
            {"category_code": "info", "category_name": "정보", "color": "#aa96da", "display_order": 3}
        ]
    },
    {
        "board_code": "qna",
        "board_name": "Q&A",
        "description": "궁금한 점을 질문하고 답변을 받으세요",
        "board_type": BoardTypeEnum.QNA,
        "read_permission": PermissionLevelEnum.PUBLIC,
        "write_permission": PermissionLevelEnum.MEMBER,
        "comment_permission": PermissionLevelEnum.MEMBER,
        "enable_categories": True,
        "enable_secret_post": False,
        "enable_attachments": True,
        "enable_likes": True,
        "enable_comments": True,
        "display_order": 3,
        "settings": {
            "posts_per_page": 20,
            "max_file_size": 5242880,  # 5MB
            "allowed_extensions": ["jpg", "jpeg", "png", "gif", "pdf"],
            "show_author": True,
            "show_view_count": True,
            "enable_answer_selection": True
        },
        "categories": [
            {"category_code": "technical", "category_name": "기술", "color": "#6c5ce7", "display_order": 1},
            {"category_code": "general", "category_name": "일반", "color": "#00b894", "display_order": 2},
            {"category_code": "feature", "category_name": "기능", "color": "#fdcb6e", "display_order": 3}
        ]
    },
    {
        "board_code": "faq",
        "board_name": "FAQ",
        "description": "자주 묻는 질문과 답변",
        "board_type": BoardTypeEnum.FAQ,
        "read_permission": PermissionLevelEnum.PUBLIC,
        "write_permission": PermissionLevelEnum.ADMIN,
        "comment_permission": PermissionLevelEnum.DISABLED,
        "enable_categories": True,
        "enable_secret_post": False,
        "enable_attachments": False,
        "enable_likes": False,
        "enable_comments": False,
        "display_order": 4,
        "settings": {
            "posts_per_page": 50,
            "show_author": False,
            "show_view_count": False,
            "accordion_style": True
        },
        "categories": [
            {"category_code": "account", "category_name": "계정", "color": "#e17055", "display_order": 1},
            {"category_code": "payment", "category_name": "결제", "color": "#00b894", "display_order": 2},
            {"category_code": "service", "category_name": "서비스", "color": "#0984e3", "display_order": 3}
        ]
    },
    {
        "board_code": "gallery",
        "board_name": "갤러리",
        "description": "사진과 이미지를 공유하세요",
        "board_type": BoardTypeEnum.GALLERY,
        "read_permission": PermissionLevelEnum.PUBLIC,
        "write_permission": PermissionLevelEnum.MEMBER,
        "comment_permission": PermissionLevelEnum.MEMBER,
        "enable_categories": True,
        "enable_secret_post": False,
        "enable_attachments": True,
        "enable_likes": True,
        "enable_comments": True,
        "display_order": 5,
        "settings": {
            "posts_per_page": 12,
            "max_file_size": 10485760,  # 10MB
            "allowed_extensions": ["jpg", "jpeg", "png", "gif"],
            "show_author": True,
            "show_view_count": True,
            "grid_columns": 3,
            "generate_thumbnails": True,
            "thumbnail_size": [300, 300]
        },
        "categories": [
            {"category_code": "photo", "category_name": "사진", "color": "#74b9ff", "display_order": 1},
            {"category_code": "artwork", "category_name": "작품", "color": "#a29bfe", "display_order": 2},
            {"category_code": "nature", "category_name": "자연", "color": "#55efc4", "display_order": 3}
        ]
    },
    {
        "board_code": "review",
        "board_name": "후기게시판",
        "description": "이용 후기를 남겨주세요",
        "board_type": BoardTypeEnum.REVIEW,
        "read_permission": PermissionLevelEnum.PUBLIC,
        "write_permission": PermissionLevelEnum.MEMBER,
        "comment_permission": PermissionLevelEnum.MEMBER,
        "enable_categories": True,
        "enable_secret_post": False,
        "enable_attachments": True,
        "enable_likes": True,
        "enable_comments": True,
        "display_order": 6,
        "settings": {
            "posts_per_page": 20,
            "max_file_size": 5242880,  # 5MB
            "allowed_extensions": ["jpg", "jpeg", "png", "gif"],
            "show_author": True,
            "show_view_count": True,
            "enable_rating": True,
            "rating_required": True
        },
        "categories": [
            {"category_code": "product", "category_name": "제품", "color": "#fab1a0", "display_order": 1},
            {"category_code": "service", "category_name": "서비스", "color": "#81ecec", "display_order": 2},
            {"category_code": "support", "category_name": "고객지원", "color": "#ffeaa7", "display_order": 3}
        ]
    }
]


def init_board_templates(db: Session, tenant_id: int, created_by: str = "system") -> None:
    """
    Initialize board templates for a tenant

    Args:
        db: Database session
        tenant_id: Tenant ID
        created_by: Creator identifier
    """
    try:
        # Check if tenant exists
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            logger.error(f"Tenant {tenant_id} not found")
            return

        logger.info(f"Initializing board templates for tenant {tenant_id}")

        for template in BOARD_TEMPLATES:
            # Check if board already exists
            existing = db.query(BoardExtended).filter(
                BoardExtended.tenant_id == tenant_id,
                BoardExtended.board_code == template["board_code"],
                BoardExtended.is_deleted == False
            ).first()

            if existing:
                logger.info(f"Board '{template['board_code']}' already exists, skipping")
                continue

            # Extract categories
            categories_data = template.pop("categories", [])

            # Create board
            board = BoardExtended(
                tenant_id=tenant_id,
                **template,
                created_by=created_by,
                updated_by=created_by
            )

            db.add(board)
            db.flush()  # Flush to get board.id

            # Create categories
            for cat_data in categories_data:
                category = BoardCategory(
                    board_id=board.id,
                    tenant_id=tenant_id,
                    **cat_data,
                    created_by=created_by,
                    updated_by=created_by
                )
                db.add(category)

            logger.info(f"Created board: {board.board_code} with {len(categories_data)} categories")

        db.commit()
        logger.info("Board templates initialization completed")

    except Exception as e:
        db.rollback()
        logger.error(f"Error initializing board templates: {str(e)}")
        raise


def init_board_templates_for_all_tenants(db: Session) -> None:
    """
    Initialize board templates for all active tenants

    Args:
        db: Database session
    """
    try:
        tenants = db.query(Tenant).filter(
            Tenant.is_active == True,
            Tenant.is_deleted == False
        ).all()

        for tenant in tenants:
            logger.info(f"Initializing boards for tenant: {tenant.tenant_code}")
            init_board_templates(db, tenant.id, "system")

        logger.info(f"Initialized boards for {len(tenants)} tenants")

    except Exception as e:
        logger.error(f"Error initializing boards for all tenants: {str(e)}")
        raise


if __name__ == "__main__":
    """
    Run this script to initialize board templates

    Usage:
        python -m app.db.init_board_templates
    """
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        init_board_templates_for_all_tenants(db)
    finally:
        db.close()
