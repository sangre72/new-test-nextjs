# 테넌트 관리 시스템 구현 완료

**상태**: ✅ 완료
**생성일**: 2026-01-03
**버전**: 1.0.0

---

## 구현된 파일 목록

### Backend (FastAPI + SQLAlchemy 2.0)

#### 1. 스키마 (Schemas)
- **파일**: `backend/app/schemas/shared.py`
- **내용**:
  - `TenantSettings`: 테넌트 설정 스키마
  - `TenantCreate`: 테넌트 생성 요청 스키마
  - `TenantUpdate`: 테넌트 수정 요청 스키마
  - `TenantResponse`: 테넌트 응답 스키마

#### 2. 서비스 (Services)
- **파일**: `backend/app/services/shared.py`
- **클래스**: `TenantService`
- **메서드**:
  - `get_tenant_by_code()`: 코드로 테넌트 조회
  - `get_tenant_by_id()`: ID로 테넌트 조회
  - `get_tenant_by_domain()`: 도메인으로 테넌트 조회
  - `list_tenants()`: 테넌트 목록 조회 (페이징)
  - `create_tenant()`: 테넌트 생성
  - `update_tenant()`: 테넌트 수정
  - `delete_tenant()`: 테넌트 삭제 (소프트 삭제)
  - `get_tenant_settings()`: 설정 조회
  - `update_tenant_settings()`: 설정 수정 (부분 업데이트)

#### 3. API 엔드포인트 (Endpoints)
- **파일**: `backend/app/api/v1_tenants.py`
- **라우터**: `/api/v1/tenants`
- **엔드포인트**:
  - `GET /api/v1/tenants`: 테넌트 목록
  - `GET /api/v1/tenants/{tenant_id}`: 테넌트 상세
  - `POST /api/v1/tenants`: 테넌트 생성
  - `PUT /api/v1/tenants/{tenant_id}`: 테넌트 수정
  - `DELETE /api/v1/tenants/{tenant_id}`: 테넌트 삭제
  - `GET /api/v1/tenants/{tenant_id}/settings`: 설정 조회
  - `PATCH /api/v1/tenants/{tenant_id}/settings`: 설정 수정

#### 4. 미들웨어 (Middleware)
- **파일**: `backend/app/api/tenant_middleware.py`
- **클래스**: `TenantDetectionMiddleware`
- **기능**:
  - X-Tenant-ID 헤더로 테넌트 감지
  - 서브도메인으로 테넌트 감지
  - 커스텀 도메인으로 테넌트 감지
  - request.state에 테넌트 정보 설정

#### 5. 의존성 (Dependencies)
- **파일**: `backend/app/api/deps.py` (업데이트)
- **함수**:
  - `get_current_tenant()`: 현재 테넌트 획득
  - `get_current_tenant_id()`: 현재 테넌트 ID 획득
  - `get_current_tenant_code()`: 현재 테넌트 코드 획득
  - `get_current_tenant_settings()`: 현재 테넌트 설정 획득

#### 6. 메인 앱 (Main Application)
- **파일**: `backend/app/main.py` (업데이트)
- **변경사항**:
  - 테넌트 감지 미들웨어 등록
  - 테넌트 API 라우터 등록

#### 7. 문서 (Documentation)
- **파일**: `backend/TENANT_MANAGER.md`
- **내용**:
  - 전체 가이드 문서
  - API 엔드포인트 상세 설명
  - 데이터베이스 스키마
  - 테넌트 감지 방식
  - 사용 예시
  - 보안 정보

#### 8. 테스트 (Tests)
- **파일**: `backend/tests/test_tenants.py`
- **테스트 클래스**:
  - `TestTenantCRUD`: CRUD 테스트
  - `TestTenantSettings`: 설정 테스트
  - `TestTenantFiltering`: 필터링 및 페이징 테스트

### Frontend (Next.js + TypeScript)

#### 1. 타입 정의 (Types)
- **파일**: `frontend/src/types/tenant.ts`
- **타입**:
  - `Tenant`: 테넌트 정보
  - `TenantSettings`: 테넌트 설정
  - `TenantCreateRequest`: 생성 요청
  - `TenantUpdateRequest`: 수정 요청
  - `TenantListResponse`: 목록 응답
  - `TenantDetailResponse`: 상세 응답
  - `TenantSettingsResponse`: 설정 응답

