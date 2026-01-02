# 카테고리 관리 시스템 (Category Manager)

**게시판별 카테고리를 관리하는 시스템입니다.**

상태: 구현 완료

---

## 개요

카테고리 관리 시스템은 다음 기능을 제공합니다:

- 게시판별 독립적인 카테고리 관리
- 무한 깊이의 계층형 카테고리 (Hierarchical Categories)
- 드래그앤드롭으로 순서와 계층 변경
- 게시글 수 캐싱
- 테넌트별 완전한 데이터 격리

---

## 특징

### 1. 계층형 카테고리

```
공지사항 (depth=0, path=/1/)
├── 일반 (depth=1, path=/1/2/)
│   ├── 서비스 안내 (depth=2, path=/1/2/3/)
│   └── 점검 안내 (depth=2, path=/1/2/4/)
├── 긴급 (depth=1, path=/1/5/)
└── 이벤트 (depth=1, path=/1/6/)
    ├── 진행중 (depth=2, path=/1/6/7/)
    └── 종료 (depth=2, path=/1/6/8/)
```

**주요 필드:**
- `depth`: 계층의 깊이 (0=최상위)
- `path`: 경로 문자열 (예: `/1/2/3/`)로 빠른 하위 조회 가능
- `parent_id`: 상위 카테고리 ID (NULL이면 최상위)

### 2. 경로 기반 쿼리

`path` 컬럼을 이용하여 모든 하위 카테고리를 효율적으로 조회:

```python
# 카테고리 3의 모든 하위 카테고리 조회
SELECT * FROM categories WHERE path LIKE '/1/2/3/%'
```

### 3. 순환 참조 방지

자신의 하위 카테고리를 상위로 설정하려는 시도를 자동으로 방지합니다.

### 4. 게시글 수 캐싱

각 카테고리의 `post_count` 필드는 게시글 추가/삭제 시 동기화되어 빠른 조회를 가능하게 합니다.

---

## 데이터베이스 스키마

### categories 테이블

```sql
CREATE TABLE categories (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,

  -- 테넌트 & 게시판
  tenant_id BIGINT NOT NULL (FK: tenants),
  board_id BIGINT NOT NULL,

  -- 계층 구조
  parent_id BIGINT NULL (FK: categories),
  depth INT DEFAULT 0,
  path VARCHAR(500),

  -- 기본 정보
  category_name VARCHAR(100) NOT NULL,
  category_code VARCHAR(50) NOT NULL,
  description TEXT,

  -- 표시 설정
  sort_order INT DEFAULT 0,
  icon VARCHAR(50),
  color VARCHAR(20),

  -- 권한
  read_permission VARCHAR(50) DEFAULT 'all',
  write_permission VARCHAR(50) DEFAULT 'all',

  -- 캐시
  post_count INT DEFAULT 0,

  -- 감사 컬럼
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(100),
  updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(100),
  is_active BOOLEAN DEFAULT TRUE,
  is_deleted BOOLEAN DEFAULT FALSE,

  -- 제약
  UNIQUE KEY uk_board_category_code (board_id, category_code),
  FOREIGN KEY fk_tenant (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
  FOREIGN KEY fk_parent (parent_id) REFERENCES categories(id) ON DELETE SET NULL,

  -- 인덱스
  INDEX idx_tenant_id (tenant_id),
  INDEX idx_board_id (board_id),
  INDEX idx_parent_id (parent_id),
  INDEX idx_depth (depth),
  INDEX idx_sort_order (sort_order),
  INDEX idx_path (path),
  INDEX idx_tenant_board (tenant_id, board_id)
);
```

---

## API 엔드포인트

### 기본 URL

```
http://localhost:8000/api/v1/categories
```

### 1. 카테고리 목록 조회 (계층형 트리)

```http
GET /api/v1/categories/board/{board_id}
```

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "category_name": "공지사항",
      "category_code": "notice",
      "depth": 0,
      "path": "/1/",
      "children": [
        {
          "id": 2,
          "category_name": "일반",
          "category_code": "general",
          "depth": 1,
          "path": "/1/2/",
          "children": []
        }
      ]
    }
  ],
  "total": 1
}
```

### 2. 카테고리 목록 조회 (평면)

```http
GET /api/v1/categories/board/{board_id}/flat?skip=0&limit=100
```

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "category_name": "공지사항",
      "category_code": "notice",
      "depth": 0,
      "path": "/1/",
      ...
    }
  ],
  "total": 5
}
```

