# Tenant Management System Setup Guide

완성된 멀티테넌시 관리 시스템입니다. FastAPI + Next.js + PostgreSQL 스택에 통합되었습니다.

## 개요

테넌트 관리 시스템은 다음 기능을 제공합니다:

- 테넌트 CRUD (생성, 조회, 수정, 삭제)
- 도메인 설정 (서브도메인, 커스텀 도메인)
- 테마/로고/언어 설정
- 테넌트 미들웨어 (자동 테넌트 식별)
- 관리자 UI 대시보드

---

## 아키텍처

```
┌─────────────────────────────────────────────┐
│          Request Flow                       │
├─────────────────────────────────────────────┤
│ 1. Client Request                           │
│    ├─ Header: X-Tenant-Code                 │
│    ├─ Subdomain: tenant.example.com         │
│    └─ Domain: custom.domain.com             │
│ 2. Tenant Middleware                        │
│    └─ Identify tenant from request          │
│ 3. Set request.state.tenant_*               │
│ 4. API Endpoint                             │
│    └─ Use current tenant context            │
│ 5. Response                                 │
└─────────────────────────────────────────────┘
```

---

## Backend 설정

### 1. 미들웨어 설정

미들웨어는 모든 요청에서 테넌트를 자동으로 식별합니다.

파일: `/backend/app/api/tenant_middleware.py`

테넌트 식별 순서:
1. `X-Tenant-Code` 헤더
2. 서브도메인 (host 헤더에서 추출)
3. 커스텀 도메인
4. 기본 테넌트 (fallback)

### 2. API 의존성

파일: `/backend/app/api/deps.py`

주요 함수:

```python
# 현재 요청의 테넌트 컨텍스트 획득
current_tenant = Depends(get_current_tenant)

# 헤더의 X-Tenant-Code로 테넌트 식별
tenant = Depends(get_tenant_from_header)

# 테넌트 존재 여부 확인
tenant = Depends(validate_tenant_exists)
```

### 3. API 엔드포인트

#### 관리자 API (Admin-only)

경로: `/api/v1/admin/tenants`

```bash
# 테넌트 생성
POST /api/v1/admin/tenants
{
  "tenant_code": "shop_a",
  "tenant_name": "Shop A",
  "description": "Online shopping mall A",
  "domain": "shopa.com",
  "subdomain": "shop-a",
  "admin_email": "admin@shopa.com",
  "admin_name": "Admin User",
  "settings": {
    "theme": "light",
    "language": "ko",
    "timezone": "Asia/Seoul",
    "primaryColor": "#1976d2",
    "companyName": "Shop A Inc."
  }
}

# 테넌트 목록 조회
GET /api/v1/admin/tenants?skip=0&limit=100

# 테넌트 상세 조회
GET /api/v1/admin/tenants/{tenant_id}

# 테넌트 코드로 조회
GET /api/v1/admin/tenants/by-code/{code}

# 테넌트 수정
PATCH /api/v1/admin/tenants/{tenant_id}
{
  "tenant_name": "Updated Name",
  "settings": { "theme": "dark" }
}

# 테넌트 삭제 (소프트 삭제)
DELETE /api/v1/admin/tenants/{tenant_id}

# 테넌트 설정 조회
GET /api/v1/admin/tenants/{tenant_id}/settings

# 테넌트 설정 수정
PATCH /api/v1/admin/tenants/{tenant_id}/settings
{
  "theme": "dark",
  "language": "en",
  "primaryColor": "#ff0000"
}
```

#### 현재 테넌트 정보 API

```bash
# 현재 테넌트 정보 조회 (미들웨어에서 식별)
GET /api/v1/tenants/current/info
{
  "tenant_id": 1,
  "tenant_code": "default",
  "tenant_name": "Default Tenant",
  "settings": { ... }
}
```

---

## Frontend 구현

### 1. 타입 정의

파일: `/frontend/src/types/tenant.ts`

```typescript
interface Tenant {
  id: number
  tenant_code: string
  tenant_name: string
  description?: string
  domain?: string
  subdomain?: string
  settings?: TenantSettings
  admin_email?: string
  admin_name?: string
  status: 'active' | 'suspended' | 'inactive'
  is_active: boolean
  is_deleted: boolean
  created_at: string
  updated_at: string
}

interface TenantSettings {
  theme?: 'default' | 'light' | 'dark'
  language?: 'ko' | 'en' | 'ja' | 'zh'
  timezone?: string
  primaryColor?: string
  companyName?: string
  logo?: string
  favicon?: string
}
```

