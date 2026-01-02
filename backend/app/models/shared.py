"""
Shared Models - 모든 에이전트가 공통으로 사용하는 테이블 정의

테이블 목록:
- Tenant: 테넌트 (멀티사이트)
- UserGroup: 사용자 그룹
- UserGroupMember: 사용자-그룹 매핑
- Role: 역할
- UserRole: 사용자-역할 매핑
"""

from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Boolean,
    Integer,
    Enum,
    ForeignKey,
    DateTime,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from typing import Optional
import enum

from app.db.base import Base, TimestampMixin


# ============================================================
# 1. Tenant (테넌트/사이트)
# ============================================================
class Tenant(Base, TimestampMixin):
    """
    테넌트 (멀티사이트 아키텍처)

    여러 사이트/조직을 하나의 시스템에서 독립적으로 운영할 수 있도록 함.
    다른 테이블들이 tenant_id를 참조하여 테넌트별 데이터 분리.

    테넌트 식별 방식:
    - 서브도메인: siteA.example.com, siteB.example.com
    - 커스텀 도메인: siteA.com, siteB.com
    - 경로: example.com/siteA, example.com/siteB
    - 헤더: X-Tenant-ID 헤더

    Attributes:
        id: 테넌트 ID (PK)
        tenant_code: 테넌트 코드 (고유, 시스템 식별용)
        tenant_name: 테넌트명 (사이트명)
        description: 설명
        domain: 커스텀 도메인 (예: siteA.com)
        subdomain: 서브도메인 (예: siteA)
        settings: JSON 설정 (theme, logo, language 등)
        admin_email: 관리자 이메일
        admin_name: 관리자 이름
        is_active: 활성 여부
        is_deleted: 소프트 삭제 여부
    """

    __tablename__ = "tenants"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # 기본 정보
    tenant_code = Column(String(50), nullable=False, unique=True, index=True)
    tenant_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # 도메인 설정
    domain = Column(String(255), nullable=True, index=True)  # 커스텀 도메인
    subdomain = Column(String(100), nullable=True, index=True)  # 서브도메인

    # 설정 (JSON)
    settings = Column(JSON, nullable=True)
    # {
    #   "theme": "default",
    #   "logo": "/uploads/logo.png",
    #   "language": "ko",
    #   "timezone": "Asia/Seoul"
    # }

    # 연락처
    admin_email = Column(String(255), nullable=True)
    admin_name = Column(String(100), nullable=True)

    # 관계
    user_groups = relationship("UserGroup", back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, code={self.tenant_code}, name={self.tenant_name})>"


# ============================================================
# 2. UserGroup (사용자 그룹)
# ============================================================
class GroupTypeEnum(str, enum.Enum):
    """그룹 타입"""
    SYSTEM = "system"  # 시스템 기본 그룹 (수정 불가)
    CUSTOM = "custom"  # 관리자 생성 그룹


class UserGroup(Base, TimestampMixin):
    """
    사용자 그룹

    사용자들을 그룹으로 관리하여 권한, 콘텐츠 접근 등을 제어.
    테넌트별로 독립적인 그룹을 유지할 수 있음.

    기본 그룹:
    - all_members: 전체 회원
    - regular: 일반 회원
    - vip: VIP 회원
    - premium: 프리미엄 회원

    Attributes:
        id: 그룹 ID (PK)
        tenant_id: 테넌트 ID (FK, 선택사항)
        group_name: 그룹명
        group_code: 그룹 코드 (시스템 식별용, 테넌트별 고유)
        description: 설명
        priority: 우선순위 (높을수록 상위)
        group_type: 그룹 타입 (system/custom)
        is_active: 활성 여부
        is_deleted: 소프트 삭제 여부
    """

    __tablename__ = "user_groups"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # 테넌트 (멀티사이트)
    tenant_id = Column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # 기본 정보
    group_name = Column(String(100), nullable=False)
    group_code = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # 그룹 설정
    priority = Column(Integer, default=0, index=True)
    group_type = Column(Enum(GroupTypeEnum), default=GroupTypeEnum.CUSTOM, nullable=False)

    # 관계
    tenant = relationship("Tenant", back_populates="user_groups")
    members = relationship("UserGroupMember", back_populates="group", cascade="all, delete-orphan")

    # 복합 고유 제약 (테넌트별로 동일 group_code 허용)
    __table_args__ = (
        UniqueConstraint("tenant_id", "group_code", name="uk_tenant_group"),
        Index("idx_tenant_priority", "tenant_id", "priority"),
    )

    def __repr__(self) -> str:
        return f"<UserGroup(id={self.id}, code={self.group_code}, name={self.group_name})>"


