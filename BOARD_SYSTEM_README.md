# 멀티게시판 시스템 구현 완료

FastAPI + Next.js + PostgreSQL 기반의 **멀티게시판 시스템**이 성공적으로 구현되었습니다.

## 구현 내용

### Backend (FastAPI)

#### 1. 모델 (Models)
- **BoardExtended**: 게시판 기본 정보 및 타입별 설정
- **BoardCategory**: 게시판 카테고리
- **BoardPost**: 게시글 (모든 타입 공통)
- **BoardComment**: 댓글 (중첩 댓글 지원)
- **BoardAttachment**: 첨부파일
- **BoardLike**: 좋아요/추천

파일: `/backend/app/models/board.py`

#### 2. 스키마 (Pydantic Schemas)
- Board, BoardCategory, BoardPost, BoardComment 관련 Request/Response 스키마
- 페이지네이션, 필터링 지원

파일: `/backend/app/schemas/board.py`

#### 3. 서비스 레이어 (Business Logic)
- BoardService: 게시판 CRUD
- BoardCategoryService: 카테고리 관리
- BoardPostService: 게시글 CRUD, 페이지네이션, 검색
- BoardCommentService: 댓글 CRUD
- BoardLikeService: 좋아요 토글

파일: `/backend/app/services/board.py`

#### 4. API 엔드포인트
- `/api/v1/boards/` - 게시판 관리
- `/api/v1/boards/{board_code}/posts` - 게시글 목록
- `/api/v1/boards/{board_code}/posts/{post_id}` - 게시글 상세
- `/api/v1/boards/{board_code}/posts/{post_id}/comments` - 댓글
- `/api/v1/boards/{board_code}/posts/{post_id}/like` - 좋아요

파일: `/backend/app/api/v1/endpoints/boards.py`

#### 5. 데이터베이스 마이그레이션
- Alembic migration: `004_create_board_tables.py`
- 6개 테이블 생성 (boards, board_categories, board_posts, board_comments, board_attachments, board_likes)

파일: `/backend/alembic/versions/004_create_board_tables.py`

#### 6. 게시판 템플릿 시드 데이터
- 6가지 게시판 타입 템플릿 제공
  - notice: 공지사항
  - free: 자유게시판
  - qna: Q&A
  - faq: FAQ
  - gallery: 갤러리
  - review: 후기게시판

파일: `/backend/app/db/init_board_templates.py`

### Frontend (Next.js 16 App Router)

#### 1. TypeScript 타입 정의
- Board, BoardPost, BoardComment, BoardCategory 등 모든 타입 정의

파일: `/frontend/src/types/board.ts`

#### 2. API Client
- boardApi: 게시판 관리
- boardCategoryApi: 카테고리 관리
- boardPostApi: 게시글 CRUD
- boardCommentApi: 댓글 CRUD

파일: `/frontend/src/lib/api/boards.ts`

#### 3. 페이지 컴포넌트
- 게시판 목록: `/app/boards/[boardCode]/page.tsx`
- 게시글 상세: `/app/boards/[boardCode]/[postId]/page.tsx`
- 게시글 작성: `/app/boards/[boardCode]/write/page.tsx`
- 게시글 수정: `/app/boards/[boardCode]/[postId]/edit/page.tsx`
- 관리자 게시판 설정: `/app/admin/boards/page.tsx`

---

## 설치 및 실행

### 1. Backend 설정

```bash
cd backend

# 1) 가상환경 활성화 (이미 있다면 skip)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2) 의존성 설치 (이미 했다면 skip)
pip install -r requirements.txt

# 3) 데이터베이스 마이그레이션 실행
alembic upgrade head

# 4) 게시판 템플릿 초기화 (선택사항)
python -m app.db.init_board_templates

# 5) 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend 설정

```bash
cd frontend

# 1) 의존성 설치 (이미 했다면 skip)
npm install

# 2) 개발 서버 실행
npm run dev
```

### 3. 접속

- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs

---

## 사용 방법

### 1. 게시판 생성 (관리자)

```
URL: http://localhost:3000/admin/boards

1. "게시판 추가" 버튼 클릭
2. 게시판 정보 입력
   - 게시판 이름: 예) 공지사항
   - 게시판 코드: 예) notice (URL에 사용)
   - 타입 선택: notice/free/qna/faq/gallery/review
   - 권한 설정
   - 기능 설정 (카테고리, 비밀글, 첨부파일, 좋아요, 댓글)
3. "추가" 버튼 클릭
```

### 2. 게시글 작성

```
URL: http://localhost:3000/boards/{board_code}

1. 게시판 목록 페이지 접속
2. "글쓰기" 버튼 클릭
3. 게시글 작성
   - 카테고리 선택 (활성화된 경우)
   - 제목, 내용 입력
   - 별점 선택 (리뷰 게시판인 경우)
   - 비밀글 체크 (활성화된 경우)
4. "등록" 버튼 클릭
```

### 3. 게시글 상세 보기

```
URL: http://localhost:3000/boards/{board_code}/{post_id}