### 3. 카테고리 상세 조회

```http
GET /api/v1/categories/{category_id}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "tenant_id": 1,
    "board_id": 1,
    "parent_id": null,
    "depth": 0,
    "path": "/1/",
    "category_name": "공지사항",
    "category_code": "notice",
    "description": "공지사항 카테고리",
    "sort_order": 0,
    "icon": "folder",
    "color": "#1976d2",
    "read_permission": "all",
    "write_permission": "members",
    "post_count": 10,
    "created_at": "2026-01-03T00:00:00",
    "created_by": "admin",
    "updated_at": "2026-01-03T00:00:00",
    "updated_by": "admin",
    "is_active": true,
    "is_deleted": false
  }
}
```

### 4. 카테고리 생성

```http
POST /api/v1/categories
Content-Type: application/json

{
  "board_id": 1,
  "category_name": "일반",
  "category_code": "general",
  "parent_id": null,
  "description": "일반 공지사항",
  "sort_order": 0,
  "icon": "folder",
  "color": "#1976d2",
  "read_permission": "all",
  "write_permission": "members"
}
```

**응답:** `201 Created`

**요청 검증:**
- `category_code`: 영문 소문자, 숫자, 언더스코어만 허용 (2-50자)
- `category_name`: 1-100자
- `parent_id`: 존재하는 카테고리 ID
- 게시판 내에서 `category_code` 중복 불가

### 5. 카테고리 수정

```http
PUT /api/v1/categories/{category_id}
Content-Type: application/json

{
  "category_name": "긴급 공지",
  "description": "긴급한 내용",
  "sort_order": 5,
  "icon": "alert",
  "color": "#ff0000",
  "read_permission": "members",
  "write_permission": "admin",
  "is_active": true
}
```

**응답:** `200 OK`

**주의:**
- `category_code`는 수정 불가 (생성 후 고정)
- 부모 변경은 `/move` 엔드포인트 사용

### 6. 카테고리 계층 변경 (부모 변경)

```http
PUT /api/v1/categories/{category_id}/move?parent_id={new_parent_id}
```

**요청 예시:**
```
PUT /api/v1/categories/3/move?parent_id=1
```

**응답:** `200 OK`

**자동 처리:**
- 하위 카테고리의 `depth`, `path` 재계산
- 모든 하위 카테고리 동시 업데이트 (트랜잭션)

**주의:**
- 자신을 상위로 설정 불가
- 자신의 하위를 상위로 설정 불가 (순환 참조 방지)

### 7. 카테고리 순서 변경 (드래그앤드롭)

```http
PUT /api/v1/categories/reorder
Content-Type: application/json

{
  "category_id": 3,
  "parent_id": 1,
  "sort_order": 5
}
```

**응답:** `200 OK`

**용도:**
- 드래그앤드롭 인터페이스에서 순서와 계층을 동시에 변경

### 8. 카테고리 삭제

```http
DELETE /api/v1/categories/{category_id}
```

**응답:** `200 OK`

**조건 (모두 만족해야 삭제 가능):**
- 하위 카테고리가 없어야 함
- 게시글이 없어야 함 (`post_count == 0`)

**에러 응답:**
```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "message": "하위 카테고리가 2개 있어 삭제할 수 없습니다..."
}
```

---

## 권한 체계

모든 쓰기 작업(생성/수정/삭제)은 **Admin 권한**이 필요합니다.

```python
# 관리자만 접근 가능
@router.post("", dependencies=[Depends(_check_admin_permission)])
async def create_category(...): ...
```

**TODO:** auth-backend에서 게시판별 관리자 권한 확인으로 대체 필요

---

## 서비스 레이어 (CategoryService)

### 주요 메서드