### 2. API 클라이언트

파일: `/frontend/src/lib/api/tenants.ts`

```typescript
// 테넌트 목록 조회
const tenants = await fetchTenants(skip, limit, statusFilter)

// 테넌트 상세 조회
const tenant = await fetchTenant(id)

// 테넌트 코드로 조회
const tenant = await fetchTenantByCode(code)

// 테넌트 생성
const created = await createTenant(data)

// 테넌트 수정
const updated = await updateTenant(id, data)

// 테넌트 삭제
await deleteTenant(id)

// 설정 조회
const { settings } = await fetchTenantSettings(id)

// 설정 수정
const { settings } = await updateTenantSettings(id, data)
```

### 3. 관리자 UI 컴포넌트

파일: `/frontend/src/components/admin/TenantManager.tsx`

완전한 관리 UI를 제공합니다:

- 테넌트 목록 (검색 기능 포함)
- 테넌트 상세 조회
- 테넌트 생성/수정/삭제
- 탭 기반 UI (기본정보, 도메인설정, 테마설정)
- 위험 영역 (삭제 확인)

```typescript
import TenantManager from '@/components/admin/TenantManager'

export default function TenantsPage() {
  return <TenantManager />
}
```

---

## 사용 예시

### 1. 테넌트 생성

```javascript
// API 호출
const newTenant = await createTenant({
  tenant_code: 'acme_corp',
  tenant_name: 'ACME Corporation',
  description: 'Enterprise customer',
  domain: 'acme.com',
  admin_email: 'admin@acme.com',
  settings: {
    theme: 'light',
    language: 'en',
    companyName: 'ACME Corp',
    primaryColor: '#007bff'
  }
})

console.log('Created tenant:', newTenant.id)
```

### 2. 테넌트 접근

#### 헤더 사용 (API)
```bash
curl -H "X-Tenant-Code: acme_corp" \
  http://localhost:8000/api/v1/menus
```

#### 서브도메인 (웹)
```
http://acme_corp.example.com/admin
```

#### 커스텀 도메인
```
http://acme.com/admin
```

### 3. 테넌트 설정 수정

```javascript
const updated = await updateTenantSettings(tenantId, {
  theme: 'dark',
  primaryColor: '#000000',
  language: 'ko'
})

console.log('Updated settings:', updated.settings)
```

### 4. 현재 테넌트 정보 조회

```javascript
// 미들웨어에서 자동으로 식별된 테넌트
const currentTenant = await fetchCurrentTenant()

console.log(`Current tenant: ${currentTenant.tenant_name}`)
console.log(`Settings:`, currentTenant.settings)
```

---

## 보안 고려사항

### 1. 입력 검증

테넌트 코드 형식:
- 3-50자
- 영문 소문자, 숫자, 언더스코어만 허용
- 패턴: `^[a-z0-9_]{3,50}$`

```python
if not re.match(r"^[a-z0-9_]{3,50}$", tenant_code):
    raise ValueError("Invalid tenant code format")
```

### 2. 권한 확인

```python
# TODO: 슈퍼 관리자 권한만 테넌트 생성/삭제 가능
if current_user.role != "super_admin":
    raise HTTPException(status_code=403, detail="Only super admins can create tenants")
```

### 3. 테넌트 격리

- 각 테넌트의 데이터는 `tenant_id` FK로 격리
- 쿼리 시 항상 `tenant_id` 필터 적용 필요
- User, Menu, Board 등 모두 tenant_id 포함

### 4. 기본 테넌트 보호

```python
# 기본 테넌트는 비활성화/삭제 불가
if tenant.tenant_code == "default":
    raise HTTPException(status_code=400, detail="Cannot modify default tenant")
```

---

## 스키마 격리 (선택사항)

PostgreSQL 스키마를 사용한 완전한 격리:

```sql
-- 테넌트별 스키마 생성
CREATE SCHEMA IF NOT EXISTS tenant_1;
CREATE SCHEMA IF NOT EXISTS tenant_2;

-- 테이블을 테넌트 스키마에 생성
CREATE TABLE tenant_1.users (...)
CREATE TABLE tenant_2.users (...)
```

