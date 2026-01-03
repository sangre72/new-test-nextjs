# 메뉴 관리 시스템 - 구현 완료 보고서

FastAPI + Next.js + PostgreSQL 기반 계층형 메뉴 관리 시스템

---

## 📋 구현 개요

### 프로젝트 정보

- **프로젝트명**: Menu Management System
- **기술 스택**: Python 3.11+, FastAPI 0.128.0, SQLAlchemy 2.0+, PostgreSQL 15+
- **구현일**: 2026-01-03
- **상태**: ✅ Backend 완료

---

## ✨ 구현된 기능

### 1. 핵심 기능

✅ **메뉴 CRUD 작업**
- 메뉴 생성 (Create)
- 메뉴 조회 (Read) - 리스트/트리/단건
- 메뉴 수정 (Update)
- 메뉴 삭제 (Delete) - Soft Delete

✅ **계층형 구조**
- 무제한 깊이 부모-자식 관계 (최대 5단계 권장)
- Depth 자동 계산
- Materialized Path (빠른 조회)
- 순환 참조 방지

✅ **메뉴 타입 지원**
- User Menu (사용자 메뉴)
- Site Menu (사이트 메뉴 - 헤더/푸터)
- Admin Menu (관리자 메뉴)

✅ **권한 기반 접근 제어**
- Public (누구나)
- Authenticated (로그인 사용자)
- Role-based (역할 기반)
- Permission-based (권한 기반)

✅ **고급 기능**
- 드래그&드롭 순서 변경 (Bulk Reorder)
- 메뉴 이동 (Move to different parent)
- 벌크 삭제
- 검색 및 필터링

✅ **보안**
- JWT 인증
- Superuser 권한 검증
- 입력 검증 (XSS, SQL Injection 방지)
- 에러 처리 (try-catch)

---

## 📁 파일 구조

```
backend/
├── alembic/
│   └── versions/
│       ├── 001_create_shared_schema.py
│       ├── 002_create_categories_table.py
│       └── 003_update_menus_table.py        # 🆕 메뉴 테이블 업데이트
│
├── app/
│   ├── models/
│   │   ├── __init__.py                      # 🔄 Menu 모델 export 추가
│   │   └── shared.py                        # 🔄 Menu 모델 확장
│   │
│   ├── schemas/
│   │   ├── __init__.py                      # 🔄 Menu 스키마 export 추가
│   │   └── menu.py                          # 🆕 메뉴 Pydantic 스키마
│   │
│   ├── services/
│   │   └── menu.py                          # 🆕 메뉴 비즈니스 로직
│   │
│   └── api/v1/endpoints/
│       ├── __init__.py                      # 🔄 메뉴 라우터 등록
│       └── menus.py                         # 🆕 메뉴 API 엔드포인트
│
├── scripts/
│   └── seed_menus.py                        # 🆕 샘플 데이터 생성
│
├── tests/
│   └── test_menu_api.py                     # 🆕 메뉴 API 테스트
│
├── MENU_API_GUIDE.md                        # 🆕 상세 API 가이드
└── QUICKSTART.md                            # 🆕 빠른 시작 가이드
```

**범례:**
- 🆕 신규 생성
- 🔄 기존 파일 수정

---

## 🗄️ 데이터베이스 스키마

### Menus 테이블

```sql
CREATE TABLE menus (
    -- Primary Key
    id BIGSERIAL PRIMARY KEY,

    -- Foreign Keys
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    parent_id BIGINT REFERENCES menus(id) ON DELETE CASCADE,

    -- Basic Info
    menu_name VARCHAR(100) NOT NULL,
    menu_code VARCHAR(50) NOT NULL,
    description TEXT,

    -- Menu Type & Behavior
    menu_type ENUM('user', 'site', 'admin') NOT NULL DEFAULT 'user',
    menu_url VARCHAR(500),
    menu_icon VARCHAR(100),
    link_type ENUM('internal', 'external', 'new_tab', 'modal', 'none')
              NOT NULL DEFAULT 'internal',

    -- Hierarchy
    depth BIGINT NOT NULL DEFAULT 0,
    path VARCHAR(500),  -- Materialized path: /1/3/5
    display_order BIGINT NOT NULL DEFAULT 0,

    -- Permissions
    permission_type ENUM('public', 'authenticated', 'role_based', 'permission_based')
                    NOT NULL DEFAULT 'public',

    -- Visibility
    is_visible BOOLEAN NOT NULL DEFAULT TRUE,

    -- Metadata
    metadata JSON,

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(100),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_by VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    -- Constraints
    CONSTRAINT uk_tenant_menu_code UNIQUE (tenant_id, menu_code)
);

-- Indexes
CREATE INDEX idx_tenant_id ON menus(tenant_id);
CREATE INDEX idx_menu_code ON menus(menu_code);
CREATE INDEX idx_menu_type ON menus(menu_type);
CREATE INDEX idx_parent_id ON menus(parent_id);
CREATE INDEX idx_display_order ON menus(display_order);
CREATE INDEX idx_tenant_type_parent ON menus(tenant_id, menu_type, parent_id);
```

