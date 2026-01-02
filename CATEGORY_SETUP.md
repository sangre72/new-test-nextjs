# 카테고리 관리 시스템 - 빠른 시작 가이드

**상태**: 구현 완료 ✅

---

## 📦 설치 및 설정

### 1. 마이그레이션 적용

```bash
cd backend
alembic upgrade head
```

**결과**: `categories` 테이블 생성 (24개 컬럼, 7개 인덱스)

### 2. 서버 시작

```bash
# Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend (선택사항)
cd frontend
npm run dev
```

### 3. API 문서 확인

브라우저에서 접속:
```
http://localhost:8000/docs
```

**Swagger UI에서 모든 엔드포인트 테스트 가능**

---

## 🎯 기본 사용법

### API 호출

#### 1. 카테고리 생성

```bash
curl -X POST http://localhost:8000/api/v1/categories \
  -H "Content-Type: application/json" \
  -d '{
    "board_id": 1,
    "category_name": "공지사항",
    "category_code": "notice",
    "description": "공지사항 카테고리",
    "read_permission": "all",
    "write_permission": "members"
  }'
```

**응답:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "board_id": 1,
    "category_name": "공지사항",
    "category_code": "notice",
    "depth": 0,
    "path": "/1/1/",
    ...
  }
}
```

#### 2. 계층형 카테고리 조회

```bash
curl http://localhost:8000/api/v1/categories/board/1
```

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "category_name": "공지사항",
      "depth": 0,
      "children": [
        {
          "id": 2,
          "category_name": "일반",
          "depth": 1,
          "children": []
        }
      ]
    }
  ],
  "total": 1
}
```

#### 3. 카테고리 이동 (부모 변경)

```bash
# 카테고리 3을 카테고리 1 아래로 이동
curl -X PUT "http://localhost:8000/api/v1/categories/3/move?parent_id=1"
```

#### 4. 순서 변경 (드래그앤드롭)

```bash
curl -X PUT http://localhost:8000/api/v1/categories/reorder \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 3,
    "parent_id": 1,
    "sort_order": 5
  }'
```

---

## 📊 데이터 구조

### 테이블 스키마

```sql
categories (
  id: BIGINT PK,
  tenant_id: BIGINT FK,
  board_id: BIGINT,
  parent_id: BIGINT FK (self-ref),
  depth: INT,
  path: VARCHAR(500),
  category_name: VARCHAR(100),
  category_code: VARCHAR(50),
  description: TEXT,
  sort_order: INT,
  icon: VARCHAR(50),
  color: VARCHAR(20),
  read_permission: VARCHAR(50) = 'all',
  write_permission: VARCHAR(50) = 'all',
  post_count: INT = 0,
  created_at, created_by,
  updated_at, updated_by,
  is_active, is_deleted
)
```

### 계층 구조 예시

```
공지사항 (id=1, depth=0, path=/1/1/)
├── 일반 (id=2, depth=1, path=/1/1/2/)
│   ├── 서비스 안내 (id=3, depth=2, path=/1/1/2/3/)
│   └── 점검 안내 (id=4, depth=2, path=/1/1/2/4/)
├── 긴급 (id=5, depth=1, path=/1/1/5/)
└── 이벤트 (id=6, depth=1, path=/1/1/6/)
    ├── 진행중 (id=7, depth=2, path=/1/1/6/7/)
    └── 종료 (id=8, depth=2, path=/1/1/6/8/)
```

---

## 🔑 핵심 개념

### 1. Depth (깊이)

- 최상위: `depth = 0`
- 1단계 하위: `depth = 1`
- 2단계 하위: `depth = 2`
- ...무한 지원

### 2. Path (경로)

- 형식: `/board_id/cat_id_1/cat_id_2/...`
- 예: `/1/1/2/3/` → 게시판 1의 카테고리 1 → 2 → 3
- 용도: 모든 하위 카테고리 한 번에 조회
  ```sql
  SELECT * FROM categories WHERE path LIKE '/1/1/2/%'
  ```

### 3. Sort Order (정렬 순서)

- 숫자가 낮을수록 앞
- 같은 부모 아래의 카테고리들을 정렬
- 드래그앤드롭 시 업데이트

### 4. Post Count (게시글 수)

- 캐시된 값 (매번 계산하지 않음)
- 게시글 추가/삭제 시에만 동기화
- 빠른 조회 성능 제공

---

## ⚡ 성능 최적화

### 경로 기반 쿼리

```python
# 모든 하위 카테고리 한 번에 조회
descendants = await session.execute(
    select(Category).where(
        Category.path.startswith("/1/2/")
    )
)
```

**장점:**
- 1번의 SQL 쿼리로 조회
- 재귀 함수 불필요
- 인덱스 활용으로 빠른 성능

### 게시글 수 캐싱

