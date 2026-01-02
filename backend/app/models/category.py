"""
Category Models - 게시판 카테고리 관리

테이블 목록:
- Category: 게시판 카테고리 (계층형 구조)

특징:
- 무한 깊이의 계층형 카테고리
- 경로 기반 빠른 조회 (path 컬럼)
- 정렬 순서 관리
- 테넌트별, 게시판별 독립적 관리
- 게시글 수 캐싱

사용법:
    from app.models.category import Category

    # 상위 카테고리
    parent = Category(
        tenant_id=1,
        board_id=1,
        category_name="일반",
        category_code="general",
        depth=0,
        path="/1/",
    )

    # 하위 카테고리
    child = Category(
        tenant_id=1,
        board_id=1,
        parent_id=1,
        category_name="서비스 안내",
        category_code="service_guide",
        depth=1,
        path="/1/2/",
    )
"""

from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Integer,
    Boolean,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from typing import Optional

from app.db.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    """
    게시판 카테고리 (계층형)

    게시판별로 카테고리를 계층적으로 관리.
    드래그앤드롭으로 순서와 계층을 변경할 수 있음.

    계층 구조 예시:
    ```
    공지사항 (depth=0, path=/1/)
    ├── 일반 (depth=1, path=/1/2/)
    │   ├── 서비스 안내 (depth=2, path=/1/2/3/)
    │   └── 점검 안내 (depth=2, path=/1/2/4/)
    ├── 긴급 (depth=1, path=/1/5/)
    └── 이벤트 (depth=1, path=/1/6/)
        ├── 진행중 (depth=2, path=/1/6/7/)
        └── 종료 (depth=2, path=/1/6/8/)
    ```

    Attributes:
        id: 카테고리 ID (PK)
        tenant_id: 테넌트 ID (FK, 멀티테넌트)
        board_id: 게시판 ID (FK, 외부 참조)
        parent_id: 상위 카테고리 ID (FK, NULL이면 최상위)
        depth: 깊이 (0=최상위, 증가함에 따라 깊어짐)
        path: 경로 (예: /1/2/3/, 빠른 하위 조회용)
        category_name: 카테고리명
        category_code: 카테고리 코드 (시스템용, 게시판 내 유일)
        description: 설명
        sort_order: 정렬 순서 (낮을수록 앞, 같으면 생성순)
        icon: 아이콘 (예: folder, star)
        color: 색상 (HEX, 예: #FF0000)
        read_permission: 읽기 권한 (all/members/admin)
        write_permission: 쓰기 권한 (all/members/admin)
        post_count: 게시글 수 (캐시, 게시글 추가/삭제 시 동기화)
        created_at: 생성일시
        created_by: 생성자
        updated_at: 수정일시
        updated_by: 수정자
        is_active: 활성 여부
        is_deleted: 소프트 삭제 여부
    """

    __tablename__ = "categories"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # 테넌트 (멀티사이트)
    tenant_id = Column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="테넌트 ID",
    )

    # 게시판
    board_id = Column(
        BigInteger,
        nullable=False,
        index=True,
        comment="게시판 ID (외부 참조)",
    )

    # 계층 구조
    parent_id = Column(
        BigInteger,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="상위 카테고리 ID (NULL이면 최상위)",
    )

    depth = Column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        comment="깊이 (0=최상위)",
    )

    path = Column(
        String(500),
        nullable=True,
        index=True,
        comment="경로 (예: /1/2/3/, 빠른 하위 조회용)",
    )

    # 기본 정보
    category_name = Column(
        String(100),
        nullable=False,
        comment="카테고리명",
    )

    category_code = Column(
        String(50),
        nullable=False,
        comment="카테고리 코드 (시스템용)",
    )

    description = Column(
        Text,
        nullable=True,
        comment="설명",
    )

    # 표시 설정
    sort_order = Column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        comment="정렬 순서 (낮을수록 앞)",
    )

    icon = Column(
        String(50),
        nullable=True,
        comment="아이콘 (예: folder, star)",
    )

    color = Column(
        String(20),
        nullable=True,
        comment="색상 (HEX, 예: #FF0000)",
    )

    # 권한 설정
    read_permission = Column(
        String(50),
        default="all",
        nullable=False,
        comment="읽기 권한 (all/members/admin)",
    )

    write_permission = Column(
        String(50),
        default="all",
        nullable=False,
        comment="쓰기 권한 (all/members/admin)",
    )

    # 게시글 수 캐시
    post_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="게시글 수 (캐시)",
    )

    # 복합 고유 제약 (게시판 내에서 category_code는 유일해야 함)
    __table_args__ = (
        UniqueConstraint(
            "board_id",
            "category_code",
            name="uk_board_category_code",
        ),
        Index(
            "idx_tenant_board",
            "tenant_id",
            "board_id",
        ),
        Index(
            "idx_path_search",
            "path",
        ),
    )

    # 관계
    parent = relationship(
        "Category",
        remote_side=[id],
        backref="children",
        foreign_keys=[parent_id],
    )

    def __repr__(self) -> str:
        return (
            f"<Category(id={self.id}, code={self.category_code}, "
            f"name={self.category_name}, depth={self.depth})>"
        )
