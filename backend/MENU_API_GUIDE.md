# Menu Management API Guide

완전한 계층형 메뉴 관리 시스템 - FastAPI + PostgreSQL + SQLAlchemy

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [설치 및 설정](#설치-및-설정)
- [API 엔드포인트](#api-엔드포인트)
- [데이터 모델](#데이터-모델)
- [사용 예시](#사용-예시)
- [보안](#보안)

---

## 개요

이 메뉴 관리 API는 다음을 지원합니다:

- **계층형 구조**: 무제한 깊이의 부모-자식 관계 (최대 5단계 권장)
- **다중 메뉴 타입**: User, Site, Admin 메뉴 분리
- **권한 기반 접근**: Public, Authenticated, Role-based, Permission-based
- **드래그&드롭**: 순서 변경 및 부모 이동 지원
- **Soft Delete**: 실수로 삭제한 메뉴 복구 가능
- **Metadata 지원**: Badge, Tooltip 등 추가 정보 저장

---

## 주요 기능

### 1. CRUD 작업

- ✅ 메뉴 생성 (Create)
- ✅ 메뉴 조회 (Read) - 리스트/트리/단건
- ✅ 메뉴 수정 (Update)
- ✅ 메뉴 삭제 (Delete) - Soft Delete

### 2. 계층 관리

- ✅ 부모-자식 관계
- ✅ Depth 자동 계산
- ✅ Materialized Path (빠른 조회)
- ✅ 순환 참조 방지

### 3. 고급 기능

- ✅ 벌크 순서 변경 (Reorder)
- ✅ 메뉴 이동 (Move to different parent)
- ✅ 벌크 삭제
- ✅ 검색 및 필터링

### 4. 보안

- ✅ JWT 인증
- ✅ Superuser 권한 검증
- ✅ 입력 검증 (XSS, SQL Injection 방지)
- ✅ 에러 처리

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| **Backend** | Python 3.11+, FastAPI 0.128.0 |
| **ORM** | SQLAlchemy 2.0+ |
| **Migration** | Alembic |
| **Database** | PostgreSQL 15+ |
| **Validation** | Pydantic v2 |
| **Auth** | JWT (python-jose) |

---

## 설치 및 설정

### 1. 데이터베이스 마이그레이션

```bash
cd backend

# 마이그레이션 실행
alembic upgrade head

# 특정 리비전만 실행
alembic upgrade 003_update_menus_table
```

### 2. 샘플 데이터 생성

```bash
# 샘플 메뉴 데이터 생성
python scripts/seed_menus.py
```

생성되는 메뉴:
- **User Menus** (4개): Home, Products (3 children), About, My Account (3 children)
- **Admin Menus** (4개): Dashboard, Content (3 children), Users (3 children), Settings (3 children)
- **Site Menus** (3개): Help, Contact, Privacy

### 3. 서버 실행

```bash
# 개발 서버
uvicorn app.main:app --reload

# API 문서 확인
open http://localhost:8000/docs
```

---

## API 엔드포인트

### Public Endpoints (인증 불필요)

#### GET /api/v1/menus/public/tree

사용자에게 표시할 메뉴 트리 조회

**Query Parameters:**
- `menu_type` (required): `user` | `site` | `admin`

**Response:**
```json
{
  "total": 4,
  "items": [
    {
      "id": 1,
      "menu_name": "Home",
      "menu_code": "home",
      "menu_type": "user",
      "menu_url": "/",
      "menu_icon": "fa-home",
      "display_order": 1,
      "children": []
    },
    {
      "id": 2,
      "menu_name": "Products",
      "menu_code": "products",
      "children": [
        {
          "id": 3,
          "menu_name": "All Products",
          "menu_url": "/products/all"
        }
      ]
    }
  ]
}
```

---

### Admin Endpoints (Superuser 인증 필요)

#### GET /api/v1/menus

메뉴 리스트 조회 (페이지네이션)

**Query Parameters:**
- `menu_type`: 메뉴 타입 필터
- `parent_id`: 부모 ID 필터
- `is_visible`: 표시 여부 필터
- `is_active`: 활성 여부 필터
- `search`: 검색어 (menu_name, menu_code)
- `skip`: 건너뛸 레코드 수 (default: 0)
- `limit`: 최대 레코드 수 (default: 50, max: 100)

**Response:**
```json
{
  "total": 15,
  "items": [
    {
      "id": 1,
      "tenant_id": 1,
      "menu_name": "Home",
      "menu_code": "home",
      "menu_type": "user",
      "depth": 0,
      "path": "/1",
      "created_at": "2026-01-03T10:00:00Z"
    }
  ]
}
```

---

#### GET /api/v1/menus/tree

메뉴 트리 조회 (관리자용 - 모든 메뉴)

**Query Parameters:**
- `menu_type`: 메뉴 타입 필터 (optional)

**Response:**
```json
{
  "total": 4,
  "items": [
    {
      "id": 1,
      "menu_name": "Home",
      "children": []
    }
  ]
}
```

---

#### GET /api/v1/menus/{menu_id}

메뉴 단건 조회

**Response:**
```json
{
  "id": 1,
  "tenant_id": 1,
  "menu_name": "Home",
  "menu_code": "home",
  "menu_type": "user",
  "menu_url": "/",
  "menu_icon": "fa-home",
  "link_type": "internal",
  "permission_type": "public",
  "display_order": 1,
  "depth": 0,
  "path": "/1",
  "is_visible": true,
  "is_active": true,
  "metadata": null,
  "created_at": "2026-01-03T10:00:00Z",
  "updated_at": "2026-01-03T10:00:00Z"
}
```

---

#### POST /api/v1/menus

메뉴 생성

**Request Body:**
```json
{
  "menu_name": "New Menu",
  "menu_code": "new-menu",
  "menu_type": "user",
  "menu_url": "/new-menu",
  "menu_icon": "fa-star",
  "link_type": "internal",
  "permission_type": "public",
  "parent_id": null,
  "display_order": 10,
  "is_visible": true,
  "is_active": true,
  "metadata": {
    "badge": "New",
    "tooltip": "Check out our new feature"
  }
}
```

**Response:** `201 Created`

---

#### PUT /api/v1/menus/{menu_id}

메뉴 수정

**Request Body:** (모든 필드 optional)
```json
{
  "menu_name": "Updated Menu",
  "menu_url": "/updated-menu",
  "display_order": 5
}
```

**Response:** `200 OK`

---

#### DELETE /api/v1/menus/{menu_id}

메뉴 삭제 (Soft Delete, 자식 메뉴도 함께 삭제)

**Response:** `200 OK`

---

#### POST /api/v1/menus/bulk-delete

벌크 삭제

**Request Body:**
```json
{
  "menu_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "success": true,
  "deleted_count": 3,
  "message": "Successfully deleted 3 menus"
}
```

---

#### PUT /api/v1/menus/reorder

메뉴 순서 변경 (드래그&드롭용)

**Request Body:**
```json
{
  "items": [
    { "menu_id": 1, "new_order": 0 },
    { "menu_id": 2, "new_order": 1 },
    { "menu_id": 3, "new_order": 2 }
  ]
}
```

**Response:** `200 OK` (업데이트된 메뉴 리스트)

---

#### PUT /api/v1/menus/{menu_id}/move

메뉴 이동 (다른 부모로 이동)

**Request Body:**
```json
{
  "new_parent_id": 5,
  "new_order": 0
}
```

**Response:** `200 OK`

---

## 데이터 모델

### Menu 테이블

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `id` | BIGINT | Primary Key |
| `tenant_id` | BIGINT | 테넌트 ID (FK) |
| `menu_name` | VARCHAR(100) | 메뉴 표시명 |
| `menu_code` | VARCHAR(50) | 메뉴 코드 (unique per tenant) |
| `description` | TEXT | 설명 |
| `menu_type` | ENUM | user/site/admin |
| `menu_url` | VARCHAR(500) | URL 또는 경로 |
| `menu_icon` | VARCHAR(100) | 아이콘 클래스 |
| `link_type` | ENUM | internal/external/new_tab/modal/none |
| `parent_id` | BIGINT | 부모 메뉴 ID (FK, self) |
| `depth` | BIGINT | 계층 깊이 (0=루트) |
| `path` | VARCHAR(500) | Materialized path (/1/3/5) |
| `display_order` | BIGINT | 표시 순서 |
| `permission_type` | ENUM | public/authenticated/role_based/permission_based |
| `is_visible` | BOOLEAN | 표시 여부 |
| `metadata` | JSON | 추가 메타데이터 |
| `created_at` | TIMESTAMP | 생성일시 |
| `created_by` | VARCHAR(100) | 생성자 |
| `updated_at` | TIMESTAMP | 수정일시 |
| `updated_by` | VARCHAR(100) | 수정자 |
| `is_active` | BOOLEAN | 활성 여부 |
| `is_deleted` | BOOLEAN | 삭제 여부 |

### Enums

#### MenuTypeEnum
- `user`: 사용자 메뉴 (프론트엔드)
- `site`: 사이트 메뉴 (헤더/푸터 유틸리티)
- `admin`: 관리자 메뉴 (백엔드)

#### MenuPermissionTypeEnum
- `public`: 누구나 접근 가능
- `authenticated`: 로그인 사용자만
- `role_based`: 특정 역할 사용자만
- `permission_based`: 특정 권한 보유자만

#### MenuLinkTypeEnum
- `internal`: 내부 라우팅
- `external`: 외부 링크
- `new_tab`: 새 탭에서 열기
- `modal`: 모달로 열기
- `none`: 링크 없음 (부모 메뉴)

---

## 사용 예시

### 1. 프론트엔드 메뉴 렌더링

```typescript
// Next.js Example
import { useEffect, useState } from 'react';

interface MenuItem {
  id: number;
  menu_name: string;
  menu_url: string;
  menu_icon: string;
  children: MenuItem[];
}

export function Navigation() {
  const [menus, setMenus] = useState<MenuItem[]>([]);

  useEffect(() => {
    fetch('/api/v1/menus/public/tree?menu_type=user')
      .then(res => res.json())
      .then(data => setMenus(data.items));
  }, []);

  const renderMenu = (items: MenuItem[]) => (
    <ul>
      {items.map(item => (
        <li key={item.id}>
          <a href={item.menu_url}>
            <i className={item.menu_icon} />
            {item.menu_name}
          </a>
          {item.children?.length > 0 && renderMenu(item.children)}
        </li>
      ))}
    </ul>
  );

  return <nav>{renderMenu(menus)}</nav>;
}
```

### 2. 관리자 메뉴 편집

```typescript
// Admin Menu Editor
async function createMenu(data: MenuCreate) {
  const response = await fetch('/api/v1/menus', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });

  return response.json();
}

// Drag & Drop Reorder
async function reorderMenus(items: Array<{menu_id: number, new_order: number}>) {
  const response = await fetch('/api/v1/menus/reorder', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ items })
  });

  return response.json();
}
```

### 3. cURL Examples

```bash
# 1. 메뉴 생성
curl -X POST http://localhost:8000/api/v1/menus \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "menu_name": "Products",
    "menu_code": "products",
    "menu_type": "user",
    "menu_url": "/products",
    "menu_icon": "fa-shopping-bag",
    "display_order": 2
  }'

# 2. 메뉴 트리 조회 (Public)
curl http://localhost:8000/api/v1/menus/public/tree?menu_type=user

# 3. 메뉴 수정
curl -X PUT http://localhost:8000/api/v1/menus/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"menu_name": "Updated Name"}'

# 4. 메뉴 이동
curl -X PUT http://localhost:8000/api/v1/menus/5/move \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_parent_id": 2, "new_order": 0}'
```

---

## 보안

### 1. 입력 검증

모든 입력은 Pydantic으로 검증됩니다:

```python
# menu_code: 알파벳, 숫자, -, _ 만 허용
@validator('menu_code')
def validate_menu_code(cls, v):
    if not all(c.isalnum() or c in ['_', '-'] for c in v):
        raise ValueError('Invalid characters')
    return v.strip().lower()

# menu_url: XSS 패턴 차단
@validator('menu_url')
def validate_menu_url(cls, v):
    dangerous_patterns = ['javascript:', '<script', 'onerror=']
    if any(pattern in v.lower() for pattern in dangerous_patterns):
        raise ValueError('Invalid URL pattern')
    return v
```

### 2. SQL Injection 방지

모든 쿼리는 Parameterized Query 사용:

```python
# ❌ 절대 금지
query = f"SELECT * FROM menus WHERE id = {menu_id}"

# ✅ 항상 사용
query = db.query(Menu).filter(Menu.id == menu_id)
```

### 3. 권한 검증

```python
# Superuser만 접근 가능
@router.post("/menus")
def create_menu(
    current_user: User = Depends(get_current_superuser)
):
    ...
```

### 4. 에러 처리

모든 엔드포인트는 try-catch로 보호:

```python
try:
    menu = MenuService.create_menu(...)
except HTTPException:
    raise  # Re-raise validation errors
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Internal error: {str(e)}"
    )
```

---

## 성능 최적화

### 1. Materialized Path

빠른 자손 조회:

```python
# 모든 자손 조회 (O(1) 인덱스 스캔)
descendants = db.query(Menu).filter(
    Menu.path.like(f"{parent.path}/%")
).all()
```

### 2. 인덱스

```sql
CREATE INDEX idx_tenant_type_parent ON menus (tenant_id, menu_type, parent_id);
CREATE INDEX idx_menu_type ON menus (menu_type);
CREATE INDEX idx_display_order ON menus (display_order);
```

### 3. 페이지네이션

```python
# 기본 50개, 최대 100개 제한
limit: int = Query(50, ge=1, le=100)
```

---

## 문제 해결

### Q1. 마이그레이션 실패

```bash
# 현재 리비전 확인
alembic current

# 특정 리비전으로 다운그레이드
alembic downgrade 002

# 다시 업그레이드
alembic upgrade head
```

### Q2. 순환 참조 에러

메뉴 이동 시 순환 참조가 감지되면 400 에러 발생:

```json
{
  "detail": "Cannot move menu to its own descendant"
}
```

### Q3. 중복 menu_code 에러

같은 tenant 내에서 menu_code는 unique:

```json
{
  "detail": "Menu with code 'products' already exists"
}
```

---

## 추가 참고 자료

- **FastAPI 문서**: https://fastapi.tiangolo.com
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Alembic**: https://alembic.sqlalchemy.org/en/latest/

---

## 라이선스

MIT License

---

**생성일**: 2026-01-03
**버전**: 1.0.0
**작성자**: Claude Code (Anthropic)