```python
# ❌ 비효율적: 매번 COUNT 쿼리
post_count = session.query(Post).filter_by(category_id=1).count()

# ✅ 효율적: 미리 계산된 값 사용
print(category.post_count)

# 게시글 추가/삭제 시에만 동기화
await CategoryService.increment_post_count(session, category_id)
```

### 인덱스

생성된 인덱스:
- `path`: 경로 기반 하위 조회
- `sort_order`: 정렬 순서 조회
- `tenant_id, board_id`: 테넌트 + 게시판별 조회
- `depth`: 깊이별 조회
- `parent_id`: 상위 카테고리별 조회

---

## 🔒 보안

### 입력 검증

```python
# category_code: 영문 소문자, 숫자, 언더스코어만
pattern=r"^[a-z0-9_]+$"

# 길이 제약
category_name: min_length=1, max_length=100
```

### 테넌트 격리

```python
# 모든 쿼리에 tenant_id 포함 (필수)
await CategoryService.get_category_by_id(
    session=session,
    category_id=category_id,
    tenant_id=tenant_id  # 다른 테넌트의 데이터 접근 불가
)
```

### 순환 참조 방지

```python
# 자신의 하위를 상위로 설정하는 것을 자동으로 방지
if new_parent_id in [d.id for d in descendants]:
    raise ValueError("순환 참조 불가")
```

### 권한 확인

```python
# Admin만 생성/수정/삭제 가능
@router.post("", dependencies=[Depends(_check_admin_permission)])
```

---

## 🐛 문제 해결

### "이미 존재하는 카테고리 코드입니다"

**원인:** 같은 게시판 내에서 중복된 `category_code`

**해결:** 고유한 코드 사용
```python
"category_code": "notice_general"  # "notice" 대신
```

### "하위 카테고리가 있어 삭제할 수 없습니다"

**원인:** 삭제하려는 카테고리에 하위가 있음

**해결:** 하위 카테고리 먼저 삭제 또는 이동
```bash
# 1. 하위 카테고리를 다른 부모로 이동
curl -X PUT "http://localhost:8000/api/v1/categories/3/move?parent_id=5"

# 2. 그 후 삭제
curl -X DELETE http://localhost:8000/api/v1/categories/2
```

### "게시글이 있어 삭제할 수 없습니다"

**원인:** `post_count > 0`

**해결:** 게시글을 다른 카테고리로 이동 후 삭제
```bash
# 1. 게시글을 다른 카테고리로 이동 (board-generator에서 구현)
# 2. 카테고리 삭제
curl -X DELETE http://localhost:8000/api/v1/categories/2
```

---

## 📚 상세 문서

더 자세한 내용은 다음 문서를 참고하세요:

1. **CATEGORY_MANAGER.md** (770+ 줄)
   - API 엔드포인트 완전 가이드
   - 요청/응답 예시
   - 권한 체계
   - 서비스 레이어 API
   - 사용 예시 (5가지)
   - 문제 해결
   - 성능 최적화

2. **CATEGORY_IMPLEMENTATION.md**
   - 구현 완료 보고서
   - 생성된 파일 목록
   - 아키텍처
   - 보안 구현
   - 성능 최적화
   - 구현 체크리스트
   - 다음 단계

---

## 🚀 다음 단계

### 1. 게시판 통합 (board-generator)

```python
# 게시판 생성 시 기본 카테고리 자동 생성
board = await create_board(...)
await create_default_categories(
    board_id=board.id,
    categories=["공지사항", "자유게시판", "Q&A"]
)
```

### 2. 게시글 통합 (post-manager)

```python
# 게시글 생성 시 카테고리 필수
post = await create_post(
    category_id=1,  # 필수
    title="제목",
    content="내용"
)

# 게시글 삭제 시 카테고리 카운트 감소
await CategoryService.decrement_post_count(session, post.category_id)
```

### 3. 권한 강화 (auth-backend)

```python
# 게시판별 관리자 권한 확인
await check_board_admin_permission(
    user_id=user_id,
    board_id=board_id,
    tenant_id=tenant_id
)
```

### 4. 프론트엔드 (Next.js)

```tsx
// 카테고리 목록 조회
const { data: categories } = useFetch(`/api/v1/categories/board/${boardId}`);

// 계층형 드래그앤드롭 UI
<CategoryTree categories={categories} onReorder={handleReorder} />
```

---

## 📞 테스트

### Postman 컬렉션

```json
{
  "info": { "name": "Category API" },
  "item": [
    {
      "name": "Create Category",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/v1/categories",
        "body": {
          "board_id": 1,
          "category_name": "공지사항",
          "category_code": "notice"
        }
      }
    },
    {
      "name": "List Categories (Tree)",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/v1/categories/board/1"
      }
    }
  ]
}
```

