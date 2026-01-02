# 테넌트 관리 시스템 (Tenant Manager)

FastAPI + SQLAlchemy 2.0 기반의 멀티테넌시(멀티사이트) 관리 시스템

> **상태**: 구현 완료 ✓
> **버전**: 1.0.0
> **생성일**: 2026-01-03

---

## 개요

테넌트 관리 시스템은 하나의 애플리케이션에서 여러 개의 독립적인 사이트/조직(테넌트)을 운영할 수 있도록 합니다.

각 테넌트는:
- 자신의 도메인(서브도메인 또는 커스텀 도메인)을 가짐
- 독립적인 테마, 로고, 설정을 가짐
- 관리자를 지정할 수 있음
- 테넌트 ID로 다른 테이블과 연결됨

---

## 기술 스택

- **Framework**: FastAPI 0.109+
- **ORM**: SQLAlchemy 2.0 + AsyncIO
- **Database**: PostgreSQL 15+
- **Validation**: Pydantic v2
- **Language**: Python 3.10+

---

## 핵심 기능

### 1. 테넌트 CRUD

```bash
# 테넌트 목록 조회
GET /api/v1/tenants?skip=0&limit=20&is_active=true

# 테넌트 상세 조회
GET /api/v1/tenants/{tenant_id}

# 테넌트 생성
POST /api/v1/tenants

# 테넌트 수정
PUT /api/v1/tenants/{tenant_id}

# 테넌트 삭제 (소프트 삭제)
DELETE /api/v1/tenants/{tenant_id}
```

### 2. 도메인 설정

테넌트를 식별하는 방식:

| 방식 | 예시 | 설명 |
|------|------|------|
| 서브도메인 | `shopA.example.com` | 서브도메인으로 식별 |
| 커스텀 도메인 | `shopA.com` | 완전한 도메인으로 식별 |
| 헤더 | `X-Tenant-ID: shop_a` | API 요청 시 헤더로 식별 |

### 3. 테마/로고/설정

```json
{
  "theme": "default",
  "logo": "/uploads/logo.png",
  "favicon": "/uploads/favicon.ico",
  "language": "ko",
  "timezone": "Asia/Seoul",
  "primary_color": "#1976d2",
  "company_name": "회사명",
  "contact_email": "contact@example.com",
  "contact_phone": "010-1234-5678"
}
```

### 4. 테넌트 설정 API

```bash
# 테넌트 설정 조회
GET /api/v1/tenants/{tenant_id}/settings

# 테넌트 설정 수정 (부분 업데이트)
PATCH /api/v1/tenants/{tenant_id}/settings
```

---

## 데이터베이스 스키마

### tenants 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | BIGINT | PK, Auto Increment |
| tenant_code | VARCHAR(50) | 고유, 테넌트 코드 (시스템 식별용) |
| tenant_name | VARCHAR(100) | 테넌트명 (사이트명) |
| description | TEXT | 설명 |
| domain | VARCHAR(255) | 커스텀 도메인 |
| subdomain | VARCHAR(100) | 서브도메인 |
| settings | JSON | 테넌트 설정 (theme, logo 등) |
| admin_email | VARCHAR(255) | 관리자 이메일 |
| admin_name | VARCHAR(100) | 관리자 이름 |
| created_at | DATETIME | 생성일시 |
| created_by | VARCHAR(100) | 생성자 |
| updated_at | DATETIME | 수정일시 |
| updated_by | VARCHAR(100) | 수정자 |
| is_active | BOOLEAN | 활성 여부 |
| is_deleted | BOOLEAN | 소프트 삭제 여부 |

---

## API 엔드포인트 상세

### 테넌트 목록 조회

```http
GET /api/v1/tenants?skip=0&limit=20&is_active=true
```

**Query Parameters:**
- `skip` (int, 기본값: 0): 스킵할 개수
- `limit` (int, 기본값: 20, 최대: 100): 조회할 개수
- `is_active` (bool, 선택): 활성 여부 필터링

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "tenant_code": "shop_a",
      "tenant_name": "쇼핑몰 A",
      "description": "쇼핑몰",
      "domain": "shopa.com",
      "subdomain": "shop_a",
      "settings": {
        "theme": "default",
        "logo": "/uploads/logo.png",
        "language": "ko"
      },
      "admin_email": "admin@shopa.com",
      "admin_name": "관리자",
      "created_at": "2026-01-03T10:00:00",
      "created_by": "system",
      "updated_at": "2026-01-03T10:00:00",
      "updated_by": null,
      "is_active": true,
      "is_deleted": false
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

---

### 테넌트 생성

