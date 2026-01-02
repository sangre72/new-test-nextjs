"""
Category Service - 카테고리 관리 비즈니스 로직

포함:
- CategoryService: 카테고리 CRUD, 계층 관리, 순서 변경

특징:
- 계층형 카테고리 관리 (depth, path 자동 계산)
- 경로 기반 빠른 쿼리
- 순환 참조 방지 (자신의 하위를 상위로 설정 불가)
- 트랜잭션 관리 (부모 변경 시 하위 경로 모두 업데이트)
- 게시글 수 캐싱

사용법:
    from app.services.category import CategoryService

    # 카테고리 생성
    category = await CategoryService.create_category(
        session=session,
        tenant_id=1,
        board_id=1,
        category_name="일반",
        category_code="general",
    )

    # 계층형 카테고리 목록 조회
    categories = await CategoryService.get_categories_tree(
        session=session,
        tenant_id=1,
        board_id=1,
    )

    # 순서 변경
    await CategoryService.reorder_categories(
        session=session,
        category_id=3,
        new_parent_id=1,
        new_sort_order=5,
    )
"""

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple

from app.models.category import Category


class CategoryService:
    """카테고리 관리 서비스"""

    # ============================================================
    # 조회 (READ)
    # ============================================================

    @staticmethod
    async def get_category_by_id(
        session: AsyncSession,
        category_id: int,
        tenant_id: Optional[int] = None,
    ) -> Optional[Category]:
        """카테고리 ID로 조회"""
        query = select(Category).where(
            Category.id == category_id,
            Category.is_deleted == False,
        )

        if tenant_id:
            query = query.where(Category.tenant_id == tenant_id)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_category_by_code(
        session: AsyncSession,
        board_id: int,
        category_code: str,
        tenant_id: Optional[int] = None,
    ) -> Optional[Category]:
        """카테고리 코드로 조회"""
        query = select(Category).where(
            Category.board_id == board_id,
            Category.category_code == category_code,
            Category.is_deleted == False,
        )

        if tenant_id:
            query = query.where(Category.tenant_id == tenant_id)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_categories_flat(
        session: AsyncSession,
        tenant_id: int,
        board_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Category], int]:
        """카테고리 목록 조회 (평면)"""
        # 총 개수
        count_result = await session.execute(
            select(func.count(Category.id)).where(
                Category.tenant_id == tenant_id,
                Category.board_id == board_id,
                Category.is_deleted == False,
            )
        )
        total = count_result.scalar() or 0

        # 페이징된 결과
        result = await session.execute(
            select(Category)
            .where(
                Category.tenant_id == tenant_id,
                Category.board_id == board_id,
                Category.is_deleted == False,
            )
            .order_by(Category.path, Category.sort_order)
            .offset(skip)
            .limit(limit)
        )
        categories = result.scalars().all()

        return categories, total

    @staticmethod
    async def get_categories_tree(
        session: AsyncSession,
        tenant_id: int,
        board_id: int,
    ) -> List[Category]:
        """카테고리 목록 조회 (계층형 트리, 최상위만 반환)"""
        result = await session.execute(
            select(Category)
            .where(
                Category.tenant_id == tenant_id,
                Category.board_id == board_id,
                Category.parent_id == None,
                Category.is_deleted == False,
            )
            .order_by(Category.sort_order, Category.created_at)
        )
        return result.scalars().all()

    @staticmethod
    async def get_category_children(
        session: AsyncSession,
        parent_id: int,
    ) -> List[Category]:
        """카테고리의 하위 카테고리 조회"""
        result = await session.execute(
            select(Category)
            .where(
                Category.parent_id == parent_id,
                Category.is_deleted == False,
            )
            .order_by(Category.sort_order, Category.created_at)
        )
        return result.scalars().all()

    @staticmethod
    async def get_category_descendants(
        session: AsyncSession,
        category_id: int,
    ) -> List[Category]:
        """카테고리의 모든 하위 카테고리 조회 (재귀)"""
        category = await CategoryService.get_category_by_id(session, category_id)
        if not category or not category.path:
            return []

        # path를 이용한 빠른 조회
        result = await session.execute(
            select(Category).where(
                Category.path.startswith(category.path),
                Category.id != category.id,
                Category.is_deleted == False,
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_category_ancestors(
        session: AsyncSession,
        category_id: int,
    ) -> List[Category]:
        """카테고리의 모든 상위 카테고리 조회 (재귀)"""
        ancestors = []
        current = await CategoryService.get_category_by_id(session, category_id)

        while current and current.parent_id:
            parent = await CategoryService.get_category_by_id(
                session, current.parent_id
            )
            if parent:
                ancestors.insert(0, parent)
                current = parent
            else:
                break

        return ancestors

    # ============================================================
    # 생성 (CREATE)
    # ============================================================

    @staticmethod
    async def create_category(
        session: AsyncSession,
        tenant_id: int,
        board_id: int,
        category_name: str,
        category_code: str,
        parent_id: Optional[int] = None,
        description: Optional[str] = None,
        sort_order: int = 0,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        read_permission: str = "all",
        write_permission: str = "all",
        created_by: str = "system",
    ) -> Category:
        """새 카테고리 생성"""
        # 중복 검사
        existing = await CategoryService.get_category_by_code(
            session, board_id, category_code, tenant_id
        )
        if existing:
            raise ValueError(
                f"카테고리 코드 '{category_code}'는 이미 존재합니다."
            )

        # depth와 path 계산
        depth = 0
        path = f"/{board_id}/"

        if parent_id:
            parent = await CategoryService.get_category_by_id(
                session, parent_id, tenant_id
            )
            if not parent:
                raise ValueError("상위 카테고리를 찾을 수 없습니다.")

            depth = parent.depth + 1
            path = parent.path if parent.path else f"/{board_id}/"

        # 카테고리 생성
        category = Category(
            tenant_id=tenant_id,
            board_id=board_id,
            parent_id=parent_id,
            category_name=category_name,
            category_code=category_code,
            description=description,
            depth=depth,
            sort_order=sort_order,
            icon=icon,
            color=color,
            read_permission=read_permission,
            write_permission=write_permission,
            created_by=created_by,
        )
        session.add(category)
        await session.flush()

        # path 업데이트 (자신의 ID를 포함하여)
        category.path = f"{path}{category.id}/"
        await session.flush()

        await session.commit()
        await session.refresh(category)
        return category

    # ============================================================
    # 수정 (UPDATE)
    # ============================================================

    @staticmethod
    async def update_category(
        session: AsyncSession,
        category_id: int,
        tenant_id: int,
        category_name: Optional[str] = None,
        description: Optional[str] = None,
        sort_order: Optional[int] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        read_permission: Optional[str] = None,
        write_permission: Optional[str] = None,
        is_active: Optional[bool] = None,
        updated_by: str = "system",
    ) -> Category:
        """카테고리 수정 (계층 변경 제외)"""
        category = await CategoryService.get_category_by_id(
            session, category_id, tenant_id
        )
        if not category:
            raise ValueError("카테고리를 찾을 수 없습니다.")

        # 필드 업데이트
        if category_name is not None:
            category.category_name = category_name
        if description is not None:
            category.description = description
        if sort_order is not None:
            category.sort_order = sort_order
        if icon is not None:
            category.icon = icon
        if color is not None:
            category.color = color
        if read_permission is not None:
            category.read_permission = read_permission
        if write_permission is not None:
            category.write_permission = write_permission
        if is_active is not None:
            category.is_active = is_active

        category.updated_by = updated_by

        await session.commit()
        await session.refresh(category)
        return category

    @staticmethod
    async def move_category(
        session: AsyncSession,
        category_id: int,
        new_parent_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        updated_by: str = "system",
    ) -> Category:
        """카테고리 계층 변경 (부모 변경)"""
        category = await CategoryService.get_category_by_id(
            session, category_id, tenant_id
        )
        if not category:
            raise ValueError("카테고리를 찾을 수 없습니다.")

        # 자신을 부모로 설정하려고 하면 오류
        if new_parent_id == category_id:
            raise ValueError("자신을 상위 카테고리로 설정할 수 없습니다.")

        # 자신의 하위를 부모로 설정하려고 하면 오류 (순환 참조 방지)
        if new_parent_id:
            descendants = await CategoryService.get_category_descendants(
                session, category_id
            )
            if any(d.id == new_parent_id for d in descendants):
                raise ValueError(
                    "하위 카테고리를 상위 카테고리로 설정할 수 없습니다."
                )

        # 새로운 depth와 path 계산
        new_depth = 0
        new_path = f"/{category.board_id}/"

        if new_parent_id:
            parent = await CategoryService.get_category_by_id(
                session, new_parent_id, tenant_id
            )
            if not parent:
                raise ValueError("새로운 상위 카테고리를 찾을 수 없습니다.")

            new_depth = parent.depth + 1
            new_path = parent.path if parent.path else f"/{category.board_id}/"

        # 기존 path 저장 (하위 카테고리 업데이트용)
        old_path = category.path

        # 카테고리 업데이트
        category.parent_id = new_parent_id
        category.depth = new_depth
        category.path = f"{new_path}{category.id}/"
        category.updated_by = updated_by
        await session.flush()

        # 하위 카테고리들의 path, depth 재귀적 업데이트
        await CategoryService._update_descendants_path(
            session, category_id, old_path, category.path, new_depth + 1
        )

        await session.commit()
        await session.refresh(category)
        return category

    @staticmethod
    async def _update_descendants_path(
        session: AsyncSession,
        parent_id: int,
        old_path: str,
        new_path: str,
        new_base_depth: int,
    ) -> None:
        """하위 카테고리들의 path, depth 재귀적 업데이트"""
        children = await CategoryService.get_category_children(
            session, parent_id
        )

        for child in children:
            if child.path and old_path:
                # 기존 path에서 새로운 path로 교체
                relative_path = child.path[len(old_path) :]
                child.path = new_path + relative_path
                child.depth = new_base_depth + (child.depth - (old_path.count("/") - 1))

            await session.flush()

            # 재귀
            await CategoryService._update_descendants_path(
                session,
                child.id,
                new_path if child.path else old_path,
                child.path if child.path else new_path,
                child.depth + 1,
            )

    @staticmethod
    async def reorder_categories(
        session: AsyncSession,
        category_id: int,
        new_parent_id: Optional[int] = None,
        new_sort_order: int = 0,
        tenant_id: Optional[int] = None,
        updated_by: str = "system",
    ) -> Category:
        """카테고리 순서/계층 변경 (드래그앤드롭)"""
        category = await CategoryService.get_category_by_id(
            session, category_id, tenant_id
        )
        if not category:
            raise ValueError("카테고리를 찾을 수 없습니다.")

        # 부모 변경 필요
        if new_parent_id != category.parent_id:
            category = await CategoryService.move_category(
                session, category_id, new_parent_id, tenant_id, updated_by
            )

        # 정렬 순서 변경
        category.sort_order = new_sort_order
        category.updated_by = updated_by

        await session.commit()
        await session.refresh(category)
        return category

    # ============================================================
    # 삭제 (DELETE)
    # ============================================================

    @staticmethod
    async def delete_category(
        session: AsyncSession,
        category_id: int,
        tenant_id: Optional[int] = None,
        updated_by: str = "system",
    ) -> bool:
        """카테고리 소프트 삭제"""
        category = await CategoryService.get_category_by_id(
            session, category_id, tenant_id
        )
        if not category:
            raise ValueError("카테고리를 찾을 수 없습니다.")

        # 하위 카테고리 존재 확인
        children = await CategoryService.get_category_children(session, category_id)
        if children:
            raise ValueError(
                f"하위 카테고리가 {len(children)}개 있어 삭제할 수 없습니다. "
                "먼저 하위 카테고리를 삭제하세요."
            )

        # 게시글 존재 여부 확인 (외부 서비스에서 처리)
        # post_count가 0이 아니면 게시글이 있음
        if category.post_count > 0:
            raise ValueError(
                f"이 카테고리에 {category.post_count}개의 게시글이 있습니다. "
                "먼저 게시글을 이동하거나 삭제하세요."
            )

        # 소프트 삭제
        category.is_deleted = True
        category.updated_by = updated_by

        await session.commit()
        return True

    @staticmethod
    async def increment_post_count(
        session: AsyncSession,
        category_id: int,
        increment: int = 1,
    ) -> Optional[Category]:
        """게시글 수 증가 (게시글 추가 시)"""
        category = await CategoryService.get_category_by_id(session, category_id)
        if not category:
            return None

        category.post_count = max(0, category.post_count + increment)
        await session.commit()
        await session.refresh(category)
        return category

    @staticmethod
    async def decrement_post_count(
        session: AsyncSession,
        category_id: int,
        decrement: int = 1,
    ) -> Optional[Category]:
        """게시글 수 감소 (게시글 삭제 시)"""
        category = await CategoryService.get_category_by_id(session, category_id)
        if not category:
            return None

        category.post_count = max(0, category.post_count - decrement)
        await session.commit()
        await session.refresh(category)
        return category

    # ============================================================
    # 유틸리티
    # ============================================================

    @staticmethod
    def build_category_tree(
        categories: List[Category],
        parent_id: Optional[int] = None,
    ) -> List[Category]:
        """카테고리 리스트를 계층형 트리로 변환"""
        tree = []
        for category in categories:
            if category.parent_id == parent_id:
                # 하위 카테고리 재귀적으로 추가
                category.children = CategoryService.build_category_tree(
                    categories, category.id
                )
                tree.append(category)
        return tree