SQLAlchemy 설정:

```python
from sqlalchemy import create_engine, event
from sqlalchemy.engine.url import make_url

# 동적 스키마 지정
@event.listens_for(Engine, "connect")
def set_search_path(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    tenant_code = request.state.tenant_code  # 미들웨어에서 설정
    cursor.execute(f"SET search_path TO tenant_{tenant_code}")
    cursor.close()
```

---

## 마이그레이션

### 기본 테넌트 생성

Alembic으로 기본 테넌트를 자동 생성하도록 설정할 수 있습니다.

```python
# migrations/001_create_default_tenant.py
def upgrade():
    # Insert default tenant
    op.execute("""
        INSERT INTO tenants (
            tenant_code, tenant_name, description,
            created_by, updated_by, status
        ) VALUES (
            'default', 'Default Tenant', 'System default tenant',
            'system', 'system', 'active'
        )
        ON CONFLICT (tenant_code) DO NOTHING;
    """)

def downgrade():
    op.execute("DELETE FROM tenants WHERE tenant_code = 'default';")
```

실행:

```bash
cd backend
alembic upgrade head
```

---

## 테스트

### 테넌트 생성 테스트

```python
# backend/tests/test_tenants.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_tenant():
    response = client.post(
        "/api/v1/admin/tenants",
        json={
            "tenant_code": "test_tenant",
            "tenant_name": "Test Tenant",
            "admin_email": "admin@test.com"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["tenant_code"] == "test_tenant"

def test_get_tenant_by_header():
    response = client.get(
        "/api/v1/tenants/current/info",
        headers={"X-Tenant-Code": "default"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tenant_code"] == "default"
```

실행:

```bash
cd backend
pytest tests/test_tenants.py -v
```

---

## 문제 해결

### 1. 테넌트를 찾을 수 없음

**문제**: `GET /api/v1/tenants/current/info` 응답이 404

**해결**:
1. 데이터베이스에 기본 테넌트 확인
2. 테넌트 코드 확인 (대소문자 구분)
3. 미들웨어가 올바르게 실행되었는지 확인

```bash
# PostgreSQL에서 확인
SELECT * FROM tenants WHERE tenant_code = 'default';
```

### 2. 중복 도메인 에러

**문제**: `POST /api/v1/admin/tenants` 응답이 409 Conflict

**해결**:
1. 도메인이 이미 사용 중인지 확인
2. 도메인을 NULL로 설정하거나 다른 도메인 사용

```bash
# PostgreSQL에서 확인
SELECT tenant_code, domain FROM tenants WHERE domain = 'example.com';
```

### 3. 권한 오류

**문제**: `POST /api/v1/admin/tenants` 응답이 403 Forbidden

**해결**:
- 슈퍼 관리자 권한 확인 필요 (현재는 주석 처리됨)
- JWT 토큰에서 역할 확인

---

## 다음 단계

1. **인증/권한**: JWT를 사용한 사용자 인증 및 역할 기반 접근 제어 구현
2. **감사 로그**: 테넌트 변경사항 기록
3. **백업/복구**: 테넌트별 데이터 백업 전략
4. **성능**: 테넌트별 캐싱 전략
5. **모니터링**: 테넌트별 리소스 사용량 추적

---

## 파일 구조

```
backend/
├── app/
│   ├── api/
│   │   ├── tenant_middleware.py    # 테넌트 식별 미들웨어
│   │   ├── deps.py                 # API 의존성
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── shared.py       # 기본 CRUD 엔드포인트
│   │           └── tenants.py      # 관리자 테넌트 엔드포인트
│   ├── models/
│   │   └── shared.py               # Tenant 모델 포함
│   ├── schemas/
│   │   └── shared.py               # Tenant 스키마 포함
│   ├── services/
│   │   └── shared.py               # TenantService
│   └── main.py                     # 미들웨어 등록
│
frontend/
├── src/
│   ├── types/
│   │   └── tenant.ts               # Tenant 타입 정의
│   ├── lib/
│   │   └── api/
│   │       └── tenants.ts          # Tenant API 클라이언트
│   └── components/
│       └── admin/
│           └── TenantManager.tsx   # 관리자 UI
```

---

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
