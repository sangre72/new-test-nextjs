"""
Shared Services - 공유 모델의 비즈니스 로직

포함:
- TenantService
- UserGroupService
- RoleService
"""

import json
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any

from app.models.shared import (
    Tenant,
    UserGroup,
    UserGroupMember,
    Role,
    UserRole,
    GroupTypeEnum,
    RoleScopeEnum,
)


class TenantService:
    """테넌트 관리 서비스"""

    @staticmethod
    async def get_tenant_by_code(
        session: AsyncSession,
        tenant_code: str,
    ) -> Optional[Tenant]:
        """테넌트 코드로 테넌트 조회"""
        result = await session.execute(
            select(Tenant).where(
                Tenant.tenant_code == tenant_code,
                Tenant.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tenant_by_id(
        session: AsyncSession,
        tenant_id: int,
    ) -> Optional[Tenant]:
        """테넌트 ID로 테넌트 조회"""
        result = await session.execute(
            select(Tenant).where(
                Tenant.id == tenant_id,
                Tenant.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tenant_by_domain(
        session: AsyncSession,
        domain: str,
    ) -> Optional[Tenant]:
        """도메인으로 테넌트 조회 (서브도메인 또는 커스텀 도메인)"""
        # 서브도메인으로 먼저 찾기
        result = await session.execute(
            select(Tenant).where(
                Tenant.subdomain == domain,
                Tenant.is_deleted == False,
                Tenant.is_active == True,
            )
        )
        tenant = result.scalar_one_or_none()

        if tenant:
            return tenant

        # 커스텀 도메인으로 찾기
        result = await session.execute(
            select(Tenant).where(
                Tenant.domain == domain,
                Tenant.is_deleted == False,
                Tenant.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_tenants(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> tuple[List[Tenant], int]:
        """모든 테넌트 조회"""
        # 쿼리 구성
        query = select(Tenant).where(Tenant.is_deleted == False)

        if is_active is not None:
            query = query.where(Tenant.is_active == is_active)

        # 총 개수
        count_query = select(func.count(Tenant.id)).where(Tenant.is_deleted == False)
        if is_active is not None:
            count_query = count_query.where(Tenant.is_active == is_active)

        count_result = await session.execute(count_query)
        total = count_result.scalar()

        # 페이징된 결과
        result = await session.execute(
            query.order_by(Tenant.created_at.desc()).offset(skip).limit(limit)
        )
        tenants = result.scalars().all()

        return tenants, total

    @staticmethod
    async def create_tenant(
        session: AsyncSession,
        tenant_code: str,
        tenant_name: str,
        description: Optional[str] = None,
        domain: Optional[str] = None,
        subdomain: Optional[str] = None,
        admin_email: Optional[str] = None,
        admin_name: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        created_by: str = "system",
    ) -> Tenant:
        """새 테넌트 생성"""
        # settings를 JSON으로 변환
        settings_json = None
        if settings:
            settings_json = settings

        tenant = Tenant(
            tenant_code=tenant_code,
            tenant_name=tenant_name,
            description=description,
            domain=domain,
            subdomain=subdomain,
            admin_email=admin_email,
            admin_name=admin_name,
            settings=settings_json,
            created_by=created_by,
        )
        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)
        return tenant

    @staticmethod
    async def update_tenant(
        session: AsyncSession,
        tenant_id: int,
        tenant_name: Optional[str] = None,
        description: Optional[str] = None,
        domain: Optional[str] = None,
        subdomain: Optional[str] = None,
        admin_email: Optional[str] = None,
        admin_name: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None,
        updated_by: str = "system",
    ) -> Optional[Tenant]:
        """테넌트 수정"""
        tenant = await TenantService.get_tenant_by_id(session, tenant_id)

        if not tenant:
            return None

        if tenant_name is not None:
            tenant.tenant_name = tenant_name
        if description is not None:
            tenant.description = description
        if domain is not None:
            tenant.domain = domain
        if subdomain is not None:
            tenant.subdomain = subdomain
        if admin_email is not None:
            tenant.admin_email = admin_email
        if admin_name is not None:
            tenant.admin_name = admin_name
        if settings is not None:
            tenant.settings = settings
        if is_active is not None:
            tenant.is_active = is_active

        tenant.updated_by = updated_by

        await session.commit()
        await session.refresh(tenant)
        return tenant

    @staticmethod
    async def delete_tenant(
        session: AsyncSession,
        tenant_id: int,
        updated_by: str = "system",
    ) -> bool:
        """테넌트 소프트 삭제 (기본 테넌트는 삭제 불가)"""
        tenant = await TenantService.get_tenant_by_id(session, tenant_id)

        if not tenant:
            return False

        # 기본 테넌트는 삭제 불가
        if tenant.tenant_code == "default":
            return False

        tenant.is_deleted = True
        tenant.updated_by = updated_by

        await session.commit()
        return True

    @staticmethod
    async def get_tenant_settings(
        session: AsyncSession,
        tenant_id: int,
    ) -> Optional[Dict[str, Any]]:
        """테넌트의 설정 조회"""
        tenant = await TenantService.get_tenant_by_id(session, tenant_id)

        if not tenant:
            return None

        return tenant.settings or {}

    @staticmethod
    async def update_tenant_settings(
        session: AsyncSession,
        tenant_id: int,
        settings: Dict[str, Any],
        updated_by: str = "system",
    ) -> Optional[Dict[str, Any]]:
        """테넌트의 설정 업데이트 (부분 업데이트)"""
        tenant = await TenantService.get_tenant_by_id(session, tenant_id)

        if not tenant:
            return None

        # 기존 설정 유지하고 새 설정으로 병합
        current_settings = tenant.settings or {}
        updated_settings = {**current_settings, **settings}

        tenant.settings = updated_settings
        tenant.updated_by = updated_by

        await session.commit()
        await session.refresh(tenant)
        return tenant.settings


class UserGroupService:
    """사용자 그룹 관리 서비스"""

    @staticmethod
    async def get_group_by_code(
        session: AsyncSession,
        tenant_id: int,
        group_code: str,
    ) -> Optional[UserGroup]:
        """그룹 코드로 그룹 조회"""
        result = await session.execute(
            select(UserGroup).where(
                UserGroup.tenant_id == tenant_id,
                UserGroup.group_code == group_code,
                UserGroup.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_groups(
        session: AsyncSession,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[UserGroup], int]:
        """테넌트의 모든 그룹 조회"""
        # 총 개수
        count_result = await session.execute(
            select(func.count(UserGroup.id)).where(
                UserGroup.tenant_id == tenant_id,
                UserGroup.is_deleted == False,
            )
        )
        total = count_result.scalar()

        # 페이징된 결과
        result = await session.execute(
            select(UserGroup)
            .where(
                UserGroup.tenant_id == tenant_id,
                UserGroup.is_deleted == False,
            )
            .order_by(UserGroup.priority.desc(), UserGroup.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        groups = result.scalars().all()

        return groups, total

    @staticmethod
    async def add_user_to_group(
        session: AsyncSession,
        user_id: str,
        group_id: int,
        created_by: str = "system",
    ) -> UserGroupMember:
        """사용자를 그룹에 추가"""
        # 이미 멤버인지 확인
        result = await session.execute(
            select(UserGroupMember).where(
                UserGroupMember.user_id == user_id,
                UserGroupMember.group_id == group_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        member = UserGroupMember(
            user_id=user_id,
            group_id=group_id,
            created_by=created_by,
        )
        session.add(member)
        await session.commit()
        await session.refresh(member)
        return member

    @staticmethod
    async def get_user_groups(
        session: AsyncSession,
        user_id: str,
        tenant_id: Optional[int] = None,
    ) -> List[UserGroup]:
        """사용자가 속한 모든 그룹 조회"""
        query = (
            select(UserGroup)
            .join(UserGroupMember)
            .where(
                UserGroupMember.user_id == user_id,
                UserGroup.is_deleted == False,
            )
        )

        if tenant_id:
            query = query.where(UserGroup.tenant_id == tenant_id)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_group_member_count(
        session: AsyncSession,
        group_id: int,
    ) -> int:
        """그룹의 멤버 수"""
        result = await session.execute(
            select(func.count(UserGroupMember.id)).where(
                UserGroupMember.group_id == group_id
            )
        )
        return result.scalar() or 0


class RoleService:
    """역할 관리 서비스"""

    @staticmethod
    async def get_role_by_code(
        session: AsyncSession,
        role_code: str,
    ) -> Optional[Role]:
        """역할 코드로 역할 조회"""
        result = await session.execute(
            select(Role).where(
                Role.role_code == role_code,
                Role.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_role_by_id(
        session: AsyncSession,
        role_id: int,
    ) -> Optional[Role]:
        """역할 ID로 역할 조회"""
        result = await session.execute(
            select(Role).where(
                Role.id == role_id,
                Role.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_roles(
        session: AsyncSession,
        role_scope: Optional[RoleScopeEnum] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Role], int]:
        """모든 역할 조회"""
        # 필터링
        query = select(Role).where(Role.is_deleted == False)

        if role_scope:
            query = query.where(Role.role_scope == role_scope)

        # 총 개수
        count_query = select(func.count(Role.id)).where(Role.is_deleted == False)
        if role_scope:
            count_query = count_query.where(Role.role_scope == role_scope)

        count_result = await session.execute(count_query)
        total = count_result.scalar()

        # 페이징된 결과
        result = await session.execute(
            query.order_by(Role.priority.desc()).offset(skip).limit(limit)
        )
        roles = result.scalars().all()

        return roles, total

    @staticmethod
    async def assign_role_to_user(
        session: AsyncSession,
        user_id: str,
        role_id: int,
        created_by: str = "system",
    ) -> UserRole:
        """사용자에게 역할 할당"""
        # 이미 할당되었는지 확인
        result = await session.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            created_by=created_by,
        )
        session.add(user_role)
        await session.commit()
        await session.refresh(user_role)
        return user_role

    @staticmethod
    async def get_user_roles(
        session: AsyncSession,
        user_id: str,
    ) -> List[Role]:
        """사용자가 가진 모든 역할 조회"""
        result = await session.execute(
            select(Role)
            .join(UserRole)
            .where(
                UserRole.user_id == user_id,
                Role.is_deleted == False,
            )
        )
        return result.scalars().all()

    @staticmethod
    async def is_user_admin(
        session: AsyncSession,
        user_id: str,
    ) -> bool:
        """사용자가 관리자인지 확인"""
        result = await session.execute(
            select(func.count(UserRole.id))
            .join(Role)
            .where(
                UserRole.user_id == user_id,
                Role.role_scope == RoleScopeEnum.ADMIN,
                Role.is_deleted == False,
            )
        )
        count = result.scalar() or 0
        return count > 0