---

## 🔌 API 엔드포인트

### Public Endpoints (인증 불필요)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/menus/public/tree` | 공개 메뉴 트리 조회 |

### Admin Endpoints (Superuser 인증 필요)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/menus` | 메뉴 리스트 (페이지네이션) |
| GET | `/api/v1/menus/tree` | 메뉴 트리 (전체) |
| GET | `/api/v1/menus/{id}` | 메뉴 단건 조회 |
| POST | `/api/v1/menus` | 메뉴 생성 |
| PUT | `/api/v1/menus/{id}` | 메뉴 수정 |
| DELETE | `/api/v1/menus/{id}` | 메뉴 삭제 (Soft Delete) |
| POST | `/api/v1/menus/bulk-delete` | 벌크 삭제 |
| PUT | `/api/v1/menus/reorder` | 순서 변경 (드래그&드롭) |
| PUT | `/api/v1/menus/{id}/move` | 메뉴 이동 (다른 부모로) |

---

## 🔐 보안 구현

### 1. Security First Principle

✅ **입력 검증**
```python
@validator('menu_code')
def validate_menu_code(cls, v):
    # 위험한 문자 차단
    if any(char in v for char in ['<', '>', '&', '"', "'"]):
        raise ValueError('Invalid characters')
    # 알파벳, 숫자, -, _ 만 허용
    if not all(c.isalnum() or c in ['_', '-'] for c in v):
        raise ValueError('Invalid format')
    return v.strip().lower()
```

✅ **XSS 방지**
```python
@validator('menu_url')
def validate_menu_url(cls, v):
    dangerous_patterns = ['javascript:', '<script', 'onerror=']
    if any(pattern in v.lower() for pattern in dangerous_patterns):
        raise ValueError('Invalid URL pattern')
    return v
```

✅ **SQL Injection 방지**
```python
# ❌ 절대 사용 금지
query = f"SELECT * FROM menus WHERE id = {menu_id}"

# ✅ 항상 사용
query = db.query(Menu).filter(Menu.id == menu_id)
```

### 2. Error Handling First Principle

✅ **모든 엔드포인트에 에러 처리**
```python
try:
    menu = MenuService.create_menu(...)
    return MenuResponse.from_orm(menu)
except HTTPException:
    raise  # Re-raise validation errors
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Internal error: {str(e)}"
    )
```

✅ **권한 검증**
```python
@router.post("/menus")
def create_menu(
    current_user: User = Depends(get_current_superuser)
):
    # Only superusers can create menus
    ...
```

---

## 📊 샘플 데이터

`scripts/seed_menus.py` 실행 시 생성:

### User Menus (10개)
- Home
- Products
  - All Products
  - New Arrivals
  - Sale
- About
- My Account
  - Profile
  - Orders
  - Wishlist

### Admin Menus (13개)
- Dashboard
- Content
  - Posts
  - Categories
  - Tags
- Users
  - All Users
  - Roles
  - Permissions
- Settings
  - General
  - Menus
  - SEO

### Site Menus (3개)
- Help
- Contact
- Privacy

**총 26개 메뉴**

---

## 🧪 테스트

### 테스트 커버리지

```bash
pytest tests/test_menu_api.py -v
```

**테스트 항목:**

✅ **CRUD Tests**
- test_create_menu
- test_create_menu_with_parent
- test_get_menus
- test_get_menu_tree
- test_update_menu
- test_delete_menu
- test_reorder_menus

✅ **Validation Tests**
- test_invalid_menu_code
- test_invalid_menu_url
- test_duplicate_menu_code

✅ **Security Tests**
- test_unauthorized_access
- test_public_endpoint_no_auth

---

## 🚀 사용 방법

### 1. 설치

```bash
cd backend

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 DATABASE_URL 수정
```

### 2. 마이그레이션

```bash
# 데이터베이스 마이그레이션 실행
alembic upgrade head
```

### 3. 샘플 데이터 생성

```bash
# 샘플 메뉴 생성
python scripts/seed_menus.py
```

### 4. 서버 실행

```bash
# 개발 서버
uvicorn app.main:app --reload
```

### 5. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📚 사용 예시

### cURL 예시

```bash
# 1. 로그인
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2. 공개 메뉴 조회
curl http://localhost:8000/api/v1/menus/public/tree?menu_type=user

# 3. 메뉴 생성 (인증 필요)
curl -X POST http://localhost:8000/api/v1/menus \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "menu_name": "New Menu",
    "menu_code": "new-menu",
    "menu_type": "user",
    "menu_url": "/new-menu",
    "display_order": 10
  }'
```