# ============================================================
# 3. UserGroupMember (사용자-그룹 매핑)
# ============================================================
class UserGroupMember(Base):
    """
    사용자-그룹 매핑 (중간 테이블)

    사용자가 어떤 그룹에 속하는지 저장.
    한 사용자가 여러 그룹에 속할 수 있음.

    Attributes:
        id: 매핑 ID (PK)
        user_id: 사용자 ID (외부 참조)
        group_id: 그룹 ID (FK)
        created_at: 생성일시
        created_by: 생성자
    """

    __tablename__ = "user_group_members"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # 관계
    user_id = Column(String(50), nullable=False, index=True)
    group_id = Column(
        BigInteger,
        ForeignKey("user_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 감사 컬럼 (TimestampMixin 중 일부만)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)

    # 관계
    group = relationship("UserGroup", back_populates="members")

    # 복합 고유 제약
    __table_args__ = (UniqueConstraint("user_id", "group_id", name="uk_user_group"),)

    def __repr__(self) -> str:
        return f"<UserGroupMember(user_id={self.user_id}, group_id={self.group_id})>"


# ============================================================
# 4. Role (역할)
# ============================================================
class RoleScopeEnum(str, enum.Enum):
    """역할 범위"""
    ADMIN = "admin"  # 관리자 전용
    USER = "user"  # 사용자 전용
    BOTH = "both"  # 모두 사용


class Role(Base, TimestampMixin):
    """
    역할 (권한 관리)

    사용자에게 부여할 수 있는 역할 정의.
    기본 역할: super_admin, admin, manager, editor, viewer

    Attributes:
        id: 역할 ID (PK)
        role_name: 역할명
        role_code: 역할 코드 (고유)
        description: 설명
        priority: 우선순위
        role_scope: 역할 범위 (admin/user/both)
        is_active: 활성 여부
        is_deleted: 소프트 삭제 여부
    """

    __tablename__ = "roles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # 기본 정보
    role_name = Column(String(100), nullable=False)
    role_code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # 역할 설정
    priority = Column(Integer, default=0, index=True)
    role_scope = Column(Enum(RoleScopeEnum), default=RoleScopeEnum.BOTH, nullable=False)

    # 관계
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, code={self.role_code}, name={self.role_name})>"


# ============================================================
# 5. UserRole (사용자-역할 매핑)
# ============================================================
class UserRole(Base):
    """
    사용자-역할 매핑 (중간 테이블)

    사용자가 어떤 역할을 가지는지 저장.
    한 사용자가 여러 역할을 가질 수 있음.

    Attributes:
        id: 매핑 ID (PK)
        user_id: 사용자 ID (외부 참조)
        role_id: 역할 ID (FK)
        created_at: 생성일시
        created_by: 생성자
    """

    __tablename__ = "user_roles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # 관계
    user_id = Column(String(50), nullable=False, index=True)
    role_id = Column(
        BigInteger,
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 감사 컬럼 (TimestampMixin 중 일부만)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)

    # 관계
    role = relationship("Role", back_populates="user_roles")

    # 복합 고유 제약
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uk_user_role"),)

    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"