```python
# 조회
await CategoryService.get_category_by_id(session, category_id)
await CategoryService.get_category_by_code(session, board_id, category_code)
await CategoryService.get_categories_tree(session, tenant_id, board_id)
await CategoryService.list_categories_flat(session, tenant_id, board_id)
await CategoryService.get_category_children(session, parent_id)
await CategoryService.get_category_descendants(session, category_id)
await CategoryService.get_category_ancestors(session, category_id)

# 생성
await CategoryService.create_category(
    session, tenant_id, board_id, category_name, category_code, ...
)

# 수정
await CategoryService.update_category(session, category_id, ...)

# 이동
await CategoryService.move_category(
    session, category_id, new_parent_id, ...
)

# 순서 변경
await CategoryService.reorder_categories(
    session, category_id, new_parent_id, new_sort_order, ...
)

# 삭제
await CategoryService.delete_category(session, category_id)

# 게시글 수 동기화
await CategoryService.increment_post_count(session, category_id)
await CategoryService.decrement_post_count(session, category_id)
```

### 에러 처리

모든 메서드는 예외 발생 시 `ValueError` 또는 `HTTPException`을 발생시킵니다:

```python
try:
    await CategoryService.move_category(...)
except ValueError as e:
    # 비즈니스 로직 에러
    return ErrorResponse(error_code="VALIDATION_ERROR", message=str(e))
```

---

## 사용 예시

### 1. 카테고리 생성 (계층형)

```python
# 최상위 카테고리 생성
notice = await CategoryService.create_category(
    session=session,
    tenant_id=1,
    board_id=1,
    category_name="공지사항",
    category_code="notice",
)

# 하위 카테고리 생성
general = await CategoryService.create_category(
    session=session,
    tenant_id=1,
    board_id=1,
    category_name="일반",
    category_code="general",
    parent_id=notice.id,  # 상위 지정
)

# 더 깊은 하위 카테고리
service_guide = await CategoryService.create_category(
    session=session,
    tenant_id=1,
    board_id=1,
    category_name="서비스 안내",
    category_code="service_guide",
    parent_id=general.id,  # 2단계 깊이
)
```

결과:
```
notice (depth=0, path=/1/)
└── general (depth=1, path=/1/2/)
    └── service_guide (depth=2, path=/1/2/3/)
```

### 2. 계층형 트리 조회

```python
# 최상위 카테고리들만 조회 (children 포함)
categories = await CategoryService.get_categories_tree(
    session=session,
    tenant_id=1,
    board_id=1,
)

# 출력
for cat in categories:
    print(f"{cat.category_name} (depth={cat.depth})")
    for child in cat.children:
        print(f"  └── {child.category_name} (depth={child.depth})")
```

### 3. 모든 하위 카테고리 조회

```python
# 경로 기반으로 빠른 조회
descendants = await CategoryService.get_category_descendants(
    session=session,
    category_id=2,  # general의 모든 하위
)

for desc in descendants:
    print(f"{desc.category_name} (path={desc.path})")
```

### 4. 카테고리 이동

```python
# general을 notice의 형제로 변경
# 즉, notice와 같은 레벨로 올리기
await CategoryService.move_category(
    session=session,
    category_id=2,  # general
    new_parent_id=None,  # 최상위
)

# 자동으로 하위 카테고리들도 업데이트됨
# service_guide (depth=1, path=/1/3/ 으로 변경됨)
```

### 5. 게시글 추가 시 카테고리 카운트 증가

```python
# 게시글 생성 후
await CategoryService.increment_post_count(
    session=session,
    category_id=category.id,
)

# 게시글 삭제 시
await CategoryService.decrement_post_count(
    session=session,
    category_id=category.id,
)
```

---

## 문제 해결

### 1. "카테고리 코드 'general'은 이미 존재합니다"

**원인:** 같은 게시판 내에서 중복된 `category_code`

**해결:**
```python
# 1. 고유한 코드 사용
category_code = "general_v2"

# 2. 기존 카테고리 삭제 후 재생성
```

### 2. "하위 카테고리가 3개 있어 삭제할 수 없습니다"

**원인:** 삭제하려는 카테고리에 하위 카테고리가 있음

**해결:**
```python
# 1. 먼저 하위 카테고리 삭제
for child in category.children:
    await CategoryService.delete_category(session, child.id)

# 2. 상위 카테고리 삭제
await CategoryService.delete_category(session, category.id)

# 또는 하위 카테고리를 다른 부모로 이동
await CategoryService.move_category(
    session=session,
    category_id=child.id,
    new_parent_id=another_parent_id,
)
```