### cURL 테스트 스크립트

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# 1. 카테고리 생성
echo "Creating categories..."
curl -X POST "$BASE_URL/api/v1/categories" \
  -H "Content-Type: application/json" \
  -d '{"board_id":1,"category_name":"공지","category_code":"notice"}'

# 2. 목록 조회
echo "\nListing categories..."
curl "$BASE_URL/api/v1/categories/board/1"

# 3. 상세 조회
echo "\nGetting category..."
curl "$BASE_URL/api/v1/categories/1"

# 4. 수정
echo "\nUpdating category..."
curl -X PUT "$BASE_URL/api/v1/categories/1" \
  -H "Content-Type: application/json" \
  -d '{"category_name":"공지사항"}'

# 5. 삭제
echo "\nDeleting category..."
curl -X DELETE "$BASE_URL/api/v1/categories/1"
```

---

## 📝 체크리스트

### 초기 설정
- [ ] 마이그레이션 적용 (`alembic upgrade head`)
- [ ] 서버 시작 (backend + frontend)
- [ ] API 문서 확인 (`/docs`)
- [ ] 첫 카테고리 생성 및 테스트

### 기본 기능 확인
- [ ] 카테고리 CRUD (생성, 조회, 수정, 삭제)
- [ ] 계층형 조회 (tree)
- [ ] 평면 조회 (flat)
- [ ] 부모 변경 (move)
- [ ] 순서 변경 (reorder)

### 고급 기능 확인
- [ ] 깊은 계층 생성 (3+ 레벨)
- [ ] 경로 확인 (path가 올바르게 갱신되는지)
- [ ] 게시글 수 캐싱 (post_count)
- [ ] 소프트 삭제 (is_deleted flag)

### 보안 확인
- [ ] 테넌트 격리 테스트
- [ ] 권한 확인 (Admin만 생성/수정/삭제)
- [ ] 순환 참조 방지
- [ ] 입력 검증 (category_code 형식)

---

## 💡 팁

### 1. 개발 모드에서 권한 무시하기

```python
# 개발 시에만 사용 (프로덕션 금지)
async def _check_admin_permission():
    # return None  # 권한 확인 생략
    return "dev-user"
```

### 2. 데이터베이스에서 직접 조회

```sql
-- 계층형 보기
SELECT id, parent_id, depth, path, category_name
FROM categories
WHERE board_id = 1
ORDER BY path, sort_order;

-- 특정 깊이의 카테고리
SELECT * FROM categories WHERE depth = 2;

-- 모든 하위 카테고리
SELECT * FROM categories WHERE path LIKE '/1/2/%';
```

### 3. 성능 모니터링

```sql
-- 인덱스 활용 확인
EXPLAIN SELECT * FROM categories WHERE path LIKE '/1/2/%';

-- 테이블 크기
SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2)
FROM information_schema.TABLES
WHERE table_name = 'categories';
```

---

## 📄 파일 위치

```
backend/
├── app/
│   ├── models/
│   │   └── category.py          # Category 모델
│   ├── schemas/
│   │   └── category.py          # Pydantic 스키마
│   ├── services/
│   │   └── category.py          # 비즈니스 로직
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── categories.py # API 엔드포인트
│   └── main.py                  # 라우터 등록
└── alembic/
    └── versions/
        └── 001_create_categories_table.py  # 마이그레이션

documents/
├── CATEGORY_MANAGER.md          # 완전 가이드
├── CATEGORY_IMPLEMENTATION.md   # 구현 보고서
└── CATEGORY_SETUP.md            # 이 파일
```

---

## 🎓 학습 자료

### 개념 이해

1. **계층형 데이터 구조**
   - Adjacency List (parent_id): 현재 구조
   - Nested Set: 쿼리 최적화 (복잡)
   - Closure Table: 모든 관계 저장 (공간 많음)

2. **경로 기반 쿼리**
   - 트리 순회: 깊이 우선(DFS), 너비 우선(BFS)
   - 경로 인덱싱: 시간 O(1), 공간 O(n)

3. **성능 최적화**
   - 인덱스 전략
   - 쿼리 플랜 분석
   - 캐싱 전략

### 참고 자료

- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/
- FastAPI: https://fastapi.tiangolo.com/
- Pydantic v2: https://docs.pydantic.dev/
- PostgreSQL: https://www.postgresql.org/docs/

---

## ✨ 완료!

카테고리 관리 시스템 설정이 완료되었습니다.

**다음 작업:**
1. 마이그레이션 적용
2. 서버 시작
3. API 테스트
4. 다른 시스템과 통합 (board-generator, post-manager 등)

**지원:**
- CATEGORY_MANAGER.md: 문제 해결 섹션 참고
- API 문서: http://localhost:8000/docs
- 깃허브 이슈: 발생한 문제 리포팅

Happy coding! 🚀
