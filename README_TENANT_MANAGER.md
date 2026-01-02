# 테넌트 관리 시스템 (Tenant Manager)

FastAPI + PostgreSQL + Next.js 기반의 **멀티테넌시 SaaS 플랫폼** 구현

---

## 프로젝트 정보

| 항목 | 설명 |
|------|------|
| **상태** | ✅ 구현 완료 |
| **버전** | 1.0.0 |
| **생성일** | 2026-01-03 |
| **기술스택** | FastAPI + SQLAlchemy 2.0 + PostgreSQL + Next.js |
| **코딩규칙** | [CLAUDE.md](CLAUDE.md) 참조 |

---

## 핵심 기능

### 1️⃣ 테넌트 CRUD (Create, Read, Update, Delete)

```bash
# 테넌트 목록 조회
GET /api/v1/tenants?skip=0&limit=20

# 테넌트 생성
POST /api/v1/tenants

# 테넌트 상세 조회
GET /api/v1/tenants/{tenant_id}

# 테넌트 수정
PUT /api/v1/tenants/{tenant_id}

# 테넌트 삭제 (소프트 삭제)
DELETE /api/v1/tenants/{tenant_id}
```

### 2️⃣ 도메인 설정 (Domain Configuration)

테넌트를 식별하는 3가지 방식 지원:

| 방식 | 예시 | 설명 |
|------|------|------|
| **서브도메인** | `shop_a.example.com` | 서브도메인으로 자동 감지 |
| **커스텀 도메인** | `shop_a.com` | 완전한 도메인으로 감지 |
| **헤더 기반** | `X-Tenant-ID: shop_a` | API 요청 헤더로 지정 |

### 3️⃣ 테마/로고 설정 (Theme & Branding)

```json
{
  "theme": "default",           // 테마 (default, dark, light)
  "logo": "/uploads/logo.png",  // 로고 URL
  "favicon": "/uploads/favicon.ico",
  "language": "ko",              // 언어 (ko, en, ja, zh)
  "timezone": "Asia/Seoul",      // 시간대
  "primary_color": "#1976d2",    // 기본 색상
  "company_name": "회사명",      // 회사명
  "contact_email": "contact@example.com",
  "contact_phone": "010-1234-5678"
}
```

### 4️⃣ 자동 테넌트 감지 (Auto Tenant Detection)

미들웨어가 요청에서 자동으로 테넌트를 감지합니다 (우선순위):

1. **X-Tenant-ID 헤더** (명시적 지정)
2. **서브도메인** (siteA.example.com)
3. **커스텀 도메인** (siteA.com)
4. **세션** (request.state)
5. **기본값** (default)

```python
# FastAPI 컨트롤러에서 현재 테넌트 접근
async def get_items(
    tenant: Tenant = Depends(get_current_tenant),
    tenant_id: int = Depends(get_current_tenant_id)
):
    # 현재 테넌트의 데이터만 조회
    pass
```

---

## 프로젝트 구조

### Backend (FastAPI)

```
backend/app/
├── api/
│   ├── deps.py                    # 의존성 (테넌트 함수 포함)
│   ├── tenant_middleware.py       # 테넌트 감지 미들웨어 [신규]
│   └── v1_tenants.py             # 테넌트 API 엔드포인트 [신규]
├── models/
│   └── shared.py                 # Tenant 모델 (이미 구현됨)
├── schemas/
│   └── shared.py                 # 요청/응답 스키마 [업데이트]
├── services/
│   └── shared.py                 # TenantService [업데이트]
└── main.py                       # FastAPI 앱 [업데이트]
```

### Frontend (Next.js)

```
frontend/src/
├── types/
│   └── tenant.ts                # TypeScript 타입 정의 [신규]
└── lib/api/
    └── tenants.ts               # API 클라이언트 [신규]
```

### Documentation

```
├── TENANT_IMPLEMENTATION.md     # 구현 상세 설명 [신규]
├── backend/TENANT_MANAGER.md    # 테넌트 시스템 가이드 [신규]
└── README_TENANT_MANAGER.md    # 이 파일
```

---

## 생성된 파일 (11개)

### Backend (8개)

| 파일 | 설명 | 상태 |
|------|------|------|
| `app/api/v1_tenants.py` | API 엔드포인트 (CRUD + 설정) | 신규 |
| `app/api/tenant_middleware.py` | 테넌트 감지 미들웨어 | 신규 |
| `app/api/deps.py` | 의존성 주입 함수 | 업데이트 |
| `app/services/shared.py` | TenantService | 업데이트 |
| `app/schemas/shared.py` | 요청/응답 스키마 | 업데이트 |
| `app/main.py` | FastAPI 앱 통합 | 업데이트 |
| `TENANT_MANAGER.md` | 상세 가이드 문서 | 신규 |
| `tests/test_tenants.py` | 단위 테스트 | 신규 |

