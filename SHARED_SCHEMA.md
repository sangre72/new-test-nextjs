# 공유 데이터베이스 스키마 (Shared Schema)

여러 에이전트가 **공통으로 사용하는 테이블**을 정의하고 초기화합니다.

**상태**: 초기화 완료

---

## 목차

1. [개요](#개요)
2. [테이블 목록](#테이블-목록)
3. [멀티 테넌트 아키텍처](#멀티-테넌트-아키텍처)
4. [초기화 방법](#초기화-방법)
5. [데이터 모델](#데이터-모델)
6. [API 사용 예시](#api-사용-예시)
7. [다른 에이전트 의존성](#다른-에이전트-의존성)

---

## 개요

**공유 스키마**는 다음 에이전트들이 공통으로 사용하는 테이블들입니다:

- `auth-backend`: 사용자 인증
- `menu-manager`: 메뉴 관리
- `board-generator`: 게시판 시스템
- 기타 사용자/권한 관련 에이전트

### 핵심 특징

- **멀티 테넌트**: 여러 사이트/조직을 하나의 시스템에서 관리
- **감사 추적**: 모든 테이블에 생성자, 수정자, 날짜 기록
- **소프트 삭제**: 데이터 복구 가능한 논리적 삭제
- **계층적 권한**: 역할(Role)과 그룹(Group)을 통한 권한 관리

---

## 테이블 목록

| 테이블 | 설명 | 행 수 | 의존 에이전트 |
|--------|------|-------|--------------|
| `tenants` | 테넌트 (멀티사이트) | 1+ | 모든 에이전트 |
| `user_groups` | 사용자 그룹 | 4+ | board-generator, menu-manager |
| `user_group_members` | 사용자-그룹 매핑 | N | board-generator, menu-manager |
| `roles` | 역할 | 5+ | menu-manager, auth-backend |
| `user_roles` | 사용자-역할 매핑 | N | menu-manager, auth-backend |

### 테이블 관계도

```
                    tenants
                       │
                       │ (fk: tenant_id)
                       ▼
    ┌──────────────────┬──────────────────┐
    │                  │                  │
    ▼                  ▼                  ▼
user_groups          roles          (other tables)
    │
    │ (1:N)
    ▼
user_group_members      user_roles
                            │
                            └─────── roles (fk)
```

---

## 멀티 테넌트 아키텍처

### 테넌트 개념

**테넌트**: 하나의 시스템에서 여러 사이트/조직을 독립적으로 운영하기 위한 개념

```
┌─────────────────────────────────────────────────────────┐
│               Single Application                         │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Tenant A    │  │  Tenant B    │  │  Tenant C    │  │
│  │  (siteA.com) │  │  (siteB.com) │  │  (siteC.com) │  │
│  │              │  │              │  │              │  │
│  │ - Users      │  │ - Users      │  │ - Users      │  │
│  │ - Menus      │  │ - Menus      │  │ - Menus      │  │
│  │ - Boards     │  │ - Boards     │  │ - Boards     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
└─────────────────────────────────────────────────────────┘
          ↓
       Database (PostgreSQL)
```

### 테넌트 식별 방식

| 방식 | 예시 | 사용 시나리오 |
|------|------|--------------|
| **서브도메인** | `siteA.example.com` | SaaS 플랫폼 |
| **커스텀 도메인** | `siteA.com` | 완전 독립 사이트 |
| **경로** | `example.com/siteA` | 단일 도메인 멀티사이트 |
| **헤더** | `X-Tenant-ID: siteA` | API 기반 시스템 |

### 데이터 분리

모든 테이블은 `tenant_id`를 통해 테넌트별로 데이터를 분리합니다:

```python
# 예: 특정 테넌트의 메뉴만 조회
query = select(Menu).where(Menu.tenant_id == current_tenant_id)
```

---

## 초기화 방법

### 1. 자동 초기화

가장 간단한 방법입니다. Python 스크립트를 실행하면 모든 테이블과 기본 데이터가 자동으로 생성됩니다.

```bash
cd /Users/bumsuklee/git/new-test/backend
python -m app.db.init_shared_schema
```

**출력 예시:**

```
INFO:__main__:============================================================
INFO:__main__:공유 스키마 초기화 시작
INFO:__main__:============================================================
INFO:__main__:1단계: 테이블 존재 여부 확인 중...
INFO:__main__:누락된 테이블: ['tenants', 'user_groups', 'user_group_members', 'roles', 'user_roles']
INFO:__main__:2단계: 테이블 생성 중...
INFO:__main__:테이블 생성 완료
INFO:__main__:3단계: 기본 데이터 삽입 중...
INFO:__main__:기본 테넌트 생성 완료 (ID: 1)
INFO:__main__:4개의 사용자 그룹 생성 완료
INFO:__main__:5개의 역할 생성 완료
INFO:__main__:============================================================
INFO:__main__:공유 스키마 초기화 완료!
INFO:__main__:============================================================
```

### 2. Python 코드에서 초기화

다른 에이전트의 초기화 코드에서 이 함수를 호출할 수 있습니다:

```python
from app.db.init_shared_schema import init_shared_schema, check_shared_tables

# 테이블 상태 확인
check_result = await check_shared_tables()
if not check_result["initialized"]:
    print(f"누락된 테이블: {check_result['missing_tables']}")
    await init_shared_schema()
```

### 3. 개별 테이블 생성

SQLAlchemy를 통해 개별 테이블을 생성할 수 있습니다:

```python
from app.db.session import engine
from app.db.base import Base

# 모든 테이블 생성
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)

# 특정 테이블만 생성
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.tables['tenants'].create)
```

---

## 데이터 모델

### 1. Tenant (테넌트)

```python
class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id: int                    # 테넌트 ID (PK)
    tenant_code: str           # 테넌트 코드 (고유)
    tenant_name: str           # 테넌트명
    description: str           # 설명
    domain: str                # 커스텀 도메인
    subdomain: str             # 서브도메인
    settings: dict             # JSON 설정
    admin_email: str           # 관리자 이메일
    admin_name: str            # 관리자 이름

    # TimestampMixin
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    is_active: bool
    is_deleted: bool
```

**기본 데이터:**

```sql
INSERT INTO tenants VALUES (
    1, 'default', '기본 사이트', '기본 테넌트',
    NULL, NULL, NULL, NULL, NULL,
    NOW(), 'system', NOW(), 'system', true, false
);
```

### 2. UserGroup (사용자 그룹)

```python
class UserGroup(Base, TimestampMixin):
    __tablename__ = "user_groups"

    id: int                    # 그룹 ID (PK)
    tenant_id: int             # 테넌트 ID (FK)
    group_name: str            # 그룹명
    group_code: str            # 그룹 코드 (테넌트별 고유)
    description: str           # 설명
    priority: int              # 우선순위
    group_type: enum           # 타입 (system/custom)

    # TimestampMixin
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    is_active: bool
    is_deleted: bool
```

**기본 데이터:**

| group_name | group_code | priority | group_type |
|----------|-----------|----------|-----------|
| 전체 회원 | all_members | 0 | system |
| 일반 회원 | regular | 10 | system |
| VIP 회원 | vip | 50 | system |
| 프리미엄 회원 | premium | 80 | system |

### 3. UserGroupMember (사용자-그룹 매핑)

```python
class UserGroupMember(Base):
    __tablename__ = "user_group_members"

    id: int                    # 매핑 ID (PK)
    user_id: str               # 사용자 ID (외부 참조)
    group_id: int              # 그룹 ID (FK)
    created_at: datetime
    created_by: str

    # 복합 고유 제약: (user_id, group_id)
```

**사용법:**

```python
# 사용자를 그룹에 추가
member = UserGroupMember(
    user_id="user123",
    group_id=1,
    created_by="admin"
)
```

### 4. Role (역할)

```python
class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: int                    # 역할 ID (PK)
    role_name: str             # 역할명
    role_code: str             # 역할 코드 (고유)
    description: str           # 설명
    priority: int              # 우선순위 (높을수록 상위)
    role_scope: enum           # 범위 (admin/user/both)

    # TimestampMixin
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    is_active: bool
    is_deleted: bool
```

**기본 데이터:**

| role_name | role_code | priority | role_scope |
|----------|----------|----------|-----------|
| 슈퍼관리자 | super_admin | 100 | admin |
| 관리자 | admin | 50 | admin |
| 매니저 | manager | 30 | admin |
| 에디터 | editor | 20 | both |
| 뷰어 | viewer | 10 | both |

### 5. UserRole (사용자-역할 매핑)

```python
class UserRole(Base):
    __tablename__ = "user_roles"

    id: int                    # 매핑 ID (PK)
    user_id: str               # 사용자 ID (외부 참조)
    role_id: int               # 역할 ID (FK)
    created_at: datetime
    created_by: str

    # 복합 고유 제약: (user_id, role_id)
```

**사용법:**

```python
# 사용자에게 역할 부여
user_role = UserRole(
    user_id="user123",
    role_id=3,  # editor
    created_by="admin"
)
```

---

## API 사용 예시

### FastAPI 의존성

```python
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import (
    get_session,
    get_current_tenant,
    get_current_tenant_id,
)
from app.models.shared import UserGroup, Role
from app.schemas.shared import UserGroupResponse, RoleResponse

app = FastAPI()

@app.get("/api/v1/groups")
async def list_groups(
    session: AsyncSession = Depends(get_session),
    tenant_id: int = Depends(get_current_tenant_id),
) -> list[UserGroupResponse]:
    """테넌트의 모든 사용자 그룹 조회"""
    result = await session.execute(
        select(UserGroup)
        .where(UserGroup.tenant_id == tenant_id)
        .where(UserGroup.is_deleted == False)
        .order_by(UserGroup.priority.desc())
    )
    groups = result.scalars().all()
    return [UserGroupResponse.model_validate(g) for g in groups]

@app.get("/api/v1/roles")
async def list_roles(
    session: AsyncSession = Depends(get_session),
) -> list[RoleResponse]:
    """모든 역할 조회"""
    result = await session.execute(
        select(Role)
        .where(Role.is_deleted == False)
        .order_by(Role.priority.desc())
    )
    roles = result.scalars().all()
    return [RoleResponse.model_validate(r) for r in roles]
```

### 쿼리 예시

```python
from sqlalchemy import select
from app.models.shared import UserGroup, UserGroupMember, Role

# 1. 특정 사용자가 속한 모든 그룹 조회
user_id = "user123"
result = await session.execute(
    select(UserGroup)
    .join(UserGroupMember)
    .where(UserGroupMember.user_id == user_id)
    .where(UserGroup.is_deleted == False)
)
user_groups = result.scalars().all()

# 2. 특정 테넌트의 활성 그룹 조회
tenant_id = 1
result = await session.execute(
    select(UserGroup)
    .where(UserGroup.tenant_id == tenant_id)
    .where(UserGroup.is_active == True)
    .where(UserGroup.is_deleted == False)
    .order_by(UserGroup.priority.desc())
)
groups = result.scalars().all()

# 3. 특정 역할의 모든 사용자 조회
role_code = "admin"
result = await session.execute(
    select(UserRole.user_id)
    .join(Role)
    .where(Role.role_code == role_code)
    .where(Role.is_deleted == False)
)
user_ids = [row[0] for row in result.fetchall()]

# 4. 그룹별 멤버 수
result = await session.execute(
    select(
        UserGroup.id,
        UserGroup.group_name,
        func.count(UserGroupMember.id).label('member_count')
    )
    .outerjoin(UserGroupMember)
    .group_by(UserGroup.id)
)
```

---

## 다른 에이전트 의존성

### 의존하는 에이전트

| 에이전트 | 필요 테이블 | 설명 |
|---------|----------|------|
| `auth-backend` | tenants, roles, user_roles | 사용자 인증 및 권한 |
| `menu-manager` | tenants, user_groups, roles | 메뉴 관리 |
| `board-generator` | tenants, user_groups, user_group_members | 게시판 접근 제어 |
| `tenant-manager` | tenants | 테넌트 관리 |

### 초기화 순서

공유 스키마는 **반드시 가장 먼저 초기화**되어야 합니다:

```bash
# 1단계: 공유 스키마 (필수 - 가장 먼저)
python -m app.db.init_shared_schema

# 2단계: 다른 에이전트들은 이후에 초기화
Use auth-backend --init --type=phone
Use menu-manager --init
Use board-generator --init
```

### 의존성 확인 코드

다른 에이전트에서 사용할 수 있는 의존성 확인 함수:

```python
from app.db.init_shared_schema import check_shared_tables

async def ensure_shared_schema_initialized():
    """공유 스키마가 초기화되었는지 확인"""
    check_result = await check_shared_tables()

    if not check_result["initialized"]:
        print("공유 스키마가 초기화되지 않았습니다")
        print(f"누락된 테이블: {check_result['missing_tables']}")

        # 자동 초기화
        from app.db.init_shared_schema import init_shared_schema
        await init_shared_schema()

    return check_result
```

---

## 파일 구조

```
backend/app/
├── db/
│   ├── __init__.py
│   ├── base.py                    # Base, TimestampMixin
│   ├── session.py                 # AsyncSession, engine
│   └── init_shared_schema.py       # 초기화 스크립트
├── models/
│   ├── __init__.py
│   └── shared.py                  # Tenant, UserGroup, Role 등
├── schemas/
│   ├── __init__.py
│   └── shared.py                  # 요청/응답 스키마
└── api/
    ├── __init__.py
    └── deps.py                    # get_session, get_current_tenant
```

---

## 데이터베이스 연결

### 환경 변수 설정 (.env)

```bash
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/newtest

# Redis (선택사항)
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-min-32-chars
JWT_EXPIRES_IN=3600
JWT_REFRESH_EXPIRES_IN=604800

# 개발 모드
DEV_MODE=true
DEV_VERIFICATION_CODE=000000

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 데이터베이스 생성

PostgreSQL을 사용하는 경우:

```bash
# Docker로 PostgreSQL 실행
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=newtest \
  -p 5432:5432 \
  postgres:15

# 또는 로컬 설치
createdb newtest
```

---

## 문제 해결

### 테이블이 이미 존재하는 경우

초기화 스크립트가 기존 테이블을 감지하면 자동으로 건너뜁니다.

```bash
python -m app.db.init_shared_schema
# INFO:__main__:이미 초기화되어 있습니다
```

### 테이블 초기화 (데이터 손실)

**주의**: 이 명령은 모든 데이터를 삭제합니다!

```python
from app.db.session import engine
from app.db.base import Base

# 모든 테이블 삭제
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.drop_all)

# 다시 초기화
from app.db.init_shared_schema import init_shared_schema
await init_shared_schema()
```

### 마이그레이션 사용 (Alembic)

대규모 프로젝트의 경우 Alembic을 사용하여 마이그레이션을 관리할 수 있습니다:

```bash
# 마이그레이션 생성
alembic revision --autogenerate -m "Add shared schema"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

---

## 참고

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 문서](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2 문서](https://docs.pydantic.dev/)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)

---

**마지막 업데이트**: 2026-01-03
