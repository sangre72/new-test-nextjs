"""
Database Base Classes

SQLAlchemy 2.0 선언형 베이스와 공통 Mixin 정의

사용법:
    from app.db.base import Base, TimestampMixin

    class User(Base, TimestampMixin):
        __tablename__ = "users"
        id = Column(BigInteger, primary_key=True)
        name = Column(String(100))
"""

from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

# SQLAlchemy 2.0 선언형 베이스
Base = declarative_base()


class TimestampMixin:
    """
    모든 테이블에 공통으로 사용되는 감사(Audit) 컬럼

    필수 감사 컬럼:
    - created_at: 생성일시
    - created_by: 생성자
    - updated_at: 수정일시
    - updated_by: 수정자
    - is_active: 활성 여부
    - is_deleted: 소프트 삭제 여부

    사용 예시:
        class User(Base, TimestampMixin):
            __tablename__ = "users"
            id = Column(BigInteger, primary_key=True)
            name = Column(String(100))

    데이터베이스 구조:
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        created_by VARCHAR(100)
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        updated_by VARCHAR(100)
        is_active BOOLEAN DEFAULT TRUE
        is_deleted BOOLEAN DEFAULT FALSE

    설명:
    - is_active: 엔티티의 활성 상태 (비활성화 시 조회 제외)
    - is_deleted: 소프트 삭제 (물리적 삭제 대신 논리적 삭제)
    """

    # 생성일시 (서버 기본값: 현재시간)
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="생성일시",
    )

    # 생성자 (애플리케이션에서 설정)
    created_by = Column(
        String(100),
        nullable=True,
        comment="생성자 ID 또는 이름",
    )

    # 수정일시 (서버 기본값: 현재시간, 수정 시 자동 업데이트)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="수정일시",
    )

    # 수정자 (애플리케이션에서 설정)
    updated_by = Column(
        String(100),
        nullable=True,
        comment="수정자 ID 또는 이름",
    )

    # 활성 여부 (기본: True)
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="활성 여부",
    )

    # 소프트 삭제 여부 (기본: False)
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="소프트 삭제 여부",
    )