### Frontend (2개)

| 파일 | 설명 | 상태 |
|------|------|------|
| `src/types/tenant.ts` | TypeScript 타입 정의 | 신규 |
| `src/lib/api/tenants.ts` | API 클라이언트 | 신규 |

### Documentation (1개)

| 파일 | 설명 |
|------|------|
| `TENANT_IMPLEMENTATION.md` | 구현 요약 |

---

## API 엔드포인트

### 테넌트 CRUD

```http
# 목록 조회
GET /api/v1/tenants?skip=0&limit=20&is_active=true

# 상세 조회
GET /api/v1/tenants/{tenant_id}

# 생성
POST /api/v1/tenants
Content-Type: application/json
{
  "tenant_code": "shop_a",
  "tenant_name": "쇼핑몰 A",
  "subdomain": "shop_a",
  "settings": { "theme": "default" }
}

# 수정
PUT /api/v1/tenants/{tenant_id}
{
  "tenant_name": "쇼핑몰 A (수정)",
  "is_active": true
}

# 삭제
DELETE /api/v1/tenants/{tenant_id}
```

### 테넌트 설정

```http
# 설정 조회
GET /api/v1/tenants/{tenant_id}/settings

# 설정 수정 (부분 업데이트)
PATCH /api/v1/tenants/{tenant_id}/settings
{
  "theme": "dark",
  "primary_color": "#ffffff"
}
```

---

## 데이터베이스 스키마

### tenants 테이블

```sql
CREATE TABLE tenants (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  tenant_code VARCHAR(50) NOT NULL UNIQUE,  -- 테넌트 코드
  tenant_name VARCHAR(100) NOT NULL,        -- 테넌트 이름
  description TEXT,
  domain VARCHAR(255) INDEX,                -- 커스텀 도메인
  subdomain VARCHAR(100) INDEX,             -- 서브도메인
  settings JSON,                            -- 테마, 로고 등
  admin_email VARCHAR(255),
  admin_name VARCHAR(100),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(100),
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(100),
  is_active BOOLEAN DEFAULT TRUE,
  is_deleted BOOLEAN DEFAULT FALSE
);
```

---

## 사용 예시

### Python (FastAPI)

```python
from app.api.deps import get_current_tenant, get_current_tenant_id
from app.models.shared import Tenant

@router.get("/items")
async def list_items(
    tenant: Tenant = Depends(get_current_tenant),
    tenant_id: int = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """현재 테넌트의 아이템 목록"""
    # tenant.id, tenant.tenant_code, tenant.settings 등 접근 가능
    result = await session.execute(
        select(Item).where(Item.tenant_id == tenant_id)
    )
    return result.scalars().all()
```

### TypeScript (React)

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import { fetchTenants, createTenant, updateTenantSettings } from '@/lib/api/tenants';

// 테넌트 목록 조회
function TenantList() {
  const { data, isLoading } = useQuery({
    queryKey: ['tenants'],
    queryFn: () => fetchTenants(0, 20)
  });

  if (isLoading) return <div>로딩 중...</div>;

  return (
    <ul>
      {data?.data.map(tenant => (
        <li key={tenant.id}>
          {tenant.tenant_name} ({tenant.tenant_code})
        </li>
      ))}
    </ul>
  );
}