```http
POST /api/v1/tenants
Content-Type: application/json

{
  "tenant_code": "shop_b",
  "tenant_name": "쇼핑몰 B",
  "description": "의류 쇼핑몰",
  "domain": "shopb.com",
  "subdomain": "shop_b",
  "admin_email": "admin@shopb.com",
  "admin_name": "관리자",
  "settings": {
    "theme": "dark",
    "logo": "/uploads/shopb-logo.png",
    "language": "ko",
    "timezone": "Asia/Seoul",
    "primary_color": "#ff6b6b"
  }
}
```

**필드 검증:**
- `tenant_code`: 영문 소문자, 숫자, 언더스코어만 사용 가능
- 중복된 `tenant_code`는 생성 불가
- `domain`: 유효한 도메인 형식
- `admin_email`: 유효한 이메일 형식

**응답 (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "tenant_code": "shop_b",
    "tenant_name": "쇼핑몰 B",
    ...
  },
  "message": "테넌트가 생성되었습니다."
}
```

---

### 테넌트 수정

```http
PUT /api/v1/tenants/{tenant_id}
Content-Type: application/json

{
  "tenant_name": "쇼핑몰 B (수정)",
  "settings": {
    "theme": "light",
    "primary_color": "#4ecdc4"
  },
  "is_active": true
}
```

**주의:**
- `tenant_code`는 수정 불가
- 설정은 전체 교체됨 (부분 업데이트는 `/settings` 엔드포인트 사용)

---

### 테넌트 설정 조회

```http
GET /api/v1/tenants/{tenant_id}/settings
```

**응답:**
```json
{
  "success": true,
  "data": {
    "theme": "default",
    "logo": "/uploads/logo.png",
    "favicon": "/uploads/favicon.ico",
    "language": "ko",
    "timezone": "Asia/Seoul",
    "primary_color": "#1976d2",
    "company_name": "회사명",
    "contact_email": "contact@example.com",
    "contact_phone": "010-1234-5678"
  }
}
```

---

### 테넌트 설정 수정 (부분 업데이트)

```http
PATCH /api/v1/tenants/{tenant_id}/settings
Content-Type: application/json

{
  "logo": "/uploads/new-logo.png",
  "primary_color": "#5eb3d1",
  "theme": "dark"
}
```

**장점:**
- 기존 설정을 유지하면서 필요한 부분만 업데이트
- 설정을 완전히 교체하지 않음

**응답:**
```json
{
  "success": true,
  "data": {
    "theme": "dark",
    "logo": "/uploads/new-logo.png",
    "favicon": "/uploads/favicon.ico",
    "language": "ko",
    "timezone": "Asia/Seoul",
    "primary_color": "#5eb3d1",
    "company_name": "회사명",
    "contact_email": "contact@example.com",
    "contact_phone": "010-1234-5678"
  },
  "message": "테넌트 설정이 수정되었습니다."
}
```

---

### 테넌트 삭제

```http
DELETE /api/v1/tenants/{tenant_id}
```

**주의:**
- 소프트 삭제 (물리적 삭제 X)
- 기본 테넌트 (default)는 삭제 불가
- `is_deleted = true`로 마크됨

**응답:**
```json
{
  "success": true,
  "message": "테넌트가 삭제되었습니다."
}
```

---

## 테넌트 감지 (Detection)

### 우선순위

1. **X-Tenant-ID 헤더** (가장 높음)
   ```bash
   curl -H "X-Tenant-ID: shop_a" http://example.com/api/v1/items
   ```

2. **서브도메인**
   ```
   shop_a.example.com → tenant_code: shop_a
   ```

3. **커스텀 도메인**
   ```
   shop_a.com → tenant_code: shop_a
   ```

4. **세션**
   ```python
   request.state.tenant_code
   ```

5. **기본값** (가장 낮음)
   ```
   default
   ```

### 미들웨어 통합

`TenantDetectionMiddleware`가 자동으로 테넌트를 감지하고 `request.state`에 설정합니다:

```python
# 컨트롤러에서 테넌트 접근
from fastapi import Request

async def get_items(request: Request):
    tenant = request.state.tenant
    tenant_id = request.state.tenant_id
    tenant_code = request.state.tenant_code
    settings = request.state.tenant_settings
```

---

## 의존성 주입 (Dependency Injection)

FastAPI의 의존성 주입을 사용하여 테넌트 정보를 획득합니다:

```python
from fastapi import Depends
from app.api.deps import (
    get_current_tenant,
    get_current_tenant_id,
    get_current_tenant_code,
    get_current_tenant_settings,
)
from app.models.shared import Tenant

@router.get("/items")
async def list_items(
    tenant: Tenant = Depends(get_current_tenant),
    tenant_id: int = Depends(get_current_tenant_id),
    tenant_code: str = Depends(get_current_tenant_code),
    settings: dict = Depends(get_current_tenant_settings),
):
    # 현재 테넌트의 아이템 조회
    return {"tenant_code": tenant_code, "items": [...]}