#### 2. API 클라이언트 (API Client)
- **파일**: `frontend/src/lib/api/tenants.ts`
- **함수**:
  - `fetchTenants()`: 테넌트 목록 조회
  - `fetchTenant()`: 테넌트 상세 조회
  - `createTenant()`: 테넌트 생성
  - `updateTenant()`: 테넌트 수정
  - `deleteTenant()`: 테넌트 삭제
  - `fetchTenantSettings()`: 설정 조회
  - `updateTenantSettings()`: 설정 수정

---

## 핵심 기능

### 1. 테넌트 CRUD

```bash
# 테넌트 생성
POST /api/v1/tenants
{
  "tenant_code": "shop_a",
  "tenant_name": "쇼핑몰 A",
  "subdomain": "shop_a",
  "settings": {
    "theme": "default",
    "logo": "/uploads/logo.png"
  }
}

# 테넌트 목록 조회
GET /api/v1/tenants?skip=0&limit=20

# 테넌트 상세 조회
GET /api/v1/tenants/{tenant_id}

# 테넌트 수정
PUT /api/v1/tenants/{tenant_id}
{
  "tenant_name": "쇼핑몰 A (수정)",
  "settings": { "theme": "dark" }
}

# 테넌트 삭제
DELETE /api/v1/tenants/{tenant_id}
```

### 2. 도메인 설정

- **서브도메인**: `shop_a.example.com`
- **커스텀 도메인**: `shop_a.com`
- **헤더**: `X-Tenant-ID: shop_a`

### 3. 테마/로고 설정

```json
{
  "theme": "default",
  "logo": "/uploads/logo.png",
  "favicon": "/uploads/favicon.ico",
  "language": "ko",
  "timezone": "Asia/Seoul",
  "primary_color": "#1976d2",
  "company_name": "회사명"
}
```

### 4. 테넌트 감지

자동으로 현재 요청의 테넌트를 감지합니다 (우선순위):

1. X-Tenant-ID 헤더
2. 서브도메인
3. 커스텀 도메인
4. 세션
5. 기본값 (default)

### 5. 입력 검증 (Security)

- `tenant_code`: 정규식 검증 (`^[a-z0-9_]+$`)
- `domain`: 유효한 도메인 형식
- `email`: RFC 5322 형식
- XSS 방지, SQL Injection 방지

---

## 사용 방법

### Python/FastAPI

```python
from fastapi import Depends
from app.api.deps import get_current_tenant, get_current_tenant_id
from app.models.shared import Tenant

@router.get("/items")
async def list_items(
    tenant: Tenant = Depends(get_current_tenant),
    tenant_id: int = Depends(get_current_tenant_id)
):
    # 현재 테넌트의 아이템만 조회
    return {"tenant_code": tenant.tenant_code, "items": [...]}
```

### TypeScript/React

```typescript
import { fetchTenants, createTenant, updateTenantSettings } from '@/lib/api/tenants';

// 테넌트 목록 조회
const response = await fetchTenants(0, 20);
console.log(response.data);

// 테넌트 생성
const result = await createTenant({
  tenant_code: "shop_b",
  tenant_name": "쇼핑몰 B",
  subdomain": "shop_b"
});

// 테넌트 설정 수정
const updated = await updateTenantSettings(1, {
  theme: "dark",
  primary_color": "#ffffff"
});
```

---

## 데이터베이스 스키마

### tenants 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | BIGINT | PK |
| tenant_code | VARCHAR(50) | 고유, 테넌트 코드 |
| tenant_name | VARCHAR(100) | 테넌트 이름 |
| description | TEXT | 설명 |
| domain | VARCHAR(255) | 커스텀 도메인 |
| subdomain | VARCHAR(100) | 서브도메인 |
| settings | JSON | 테넌트 설정 |
| admin_email | VARCHAR(255) | 관리자 이메일 |
| admin_name | VARCHAR(100) | 관리자 이름 |
| created_at | DATETIME | 생성일시 |
| created_by | VARCHAR(100) | 생성자 |
| updated_at | DATETIME | 수정일시 |
| updated_by | VARCHAR(100) | 수정자 |
| is_active | BOOLEAN | 활성 여부 |
| is_deleted | BOOLEAN | 소프트 삭제 여부 |

---

## 테스트 실행