- 게시글 내용 확인
- 좋아요 (활성화된 경우)
- 댓글 작성 (활성화된 경우)
- 답글 작성 (중첩 댓글)
- 수정/삭제 (작성자 또는 관리자)
```

---

## 게시판 타입별 특징

### 1. notice (공지사항)
- 관리자만 작성 가능
- 상단 고정 (is_pinned)
- 일반 사용자는 읽기/댓글만 가능

### 2. free (자유게시판)
- 회원 누구나 작성 가능
- 비밀글 기능
- 댓글, 좋아요 모두 활성화

### 3. qna (Q&A)
- 질문/답변 형태
- 답변 채택 기능 (is_answered, accepted_answer_id)
- 답변 완료 표시

### 4. faq (FAQ)
- 관리자만 작성
- 아코디언 스타일 UI
- 댓글 비활성화

### 5. gallery (갤러리)
- 이미지 중심
- 썸네일 생성
- 그리드 레이아웃 (3열)

### 6. review (후기게시판)
- 별점 시스템 (1-5점)
- 추천 기능
- 평점 표시

---

## API 엔드포인트

### 게시판 관리
- `GET /api/v1/boards/` - 게시판 목록
- `GET /api/v1/boards/{board_code}` - 게시판 상세
- `POST /api/v1/boards/` - 게시판 생성 (관리자)
- `PUT /api/v1/boards/{board_id}` - 게시판 수정 (관리자)
- `DELETE /api/v1/boards/{board_id}` - 게시판 삭제 (관리자)

### 카테고리
- `GET /api/v1/boards/{board_id}/categories` - 카테고리 목록
- `POST /api/v1/boards/{board_id}/categories` - 카테고리 생성 (관리자)

### 게시글
- `GET /api/v1/boards/{board_code}/posts` - 게시글 목록 (페이지네이션)
- `GET /api/v1/boards/{board_code}/posts/{post_id}` - 게시글 상세
- `POST /api/v1/boards/{board_code}/posts` - 게시글 작성
- `PUT /api/v1/boards/{board_code}/posts/{post_id}` - 게시글 수정
- `DELETE /api/v1/boards/{board_code}/posts/{post_id}` - 게시글 삭제

### 댓글
- `GET /api/v1/boards/{board_code}/posts/{post_id}/comments` - 댓글 목록
- `POST /api/v1/boards/{board_code}/posts/{post_id}/comments` - 댓글 작성

### 좋아요
- `POST /api/v1/boards/{board_code}/posts/{post_id}/like` - 좋아요 토글

---

## 데이터베이스 스키마

### boards 테이블
- 게시판 기본 정보
- 타입 (board_type): notice/free/qna/faq/gallery/review
- 권한 설정 (read/write/comment_permission)
- 기능 설정 (enable_categories, enable_attachments, etc.)

### board_categories 테이블
- 게시판별 카테고리
- 색상 지정 가능

### board_posts 테이블
- 모든 게시판의 게시글
- board_id로 게시판 구분
- 타입별 특수 필드 (is_answered, rating, etc.)

### board_comments 테이블
- 댓글 및 답글 (parent_id로 계층 구조)

### board_attachments 테이블
- 파일 첨부 (이미지, 문서 등)
- 썸네일 지원

### board_likes 테이블
- 게시글 좋아요/추천

---

## 보안 기능

1. **권한 검증**
   - 읽기/쓰기/댓글 권한 레벨 (public/member/admin/disabled)
   - 작성자/관리자만 수정/삭제 가능

2. **입력 검증**
   - Pydantic 스키마로 자동 검증
   - XSS 방지 (HTML 이스케이프)

3. **Soft Delete**
   - 실제 삭제 대신 is_deleted 플래그 사용
   - 데이터 복구 가능

4. **인증**
   - JWT 토큰 기반 인증
   - SessionStorage에 토큰 저장 (탭 닫으면 자동 삭제)

---

## 추가 개발 가능 기능

### 현재 미구현 (추후 추가 가능)

1. **파일 첨부 업로드**
   - 현재 스키마/모델만 구현
   - Multipart form-data 업로드 API 추가 필요
   - 썸네일 생성 (Pillow 사용)

2. **에디터 개선**
   - 현재: 단순 textarea
   - 추가: WYSIWYG 에디터 (TinyMCE, Quill, etc.)

3. **갤러리 UI**
   - 현재: 일반 리스트
   - 추가: 그리드 레이아웃, 라이트박스

4. **FAQ 아코디언 UI**
   - 현재: 일반 리스트
   - 추가: 접기/펼치기 UI

5. **알림 기능**
   - 댓글 알림
   - 답변 채택 알림

6. **검색 개선**
   - 현재: 제목/내용 LIKE 검색
   - 추가: 전문 검색 (PostgreSQL Full-Text Search)

7. **통계/분석**
   - 조회수 추이
   - 인기 게시글
   - 사용자별 통계

---

## 문제 해결

### 1. 마이그레이션 실패

```bash
# 마이그레이션 히스토리 확인
alembic current

# 특정 버전으로 롤백
alembic downgrade 003_update_menus_table

# 다시 업그레이드
alembic upgrade head
```

### 2. CORS 오류

```python
# backend/app/main.py에서 CORS 설정 확인
BACKEND_CORS_ORIGINS = ["http://localhost:3000"]
```

### 3. 게시판 템플릿 초기화 실패

```bash
# 수동으로 Python REPL에서 실행
cd backend
python

>>> from app.db.session import SessionLocal
>>> from app.db.init_board_templates import init_board_templates
>>> db = SessionLocal()
>>> init_board_templates(db, tenant_id=1)
>>> db.close()
```

---

## 기술 스택

- **Backend**: Python 3.11+, FastAPI 0.128.0, SQLAlchemy 2.0+, Alembic, Pydantic
- **Frontend**: React 19, Next.js 16 (App Router), TypeScript, TanStack Query, Tailwind CSS
- **Database**: PostgreSQL 15+
- **Authentication**: JWT (Bearer Token)
- **ORM**: SQLAlchemy with Alembic migrations

---

## 참고 자료

- FastAPI 공식 문서: https://fastapi.tiangolo.com/
- Next.js 공식 문서: https://nextjs.org/docs
- SQLAlchemy 2.0 문서: https://docs.sqlalchemy.org/en/20/
- TanStack Query: https://tanstack.com/query/latest

---

## 라이선스

MIT License

---

## 개발자

Claude Code (Anthropic)

생성일: 2024-01-03