```

---

## 에러 응답

### 400 Bad Request

```json
{
  "success": false,
  "error_code": "INVALID_INPUT",
  "message": "테넌트 코드는 영문 소문자, 숫자, 언더스코어만 사용 가능합니다."
}
```

### 404 Not Found

```json
{
  "success": false,
  "error_code": "NOT_FOUND",
  "message": "테넌트를 찾을 수 없습니다."
}
```

### 409 Conflict

```json
{
  "success": false,
  "error_code": "CONFLICT",
  "message": "이미 존재하는 테넌트 코드입니다."
}
```

### 500 Internal Server Error

```json
{
  "success": false,
  "error_code": "INTERNAL_ERROR",
  "message": "테넌트를 생성하는데 실패했습니다."
}
```

---

## 보안 (Security)

### 입력 검증

- `tenant_code`: 정규식 검증 (`^[a-z0-9_]+$`)
- `domain`: 유효한 도메인 형식 검증
- `email`: RFC 5322 기본 형식 검증
- XSS 방지: 모든 문자열 입력 정제

### 권한 (Authorization)

> **주의**: 현재는 권한 검증이 구현되지 않았습니다.
> auth-backend 에이전트에서 JWT 검증을 추가하면 다음과 같이 사용합니다:

```python
# 슈퍼 관리자만 테넌트 생성 가능
@router.post("",
    dependencies=[Depends(require_role("super_admin"))]
)
async def create_tenant(...):
    ...

# 관리자 이상은 테넌트 수정 가능
@router.put("/{tenant_id}",
    dependencies=[Depends(require_role("admin", "super_admin"))]
)
async def update_tenant(...):
    ...
```

### 데이터베이스

- **Parameterized Query**: SQLAlchemy ORM 사용으로 SQL Injection 방지
- **Soft Delete**: 기본 테넌트 삭제 방지

---

## 파일 구조

```
backend/app/
├── api/
│   ├── deps.py                    # 의존성 (테넌트 관련)
│   ├── tenant_middleware.py       # 테넌트 감지 미들웨어
│   └── v1_tenants.py             # 테넌트 API 엔드포인트
├── models/
│   └── shared.py                 # Tenant 모델 (이미 구현됨)
├── schemas/
│   └── shared.py                 # TenantCreate, TenantUpdate, TenantResponse 등
├── services/
│   └── shared.py                 # TenantService
└── main.py                       # FastAPI 앱 (미들웨어, 라우터 등록)
```

---

## 사용 예시

### Python

```python
import httpx

# 테넌트 생성
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/tenants",
        json={
            "tenant_code": "shop_a",
            "tenant_name": "쇼핑몰 A",
            "subdomain": "shop_a",
            "settings": {
                "theme": "default",
                "logo": "/uploads/logo.png"
            }
        }
    )
    print(response.json())
```

### cURL

```bash
# 테넌트 생성
curl -X POST http://localhost:8000/api/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_code": "shop_a",
    "tenant_name": "쇼핑몰 A",
    "subdomain": "shop_a"
  }'

# 테넌트 목록 조회
curl http://localhost:8000/api/v1/tenants?limit=10

# 테넌트 설정 조회
curl http://localhost:8000/api/v1/tenants/1/settings

# 테넌트 설정 수정
curl -X PATCH http://localhost:8000/api/v1/tenants/1/settings \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "dark",
    "primary_color": "#ffffff"
  }'

# 헤더로 테넌트 지정
curl -H "X-Tenant-ID: shop_a" http://localhost:8000/api/v1/items
```

---

## 테스트

### 단위 테스트 (예시)

```python
# tests/test_tenants.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_tenants():
    response = client.get("/api/v1/tenants")
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_create_tenant():
    response = client.post(
        "/api/v1/tenants",
        json={
            "tenant_code": "test_tenant",
            "tenant_name": "Test Tenant",
            "subdomain": "test"
        }
    )
    assert response.status_code == 201
    assert response.json()["success"] == True

def test_invalid_tenant_code():
    response = client.post(
        "/api/v1/tenants",
        json={
            "tenant_code": "INVALID-CODE",  # 대문자 불허
            "tenant_name": "Test"
        }
    )
    assert response.status_code == 400
```

---

## 다음 단계

1. **인증 시스템 통합**
   ```bash
   Use auth-backend --init --type=phone
   ```

2. **카테고리 관리 추가**
   ```bash
   Use category-manager --init
   ```

3. **게시판 시스템 구축**
   ```bash
   Use board-generator --init
   ```

---

## 참고 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 문서](https://docs.sqlalchemy.org/en/20/)
- [Pydantic 공식 문서](https://docs.pydantic.dev/)
- [CLAUDE.md](../CLAUDE.md) - 프로젝트 가이드

---

## 라이선스

프로젝트의 라이선스를 따릅니다.