```bash
# 모든 테스트 실행
pytest backend/tests/test_tenants.py -v

# 특정 테스트 클래스만 실행
pytest backend/tests/test_tenants.py::TestTenantCRUD -v

# 특정 테스트만 실행
pytest backend/tests/test_tenants.py::TestTenantCRUD::test_create_tenant_success -v
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

---

## 보안 (Security)

✅ 완료된 항목:

- 입력 검증 (tenant_code, domain, email)
- XSS 방지
- SQL Injection 방지 (Parameterized Query)
- 기본 테넌트 삭제 방지 (Soft Delete)

⏳ 구현 예정 (auth-backend):

- JWT 토큰 검증
- 권한 제어 (슈퍼 관리자, 관리자)
- RBAC (Role-Based Access Control)

---

## 다음 단계

### 1. 인증 시스템 통합

```bash
Use auth-backend --init --type=phone
```

이후 다음과 같이 권한을 추가할 수 있습니다:

```python
@router.post("", dependencies=[Depends(require_role("super_admin"))])
async def create_tenant(...):
    ...
```

### 2. 카테고리 관리

```bash
Use category-manager --init
```

### 3. 게시판 시스템

```bash
Use board-generator --init
```

### 4. 메뉴 관리

```bash
Use menu-backend --init
Use menu-frontend --init
```

---

## 파일 요약

### Backend 파일 (7개)

1. `backend/app/schemas/shared.py` - 스키마 (업데이트)
2. `backend/app/services/shared.py` - 서비스 (업데이트)
3. `backend/app/api/v1_tenants.py` - API 엔드포인트 (신규)
4. `backend/app/api/tenant_middleware.py` - 미들웨어 (신규)
5. `backend/app/api/deps.py` - 의존성 (업데이트)
6. `backend/app/main.py` - 메인 앱 (업데이트)
7. `backend/TENANT_MANAGER.md` - 문서 (신규)
8. `backend/tests/test_tenants.py` - 테스트 (신규)

### Frontend 파일 (2개)

1. `frontend/src/types/tenant.ts` - 타입 정의 (신규)
2. `frontend/src/lib/api/tenants.ts` - API 클라이언트 (신규)

---

## 주요 특징

### 1. 멀티테넌시 지원

- 하나의 애플리케이션에서 여러 사이트 운영
- 테넌트별 독립적인 도메인, 설정, 데이터

### 2. 유연한 도메인 설정

- 서브도메인 방식 (shop_a.example.com)
- 커스텀 도메인 방식 (shop_a.com)
- 헤더 기반 식별 (X-Tenant-ID)

### 3. 자동 테넌트 감지

- 미들웨어가 자동으로 현재 테넌트 감지
- 의존성 주입으로 간편하게 접근

### 4. 설정 관리

- JSON 기반 유연한 설정
- 부분 업데이트 지원 (PATCH)

### 5. 보안

- 입력 검증
- XSS, SQL Injection 방지
- 기본 테넌트 보호

---

## 성능 고려사항

### 1. 인덱스

```sql
-- 테넌트 코드 인덱스
CREATE INDEX idx_tenant_code ON tenants(tenant_code);

-- 도메인 인덱스
CREATE INDEX idx_domain ON tenants(domain);
CREATE INDEX idx_subdomain ON tenants(subdomain);
```

### 2. 캐싱

테넌트 정보는 자주 조회되므로 Redis 캐시 추가 권장:

```python
@cache_key("tenant:{tenant_code}")
@cache_ttl(3600)
async def get_tenant_by_code(session, tenant_code):
    ...
```

### 3. 페이징

대량의 테넌트가 있을 경우 페이징 필수:

```python
GET /api/v1/tenants?skip=0&limit=20
```

---

## 라이선스

프로젝트의 라이선스를 따릅니다.

---

## 참고 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 문서](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2 문서](https://docs.pydantic.dev/)
- [CLAUDE.md](CLAUDE.md) - 프로젝트 가이드

---

## 완료 체크리스트

- [x] Tenant 모델 확인 (shared-schema에서 이미 생성)
- [x] TenantSettings 스키마 추가
- [x] TenantCreate/Update/Response 스키마 구현
- [x] TenantService 구현 (CRUD, 설정)
- [x] 테넌트 API 엔드포인트 구현
- [x] 테넌트 감지 미들웨어 구현
- [x] 의존성 주입 함수 구현
- [x] 입력 검증 (tenant_code, domain, email)
- [x] 에러 처리 (400, 404, 409, 500)
- [x] 메인 앱 통합 (라우터, 미들웨어)
- [x] Frontend 타입 정의
- [x] Frontend API 클라이언트
- [x] 테스트 코드 작성
- [x] 문서 작성 (TENANT_MANAGER.md)

---

**구현 완료!** 🎉

이제 인증 시스템을 추가하려면:
```bash
Use auth-backend --init --type=phone
```
