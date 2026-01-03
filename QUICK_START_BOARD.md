# 멀티게시판 시스템 빠른 시작 가이드

## 1. 데이터베이스 마이그레이션 실행

```bash
cd /Users/bumsuklee/git/new-test/backend

# 가상환경 활성화 (필요한 경우)
source venv/bin/activate  # 또는 conda activate your-env

# 의존성 설치 확인
pip install -r requirements.txt

# 마이그레이션 실행
alembic upgrade head

# 마이그레이션 확인
alembic current
```

**예상 출력:**
```
INFO  [alembic.runtime.migration] Running upgrade 003_update_menus_table -> 004_create_board_tables, Create board tables
004_create_board_tables (head)
```

## 2. 게시판 템플릿 초기화 (선택사항)

6가지 게시판 타입(공지사항, 자유게시판, Q&A, FAQ, 갤러리, 후기)을 자동으로 생성합니다.

```bash
cd /Users/bumsuklee/git/new-test/backend

# 방법 1: 스크립트 실행
python -m app.db.init_board_templates

# 방법 2: Python REPL에서 실행
python
```

```python
from app.db.session import SessionLocal
from app.db.init_board_templates import init_board_templates

db = SessionLocal()
init_board_templates(db, tenant_id=1, created_by="admin")
db.close()
```

## 3. Backend 서버 실행

```bash
cd /Users/bumsuklee/git/new-test/backend

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**서버 실행 확인:**
- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

## 4. Frontend 서버 실행

```bash
cd /Users/bumsuklee/git/new-test/frontend

# 의존성 설치 (최초 1회)
npm install

# 개발 서버 실행
npm run dev
```

**Frontend 접속:**
- 메인: http://localhost:3000

## 5. 게시판 접속

### 사용자 게시판
- 공지사항: http://localhost:3000/boards/notice
- 자유게시판: http://localhost:3000/boards/free
- Q&A: http://localhost:3000/boards/qna
- FAQ: http://localhost:3000/boards/faq
- 갤러리: http://localhost:3000/boards/gallery
- 후기게시판: http://localhost:3000/boards/review

### 관리자 게시판 관리
- 게시판 설정: http://localhost:3000/admin/boards

## 6. API 테스트

### Swagger UI에서 테스트
http://localhost:8000/docs

### cURL로 테스트

```bash
# 1. 게시판 목록 조회
curl -X GET "http://localhost:8000/api/v1/boards/?tenant_id=1"

# 2. 특정 게시판 조회
curl -X GET "http://localhost:8000/api/v1/boards/notice?tenant_id=1"

# 3. 게시글 목록 조회
curl -X GET "http://localhost:8000/api/v1/boards/notice/posts?tenant_id=1&page=1&page_size=20"

# 4. 게시글 작성 (인증 필요)
curl -X POST "http://localhost:8000/api/v1/boards/notice/posts" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "board_id": 1,
    "tenant_id": 1,
    "title": "테스트 게시글",
    "content": "테스트 내용입니다."
  }'
```

## 7. 문제 해결

### 마이그레이션 오류

```bash
# 현재 버전 확인
alembic current

# 특정 버전으로 다운그레이드
alembic downgrade 003_update_menus_table

# 다시 업그레이드
alembic upgrade head

# 히스토리 확인
alembic history
```

### 데이터베이스 초기화 (주의: 모든 데이터 삭제)

```bash
# PostgreSQL 접속
psql -U your_user -d your_database

# 모든 테이블 삭제
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

# 마이그레이션 다시 실행
alembic upgrade head
```

### psycopg2 설치 오류

```bash
# macOS
brew install postgresql
pip install psycopg2-binary

# Ubuntu/Debian
sudo apt-get install libpq-dev
pip install psycopg2-binary

# Windows
pip install psycopg2-binary
```

## 8. 생성된 테이블 확인

PostgreSQL에 접속하여 테이블 확인:

```sql
-- 게시판 테이블 확인
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
AND tablename LIKE 'board%';

-- 예상 결과:
-- boards
-- board_categories
-- board_posts
-- board_comments
-- board_attachments
-- board_likes

-- 게시판 목록 확인
SELECT id, board_code, board_name, board_type, total_posts
FROM boards
WHERE is_deleted = false;

-- 게시판 카테고리 확인
SELECT bc.id, b.board_name, bc.category_name, bc.color
FROM board_categories bc
JOIN boards b ON bc.board_id = b.id
WHERE bc.is_deleted = false
ORDER BY b.id, bc.display_order;
```

## 9. 다음 단계

### 필수 작업
1. 로그인/회원가입 기능 구현 (이미 있다면 연동)
2. 인증 토큰을 API 요청에 포함
3. 권한 체크 로직 구현

### 선택적 개선
1. 파일 첨부 업로드 구현
2. WYSIWYG 에디터 추가 (TinyMCE, Quill 등)
3. 갤러리 그리드 UI 구현
4. FAQ 아코디언 UI 구현
5. 알림 기능 추가
6. 검색 기능 개선 (Full-Text Search)

## 10. 개발 참고

### Backend 코드 수정 후
```bash
# 서버가 자동으로 재시작됨 (--reload 옵션)
# 모델 변경 시 마이그레이션 생성
alembic revision --autogenerate -m "설명"
alembic upgrade head
```

### Frontend 코드 수정 후
```bash
# Next.js가 자동으로 Hot Reload
# 타입 변경 시 서버 재시작 필요
npm run dev
```

---

## 요약 체크리스트

- [ ] Backend 가상환경 활성화
- [ ] `pip install -r requirements.txt` 실행
- [ ] `alembic upgrade head` 실행
- [ ] (선택) 게시판 템플릿 초기화
- [ ] Backend 서버 실행 (port 8000)
- [ ] Frontend `npm install` (최초 1회)
- [ ] Frontend 서버 실행 (port 3000)
- [ ] 브라우저에서 http://localhost:3000/boards/notice 접속
- [ ] 게시판이 보이면 성공!

---

**문제가 발생하면 `BOARD_SYSTEM_README.md`의 "문제 해결" 섹션을 참고하세요.**
