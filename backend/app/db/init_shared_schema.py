"""
Shared Schema Initialization Script

공유 데이터베이스 테이블을 초기화하고 기본 데이터를 삽입합니다.

테이블:
1. tenants - 테넌트 (멀티사이트)
2. user_groups - 사용자 그룹
3. user_group_members - 사용자-그룹 매핑
4. roles - 역할
5. user_roles - 사용자-역할 매핑

사용법:
    python -m app.db.init_shared_schema
    또는
    asyncio.run(init_shared_schema())
"""

import asyncio
import logging
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
from app.models.shared import (
    Tenant,
    UserGroup,
    Role,
    GroupTypeEnum,
    RoleScopeEnum,
)

logger = logging.getLogger(__name__)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


async def check_shared_tables() -> dict:
    """
    공유 테이블 존재 여부 확인

    Returns:
        {
            "initialized": bool,
            "existing_tables": list[str],
            "missing_tables": list[str]
        }
    """
    required_tables = [
        "tenants",
        "user_groups",
        "user_group_members",
        "roles",
        "user_roles",
    ]

    async with AsyncSessionLocal() as session:
        try:
            # PostgreSQL information_schema 확인
            query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = ANY(:tables)
            """)

            result = await session.execute(query, {"tables": required_tables})
            existing_tables = [row[0] for row in result.fetchall()]

            missing_tables = [t for t in required_tables if t not in existing_tables]

            return {
                "initialized": len(missing_tables) == 0,
                "existing_tables": existing_tables,
                "missing_tables": missing_tables,
            }
        except Exception as e:
            logger.error(f"테이블 확인 실패: {e}")
            return {
                "initialized": False,
                "existing_tables": [],
                "missing_tables": required_tables,
            }


async def create_tables():
    """SQLAlchemy 모델을 기반으로 테이블 생성"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("테이블 생성 완료")
        return True
    except Exception as e:
        logger.error(f"테이블 생성 실패: {e}")
        return False


async def insert_default_tenant():
    """기본 테넌트 삽입"""
    async with AsyncSessionLocal() as session:
        try:
            # 기존 테넌트 확인
            result = await session.execute(
                text("SELECT id FROM tenants WHERE tenant_code = 'default'")
            )
            if result.fetchone():
                logger.info("기본 테넌트가 이미 존재합니다")
                return None

            # 새 테넌트 생성
            tenant = Tenant(
                tenant_code="default",
                tenant_name="기본 사이트",
                description="기본 테넌트 (단일 사이트 운영 시 사용)",
                created_by="system",
            )
            session.add(tenant)
            await session.commit()
            await session.refresh(tenant)
            logger.info(f"기본 테넌트 생성 완료 (ID: {tenant.id})")
            return tenant.id

        except Exception as e:
            await session.rollback()
            logger.error(f"기본 테넌트 생성 실패: {e}")
            return None


async def insert_default_groups(tenant_id: int):
    """기본 사용자 그룹 삽입"""
    default_groups = [
        {
            "group_name": "전체 회원",
            "group_code": "all_members",
            "priority": 0,
            "group_type": GroupTypeEnum.SYSTEM,
        },
        {
            "group_name": "일반 회원",
            "group_code": "regular",
            "priority": 10,
            "group_type": GroupTypeEnum.SYSTEM,
        },
        {
            "group_name": "VIP 회원",
            "group_code": "vip",
            "priority": 50,
            "group_type": GroupTypeEnum.SYSTEM,
        },
        {
            "group_name": "프리미엄 회원",
            "group_code": "premium",
            "priority": 80,
            "group_type": GroupTypeEnum.SYSTEM,
        },
    ]

    async with AsyncSessionLocal() as session:
        try:
            existing = await session.execute(
                text("SELECT group_code FROM user_groups WHERE tenant_id = :tenant_id"),
                {"tenant_id": tenant_id},
            )
            existing_codes = {row[0] for row in existing.fetchall()}

            created_count = 0
            for group_data in default_groups:
                if group_data["group_code"] not in existing_codes:
                    group = UserGroup(
                        tenant_id=tenant_id,
                        group_name=group_data["group_name"],
                        group_code=group_data["group_code"],
                        priority=group_data["priority"],
                        group_type=group_data["group_type"],
                        created_by="system",
                    )
                    session.add(group)
                    created_count += 1

            if created_count > 0:
                await session.commit()
                logger.info(f"{created_count}개의 사용자 그룹 생성 완료")
            else:
                logger.info("사용자 그룹이 이미 모두 존재합니다")

        except Exception as e:
            await session.rollback()
            logger.error(f"사용자 그룹 생성 실패: {e}")