### Python 클라이언트 예시

```python
import httpx

# 메뉴 조회
response = httpx.get(
    "http://localhost:8000/api/v1/menus/public/tree",
    params={"menu_type": "user"}
)
menus = response.json()

# 메뉴 생성
response = httpx.post(
    "http://localhost:8000/api/v1/menus",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "menu_name": "New Menu",
        "menu_code": "new-menu",
        "menu_type": "user"
    }
)
```

### TypeScript/Next.js 예시

```typescript
// 메뉴 트리 조회
const getMenuTree = async (menuType: 'user' | 'site' | 'admin') => {
  const response = await fetch(
    `/api/v1/menus/public/tree?menu_type=${menuType}`
  );
  return response.json();
};

// 메뉴 렌더링
const MenuTree = ({ items }) => (
  <ul>
    {items.map(item => (
      <li key={item.id}>
        <a href={item.menu_url}>
          <i className={item.menu_icon} />
          {item.menu_name}
        </a>
        {item.children?.length > 0 && <MenuTree items={item.children} />}
      </li>
    ))}
  </ul>
);
```

---

## 📖 문서

- **[QUICKSTART.md](backend/QUICKSTART.md)** - 빠른 시작 가이드
- **[MENU_API_GUIDE.md](backend/MENU_API_GUIDE.md)** - 상세 API 문서
- **[API Docs (Swagger)](http://localhost:8000/docs)** - 대화형 API 문서

---

## ✅ 체크리스트

### Backend 구현 완료

- [x] 메뉴 모델 정의 (SQLAlchemy)
- [x] Pydantic 스키마 (입력 검증)
- [x] 서비스 레이어 (비즈니스 로직)
- [x] API 엔드포인트 (FastAPI)
- [x] Alembic 마이그레이션
- [x] 보안 검증 (XSS, SQL Injection 방지)
- [x] 에러 처리
- [x] 샘플 데이터 생성 스크립트
- [x] 테스트 코드
- [x] API 문서

### 다음 단계 (Frontend)

- [ ] Next.js 메뉴 컴포넌트
- [ ] 메뉴 편집기 UI
- [ ] 드래그&드롭 순서 변경
- [ ] 권한 기반 메뉴 필터링
- [ ] 아이콘 선택기
- [ ] 메뉴 미리보기

---

## 🎯 핵심 기술 포인트

### 1. 계층형 구조 (Materialized Path)

```python
# 빠른 자손 조회 (O(1) 인덱스 스캔)
descendants = db.query(Menu).filter(
    Menu.path.like(f"{parent.path}/%")
).all()
```

### 2. 순환 참조 방지

```python
def validate_no_circular_reference(menu_id, new_parent_id):
    current_id = new_parent_id
    while current_id:
        if current_id == menu_id:
            raise HTTPException(
                detail="Cannot move menu to its own descendant"
            )
        current_id = get_parent_id(current_id)
```

### 3. 자동 Depth 계산

```python
def calculate_depth_and_path(parent_id, menu_id):
    if not parent_id:
        return 0, f"/{menu_id}"

    parent = get_menu(parent_id)
    depth = parent.depth + 1
    path = f"{parent.path}/{menu_id}"
    return depth, path
```

---

## 🔧 기술 스택

| 구분 | 기술 | 버전 |
|------|------|------|
| Backend | Python | 3.11+ |
| Web Framework | FastAPI | 0.128.0 |
| ORM | SQLAlchemy | 2.0+ |
| Migration | Alembic | 1.14.0 |
| Database | PostgreSQL | 15+ |
| Validation | Pydantic | 2.10.5 |
| Auth | JWT (python-jose) | 3.3.0 |
| Testing | pytest | 8.3.4 |

---

## 📝 참고 사항

### 제한사항

- **최대 깊이**: 5단계 권장 (무제한 지원하지만 성능 고려)
- **페이지네이션**: 최대 100개 (기본 50개)
- **메뉴 코드**: 알파벳, 숫자, -, _ 만 허용

### 성능 최적화

- Materialized Path 사용 (빠른 자손 조회)
- 복합 인덱스 (tenant_id, menu_type, parent_id)
- Soft Delete (데이터 복구 가능)

### 보안 고려사항

- 모든 입력 검증 (Pydantic)
- SQL Injection 방지 (Parameterized Query)
- XSS 방지 (URL, Metadata 검증)
- 권한 검증 (JWT + Superuser)

---

## 🤝 기여

이 프로젝트는 Security First, Error Handling First 원칙을 준수합니다.

---

**프로젝트 상태**: ✅ Backend 완료
**다음 단계**: Frontend 구현
**버전**: 1.0.0
**작성일**: 2026-01-03