### 3. "하위 카테고리를 상위 카테고리로 설정할 수 없습니다"

**원인:** 순환 참조 시도 (A가 B의 부모인데 A를 B의 부모로 설정)

**해결:**
```python
# 올바른 계층 구조로 변경
# A -> B -> C 구조에서
# C를 B의 부모로 설정 불가

# 대신 이렇게 구조 변경:
# A -> C와 B -> A 또는 다른 구조
```

---

## 마이그레이션

### 테이블 생성

```bash
# 마이그레이션 파일 자동 생성
alembic revision --autogenerate -m "Create categories table"

# 마이그레이션 적용
alembic upgrade head
```

### 수동 마이그레이션

이미 생성된 마이그레이션 파일:
```
backend/alembic/versions/001_create_categories_table.py
```

적용:
```bash
alembic upgrade head
```

---

## 성능 최적화

### 1. 경로 기반 쿼리 (path column)

모든 하위 카테고리를 한 번에 조회:

```python
# ❌ 비효율적: 재귀 쿼리
def get_descendants(category_id):
    children = get_children(category_id)
    all_descendants = children
    for child in children:
        all_descendants.extend(get_descendants(child.id))
    return all_descendants

# ✅ 효율적: 경로 기반 쿼리 (한 번)
SELECT * FROM categories WHERE path LIKE '/1/2/%'
```

### 2. 게시글 수 캐싱

매번 게시글 테이블을 조회하는 대신 `post_count` 사용:

```python
# ❌ 비효율적: 매번 조회
category.post_count = session.query(Post).filter_by(
    category_id=category_id
).count()

# ✅ 효율적: 미리 계산된 값 사용
print(f"게시글 {category.post_count}개")

# 게시글 추가/삭제 시에만 동기화
await CategoryService.increment_post_count(session, category_id)
```

### 3. 인덱스 활용

생성된 인덱스:
- `idx_tenant_board`: 테넌트별 게시판 조회
- `idx_path`: 경로 기반 하위 조회
- `idx_sort_order`: 정렬 순서

---

## 다음 단계

1. **게시판 통합**
   - `board-generator`에서 게시판 생성 시 기본 카테고리 자동 생성
   - 게시판 설정에서 카테고리 사용 여부 설정

2. **게시글 통합**
   - 게시글 생성/삭제 시 `post_count` 동기화
   - 카테고리 없이 게시글 작성 불가능하게 설정 (옵션)

3. **권한 통합**
   - auth-backend와 통합하여 게시판별 관리자 권한 확인
   - 카테고리별 읽기/쓰기 권한 구체적으로 구현

4. **프론트엔드**
   - 카테고리 목록 조회 UI
   - 드래그앤드롭 카테고리 관리 UI
   - Admin 패널에서 카테고리 관리

5. **검색 및 필터링**
   - 카테고리별 게시글 검색
   - 게시글 목록에서 카테고리 필터링

---

## 파일 목록

### 모델
- `/backend/app/models/category.py` - Category 모델

### 스키마
- `/backend/app/schemas/category.py` - 요청/응답 스키마

### 서비스
- `/backend/app/services/category.py` - CategoryService

### API
- `/backend/app/api/v1/endpoints/categories.py` - 카테고리 엔드포인트

### 마이그레이션
- `/backend/alembic/versions/001_create_categories_table.py` - 테이블 생성

---

## 기술 스택

- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0 + AsyncIO
- **DB**: PostgreSQL
- **Validation**: Pydantic v2
- **Migration**: Alembic

---

## 주의사항

1. **테넌트 격리**: 모든 쿼리는 `tenant_id`를 필수로 포함하여 테넌트별 데이터 격리 보장

2. **트랜잭션**: 부모 변경 시 하위 카테고리의 경로도 함께 업데이트되므로 트랜잭션 필수

3. **소프트 삭제**: 물리적으로 삭제되지 않으므로 쿼리에 `is_deleted = False` 조건 필수

4. **권한 검증**: TODO - auth-backend 통합 시 권한 검증 강화

---

## 참고 자료

- [CLAUDE.md](/CLAUDE.md) - 프로젝트 코딩 규칙
- [SHARED_SCHEMA.md](/SHARED_SCHEMA.md) - 공유 테이블 정의
