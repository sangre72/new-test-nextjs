# 공유 스키마 초기화 가이드

## 개요

이 가이드는 공유 데이터베이스 스키마(tenants, user_groups, roles 등)를 초기화하는 방법을 설명합니다.

---

## 사전 요구사항

### 1. Python 환경 설정

```bash
cd /Users/bumsuklee/git/new-test/backend

# 가상 환경 생성 (처음 한 번만)
python -m venv venv

# 가상 환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 데이터베이스 설정

PostgreSQL이 실행 중이어야 합니다.

#### Docker 사용 (권장)

```bash
# PostgreSQL 실행
docker run -d \
  --name postgres-newtest \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=newtest \
  -p 5432:5432 \
  postgres:15

# Redis 실행 (선택)
docker run -d \
  --name redis-newtest \
  -p 6379:6379 \
  redis:7
```

#### 로컬 PostgreSQL 사용

```bash
# 데이터베이스 생성
createdb newtest

# 또는 psql 접속 후
psql -U postgres
CREATE DATABASE newtest;
```

### 3. 환경 변수 설정

`.env` 파일이 이미 생성되어 있습니다.
필요시 데이터베이스 연결 정보를 수정하세요:

```bash
# .env 파일 편집
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/newtest
```

---

## 초기화 방법

### 방법 1: CLI 스크립트 실행 (권장)

```bash
cd /Users/bumsuklee/git/new-test/backend

python -m app.db.init_shared_schema
```

**예상 출력:**

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

생성된 테이블:
  ✓ tenants: 테넌트 (멀티사이트)
  ✓ user_groups: 사용자 그룹
  ✓ user_group_members: 사용자-그룹 매핑
  ✓ roles: 역할
  ✓ user_roles: 사용자-역할 매핑

기본 데이터:
  ✓ 테넌트 1개: default (기본 사이트)
  ✓ 그룹 4개: 전체회원, 일반회원, VIP, 프리미엄
  ✓ 역할 5개: 슈퍼관리자, 관리자, 매니저, 에디터, 뷰어
```

### 방법 2: Python 인터프리터에서 실행

```python
import asyncio
from app.db.init_shared_schema import init_shared_schema

asyncio.run(init_shared_schema())
```

### 방법 3: FastAPI 애플리케이션 시작 시 자동 초기화

`app/main.py`에 다음을 추가할 수 있습니다:

```python
from fastapi import FastAPI
from app.db.init_shared_schema import init_shared_schema, check_shared_tables

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 공유 스키마 초기화"""
    check_result = await check_shared_tables()
    if not check_result["initialized"]:
        print("공유 스키마 초기화 중...")
        await init_shared_schema()
```

---

## 초기화 후 검증

### 1. 테이블 확인

```bash
# PostgreSQL 접속
psql -U postgres -d newtest

# 테이블 목록 확인
\dt

# 결과:
#            List of relations
#  Schema |       Name        | Type  | Owner
# --------+-------------------+-------+-------
#  public | tenants           | table | postgres
#  public | user_groups       | table | postgres
#  public | user_group_members | table | postgres
#  public | roles             | table | postgres
#  public | user_roles        | table | postgres
```

### 2. 기본 데이터 확인

```sql
-- 테넌트 확인
SELECT * FROM tenants;
-- id=1, tenant_code='default', tenant_name='기본 사이트'

-- 그룹 확인
SELECT * FROM user_groups;
-- 4개의 기본 그룹이 생성됨

-- 역할 확인
SELECT * FROM roles;
-- 5개의 기본 역할이 생성됨
```

### 3. Python에서 검증

```python
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.shared import Tenant, UserGroup, Role

async def verify_schema():
    async with AsyncSessionLocal() as session:
        # 테넌트 확인
        result = await session.execute(select(Tenant))
        tenants = result.scalars().all()
        print(f"테넌트: {len(tenants)}개")
        for tenant in tenants:
            print(f"  - {tenant.tenant_code}: {tenant.tenant_name}")

        # 그룹 확인
        result = await session.execute(select(UserGroup))
        groups = result.scalars().all()
        print(f"사용자 그룹: {len(groups)}개")
        for group in groups:
            print(f"  - {group.group_code}: {group.group_name}")

        # 역할 확인
        result = await session.execute(select(Role))
        roles = result.scalars().all()
        print(f"역할: {len(roles)}개")
        for role in roles:
            print(f"  - {role.role_code}: {role.role_name}")

import asyncio
asyncio.run(verify_schema())
```

---

## 트러블슈팅

### 데이터베이스 연결 오류

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**해결책:**

```bash
# 1. PostgreSQL 상태 확인
docker ps | grep postgres

# 2. PostgreSQL 실행되지 않으면 시작
docker start postgres-newtest

# 3. 연결 정보 확인
psql -h localhost -U postgres -d newtest
```

### 이미 초기화된 경우

스크립트가 자동으로 기존 테이블을 감지하고 건너뜁니다.

```
INFO:__main__:이미 초기화되어 있습니다
```

### 모든 데이터 초기화 (위험!)

**주의**: 이 작업은 모든 데이터를 삭제합니다!

```python
from app.db.session import engine
from app.db.base import Base

async def reset_database():
    # 모든 테이블 삭제
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # 다시 초기화
    from app.db.init_shared_schema import init_shared_schema
    await init_shared_schema()

import asyncio
asyncio.run(reset_database())
```

---

## 다음 단계

공유 스키마가 초기화된 후 다음 단계를 진행할 수 있습니다:

1. **인증 시스템 구축**
   ```bash
   Use auth-backend --init --type=phone
   Use auth-frontend --init
   ```

2. **메뉴 관리 시스템**
   ```bash
   Use menu-manager --init
   Use menu-backend --init
   ```

3. **게시판 시스템**
   ```bash
   Use board-generator --init
   ```

---

## 파일 위치

- 초기화 스크립트: `app/db/init_shared_schema.py`
- 모델 정의: `app/models/shared.py`
- 스키마 정의: `app/schemas/shared.py`
- 세션 관리: `app/db/session.py`
- 기본 클래스: `app/db/base.py`
- 의존성: `app/api/deps.py`
- 상세 문서: `../SHARED_SCHEMA.md`

---

## 참고 링크

- [SQLAlchemy AsyncIO 문서](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)
- [FastAPI 의존성 주입](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Pydantic 모델](https://docs.pydantic.dev/)

---

**작성일**: 2026-01-03