// 테넌트 생성
function CreateTenant() {
  const mutation = useMutation({
    mutationFn: createTenant,
    onSuccess: () => {
      // 성공 처리
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      tenant_code: "shop_b",
      tenant_name": "쇼핑몰 B",
      subdomain": "shop_b"
    });
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
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
curl "http://localhost:8000/api/v1/tenants?limit=10"

# 테넌트 설정 수정
curl -X PATCH http://localhost:8000/api/v1/tenants/1/settings \
  -H "Content-Type: application/json" \
  -d '{ "theme": "dark" }'

# 헤더로 테넌트 지정
curl -H "X-Tenant-ID: shop_a" http://localhost:8000/api/v1/items
```

---

## 보안 (Security)

✅ **구현된 보안 기능:**

- **입력 검증**
  - tenant_code: 정규식 검증 (`^[a-z0-9_]+$`)
  - domain: 유효한 도메인 형식
  - email: RFC 5322 기본 형식

- **XSS 방지**
  - 모든 문자열 입력 정제

- **SQL Injection 방지**
  - SQLAlchemy ORM 사용 (Parameterized Query)

- **데이터 보호**
  - 기본 테넌트 (default) 삭제 방지
  - 소프트 삭제 (물리적 삭제 X)

⏳ **향후 추가 예정:**

- JWT 토큰 검증 (auth-backend)
- 권한 제어 (슈퍼 관리자, 관리자)
- RBAC (Role-Based Access Control)

---

## 테스트

### 테스트 실행

```bash
cd backend

# 모든 테스트 실행
pytest tests/test_tenants.py -v

# 특정 클래스 테스트
pytest tests/test_tenants.py::TestTenantCRUD -v

# 특정 테스트만 실행
pytest tests/test_tenants.py::TestTenantCRUD::test_create_tenant_success -v
```

### 포함된 테스트 (25개+)

- **CRUD 테스트**: 생성, 조회, 수정, 삭제
- **검증 테스트**: tenant_code, email, domain
- **설정 테스트**: 조회, 수정 (부분 업데이트)
- **필터링 테스트**: 페이징, is_active 필터

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

## 다음 단계

### 1️⃣ 인증 시스템 통합

```bash
Use auth-backend --init --type=phone
```

그 후 권한 제어 추가:

```python
from app.api.security import require_role

@router.post("", dependencies=[Depends(require_role("super_admin"))])
async def create_tenant(...):
    ...
```

### 2️⃣ 카테고리 관리

```bash
Use category-manager --init
```

### 3️⃣ 게시판 시스템

```bash
Use board-generator --init
```

### 4️⃣ 메뉴 관리

```bash
Use menu-backend --init
Use menu-frontend --init
```

---

## 성능 최적화

### 1. 인덱스 생성

```sql
-- 이미 생성됨 (models/shared.py에서)
CREATE INDEX idx_tenant_code ON tenants(tenant_code);
CREATE INDEX idx_domain ON tenants(domain);
CREATE INDEX idx_subdomain ON tenants(subdomain);
```

### 2. 캐싱 권장

테넌트 정보는 자주 조회되므로 Redis 캐시 추가 권장:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_tenant_by_code(tenant_code: str):
    ...
```

### 3. 페이징

대량의 테넌트는 항상 페이징:

```python
GET /api/v1/tenants?skip=0&limit=20
```

---

## 문서

### 상세 문서

- **[backend/TENANT_MANAGER.md](backend/TENANT_MANAGER.md)** - API 상세 가이드
- **[TENANT_IMPLEMENTATION.md](TENANT_IMPLEMENTATION.md)** - 구현 요약
- **[CLAUDE.md](CLAUDE.md)** - 프로젝트 코딩 규칙

### 관련 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 문서](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2 문서](https://docs.pydantic.dev/)

---

## FAQ

### Q: 테넌트를 어떻게 식별하나요?

**A:** 자동으로 4가지 방식으로 식별합니다 (우선순위 순):

1. X-Tenant-ID 헤더
2. 서브도메인 (shop_a.example.com)
3. 커스텀 도메인 (shop_a.com)
4. 세션 (기본값: default)

### Q: 기본 테넌트는 왜 삭제 불가인가요?

**A:** 시스템 안정성을 위해 기본 테넌트(default)는 삭제 불가합니다. 필요시 비활성화(`is_active=false`)만 가능합니다.

### Q: 설정을 부분 업데이트할 수 있나요?

**A:** 네! `PATCH /api/v1/tenants/{id}/settings` 엔드포인트를 사용하면 기존 설정을 유지하면서 필요한 부분만 업데이트할 수 있습니다.

### Q: 슈퍼 관리자 권한은 어떻게 추가하나요?

**A:** 현재는 권한 검증이 없습니다. `auth-backend` 에이전트를 실행하면 자동으로 JWT 검증과 권한 제어가 추가됩니다:

```bash
Use auth-backend --init --type=phone
```

### Q: 데이터베이스 마이그레이션은 필요한가요?

**A:** Tenant 모델은 이미 `shared-schema`에서 생성되었습니다. alembic 마이그레이션을 실행하세요:

```bash
cd backend
alembic upgrade head
```

---

## 체크리스트

- [x] Tenant CRUD API
- [x] 도메인 설정 (서브도메인, 커스텀 도메인)
- [x] 테마/로고 설정
- [x] 자동 테넌트 감지 미들웨어
- [x] 의존성 주입
- [x] 입력 검증
- [x] 에러 처리
- [x] TypeScript 타입
- [x] API 클라이언트
- [x] 단위 테스트
- [x] 상세 문서

---

## 라이선스

프로젝트의 라이선스를 따릅니다.

---

## 지원

문제가 발생하면 다음을 확인하세요:

1. **로그 확인**: `backend/app/main.py`의 로거 설정 확인
2. **데이터베이스**: PostgreSQL 연결 확인
3. **마이그레이션**: `alembic upgrade head` 실행 확인
4. **환경변수**: `.env` 파일 설정 확인
5. **테스트**: `pytest tests/test_tenants.py -v` 실행

---

## 최종 정리

✅ **테넌트 관리 시스템 구현 완료!**

이 시스템은 멀티테넌시 SaaS 플랫폼의 핵심입니다.
다음 단계로 인증 시스템을 추가하세요:

```bash
Use auth-backend --init --type=phone
```

**Happy Coding!** 🚀