async def insert_default_roles():
    """기본 역할 삽입"""
    default_roles = [
        {
            "role_name": "슈퍼관리자",
            "role_code": "super_admin",
            "priority": 100,
            "role_scope": RoleScopeEnum.ADMIN,
        },
        {
            "role_name": "관리자",
            "role_code": "admin",
            "priority": 50,
            "role_scope": RoleScopeEnum.ADMIN,
        },
        {
            "role_name": "매니저",
            "role_code": "manager",
            "priority": 30,
            "role_scope": RoleScopeEnum.ADMIN,
        },
        {
            "role_name": "에디터",
            "role_code": "editor",
            "priority": 20,
            "role_scope": RoleScopeEnum.BOTH,
        },
        {
            "role_name": "뷰어",
            "role_code": "viewer",
            "priority": 10,
            "role_scope": RoleScopeEnum.BOTH,
        },
    ]

    async with AsyncSessionLocal() as session:
        try:
            existing = await session.execute(text("SELECT role_code FROM roles"))
            existing_codes = {row[0] for row in existing.fetchall()}

            created_count = 0
            for role_data in default_roles:
                if role_data["role_code"] not in existing_codes:
                    role = Role(
                        role_name=role_data["role_name"],
                        role_code=role_data["role_code"],
                        priority=role_data["priority"],
                        role_scope=role_data["role_scope"],
                        created_by="system",
                    )
                    session.add(role)
                    created_count += 1

            if created_count > 0:
                await session.commit()
                logger.info(f"{created_count}개의 역할 생성 완료")
            else:
                logger.info("역할이 이미 모두 존재합니다")

        except Exception as e:
            await session.rollback()
            logger.error(f"역할 생성 실패: {e}")


async def init_shared_schema():
    """
    공유 스키마 초기화 메인 함수

    순서:
    1. 테이블 생성
    2. 기본 테넌트 생성
    3. 기본 그룹 생성
    4. 기본 역할 생성
    """
    logger.info("=" * 60)
    logger.info("공유 스키마 초기화 시작")
    logger.info("=" * 60)

    # 1. 현재 상태 확인
    logger.info("1단계: 테이블 존재 여부 확인 중...")
    check_result = await check_shared_tables()

    if check_result["initialized"]:
        logger.info("이미 초기화되어 있습니다")
        logger.info(f"기존 테이블: {', '.join(check_result['existing_tables'])}")
        return True

    logger.info(f"누락된 테이블: {', '.join(check_result['missing_tables'])}")

    # 2. 테이블 생성
    logger.info("2단계: 테이블 생성 중...")
    if not await create_tables():
        logger.error("테이블 생성 실패")
        return False

    # 3. 기본 데이터 삽입
    logger.info("3단계: 기본 데이터 삽입 중...")

    default_tenant_id = await insert_default_tenant()
    if not default_tenant_id:
        logger.error("기본 테넌트 생성 실패")
        return False

    await insert_default_groups(default_tenant_id)
    await insert_default_roles()

    # 완료
    logger.info("=" * 60)
    logger.info("공유 스키마 초기화 완료!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("생성된 테이블:")
    logger.info("  ✓ tenants: 테넌트 (멀티사이트)")
    logger.info("  ✓ user_groups: 사용자 그룹")
    logger.info("  ✓ user_group_members: 사용자-그룹 매핑")
    logger.info("  ✓ roles: 역할")
    logger.info("  ✓ user_roles: 사용자-역할 매핑")
    logger.info("")
    logger.info("기본 데이터:")
    logger.info("  ✓ 테넌트 1개: default (기본 사이트)")
    logger.info("  ✓ 그룹 4개: 전체회원, 일반회원, VIP, 프리미엄")
    logger.info("  ✓ 역할 5개: 슈퍼관리자, 관리자, 매니저, 에디터, 뷰어")
    logger.info("")

    return True


async def main():
    """CLI 엔트리 포인트"""
    try:
        success = await init_shared_schema()
        if success:
            logger.info("초기화 성공")
            return 0
        else:
            logger.error("초기화 실패")
            return 1
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        return 1
    finally:
        await engine.dispose()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
