# 프로젝트 개요

FastAPI + Next.js + PostgreSQL 기반 웹 애플리케이션

## 기술 스택

### Backend
- **Python**: 3.11+
- **FastAPI**: 0.128.0
- **SQLAlchemy**: 2.0+ (ORM)
- **Alembic**: 1.13+ (DB Migration)
- **Pydantic**: 2.0+ (Validation)
- **PostgreSQL**: 15+

### Frontend
- **React**: 19.2.3
- **Next.js**: 16.1.1 (App Router)
- **TypeScript**: 5.0+
- **TanStack Query**: 5.90.16 (React Query)
- **Tailwind CSS**: 3.4+
- **Axios**: 1.6+

### DevOps
- **Docker & Docker Compose**
- **PostgreSQL**: 15-alpine

---

## 프로젝트 구조

```
/Users/bumsuklee/git/new-test/
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── api/            # API 엔드포인트
│   │   │   ├── v1/
│   │   │   │   └── endpoints/
│   │   │   ├── deps.py     # 의존성 주입
│   │   │   └── tenant_middleware.py
│   │   ├── core/           # 설정 및 보안
│   │   │   └── config.py
│   │   ├── db/             # 데이터베이스
│   │   │   ├── session.py
│   │   │   ├── base.py
│   │   │   └── init_shared_schema.py
│   │   ├── models/         # SQLAlchemy 모델
│   │   │   └── shared.py   # 공유 스키마 모델
│   │   ├── schemas/        # Pydantic 스키마
│   │   │   └── shared.py
│   │   ├── services/       # 비즈니스 로직
│   │   │   └── shared.py
│   │   └── main.py
│   ├── alembic/            # DB 마이그레이션
│   │   └── versions/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/               # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/           # App Router
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/    # React 컴포넌트
│   │   ├── lib/          # 유틸리티
│   │   │   └── api/      # API 클라이언트
│   │   └── types/        # TypeScript 타입
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── next.config.js
│   └── .env.local.example
│
├── docker-compose.yml
├── .gitignore
└── CLAUDE.md (이 파일)
```

---

## 빠른 시작

### 1. 환경 변수 설정

```bash
# Backend
cp backend/.env.example backend/.env
# DATABASE_URL, SECRET_KEY 등 수정

# Frontend
cp frontend/.env.local.example frontend/.env.local
# NEXT_PUBLIC_API_URL 수정
```

### 2. Docker로 시작 (권장)

```bash
# PostgreSQL + Backend + Frontend 모두 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 3. 로컬 개발 모드

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# DB 마이그레이션
alembic upgrade head

# 서버 실행 (http://localhost:8000)
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
```

---

## 데이터베이스 스키마

### Shared Schema (공유 데이터)
- `tenants`: 테넌트(사이트) 관리
- `categories`: 카테고리 관리 (계층 구조 지원)
- `menus`: 메뉴 관리
- `users`: 사용자
- `roles`: 역할
- `permissions`: 권한

### Tenant Schema (사이트별 격리 데이터)
- 각 테넌트는 독립적인 스키마를 가짐
- 예: `tenant_abc` 스키마에 `posts`, `comments` 등

---

## 사용 가능한 Claude Agents/Skills

프로젝트 개발 시 다음 명령어로 각 기능을 자동 생성/관리할 수 있습니다:

### 핵심 시스템

#### 1. Shared Schema (공유 스키마)
```bash
Use shared-schema --init
Use shared-schema --add-table tablename
```
- 테넌트, 사용자, 역할, 권한 등 공유 데이터 관리
- 멀티테넌트 기본 구조 생성

#### 2. Tenant Manager (테넌트 관리)
```bash
Use tenant-manager --init
Use tenant-manager --add-feature schema-isolation
```
- 멀티사이트/멀티테넌트 관리
- 도메인별 설정, 테마, 스키마 격리

#### 3. Auth Backend (인증 백엔드)
```bash
Use auth-backend --init --type=phone
Use auth-backend --init --type=email
Use auth-backend --init --type=social --providers=kakao,naver,google
```
- JWT 토큰 기반 인증
- 휴대폰 OTP, 이메일/비밀번호, 소셜 로그인

#### 4. Auth Frontend (인증 프론트엔드)
```bash
Use auth-frontend --init
Use auth-frontend --add-social kakao
```
- 로그인/회원가입 UI
- 토큰 관리, 자동 갱신

#### 5. Menu Backend (메뉴 관리 백엔드)
```bash
Use menu-backend --init
Use menu-backend --add-feature multi-level
```
- 계층형 메뉴 구조
- 권한 기반 메뉴 표시

#### 6. Menu Frontend (메뉴 관리 프론트엔드)
```bash
Use menu-frontend --init
Use menu-frontend --add-component mobile-drawer
```
- 반응형 네비게이션
- 관리자 메뉴 편집기

#### 7. Category Manager (카테고리 관리)
```bash
Use category-manager --init
Use category-manager --add-feature drag-drop
```
- 무한 깊이 계층 구조
- 드래그&드롭 정렬

### 게시판 시스템

#### 8. Board Generator (게시판 생성기)
```bash
Use board-generator --template notice      # 공지사항
Use board-generator --template free        # 자유게시판
Use board-generator --template qna         # Q&A
Use board-generator --template faq         # FAQ
Use board-generator --template gallery     # 갤러리
Use board-generator --template review      # 리뷰
Use board-generator --custom               # 커스텀 게시판
```
- 템플릿 기반 게시판 자동 생성
- CRUD, 검색, 페이징, 첨부파일

### 유틸리티

#### 9. API Generator (API 자동 생성)
```bash
Use api-generator --model User --crud
Use api-generator --from-schema schema.yaml
```
- REST API CRUD 자동 생성
- OpenAPI 문서 자동화

#### 10. Component Generator (컴포넌트 생성)
```bash
Use component-generator --type form --name UserForm
Use component-generator --type table --name UserTable
```
- React 컴포넌트 템플릿 생성
- Form, Table, Modal 등

---

## API 문서

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 환경 변수

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Security
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Multi-tenancy
ENABLE_MULTI_TENANCY=true
DEFAULT_TENANT_SCHEMA=public
```

### Frontend (.env.local)
```env
# API
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Auth
NEXT_PUBLIC_AUTH_STORAGE_KEY=auth_token

# Social Login (선택)
NEXT_PUBLIC_KAKAO_APP_KEY=your_kakao_key
NEXT_PUBLIC_NAVER_CLIENT_ID=your_naver_id
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_id
```

---

## 개발 워크플로우

### 1. 새 기능 개발
```bash
# 1. Feature 브랜치 생성
git checkout -b feature/new-feature

# 2. Backend: API 엔드포인트 작성
# - app/api/v1/endpoints/new_feature.py
# - app/models/new_feature.py
# - app/schemas/new_feature.py
# - app/services/new_feature.py

# 3. DB 마이그레이션 생성
cd backend
alembic revision --autogenerate -m "Add new_feature table"
alembic upgrade head

# 4. Frontend: 컴포넌트 작성
# - src/components/NewFeature.tsx
# - src/lib/api/newFeature.ts

# 5. 테스트
cd backend && pytest
cd frontend && npm test

# 6. 커밋 & PR
git add .
git commit -m "feat: Add new feature"
git push origin feature/new-feature
```

### 2. DB 스키마 변경
```bash
cd backend

# 모델 수정 후 마이그레이션 생성
alembic revision --autogenerate -m "Description"

# 마이그레이션 검토
cat alembic/versions/xxxxx_description.py

# 적용
alembic upgrade head

# 롤백 (필요시)
alembic downgrade -1
```

### 3. 테스트
```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm test
npm run test:e2e  # E2E 테스트 (설정 필요)
```

---

## 배포

### Docker로 배포
```bash
# 프로덕션 빌드
docker-compose -f docker-compose.prod.yml up -d

# 또는 개별 빌드
docker build -t myapp-backend ./backend
docker build -t myapp-frontend ./frontend
```

### 환경별 설정
- **개발**: `.env`, `.env.local`
- **스테이징**: `.env.staging`
- **프로덕션**: `.env.production` (절대 커밋하지 말 것)

---

## 문제 해결

### Backend 문제

#### DB 연결 실패
```bash
# PostgreSQL 실행 확인
docker-compose ps
# 또는
pg_isready -h localhost -p 5432

# DATABASE_URL 확인
cat backend/.env | grep DATABASE_URL
```

#### 마이그레이션 에러
```bash
# 마이그레이션 히스토리 확인
alembic history

# 현재 버전 확인
alembic current

# 초기화 (주의: 데이터 손실)
alembic downgrade base
alembic upgrade head
```

### Frontend 문제

#### API 호출 실패
```bash
# API URL 확인
cat frontend/.env.local | grep NEXT_PUBLIC_API_URL

# CORS 설정 확인 (backend/.env)
cat backend/.env | grep CORS
```

#### 빌드 에러
```bash
# 캐시 삭제 후 재설치
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

---

## 다음 단계

1. 환경 변수 설정 완료
2. Docker Compose로 전체 스택 실행
3. 필요한 Agent 호출하여 기능 추가:
   ```bash
   Use auth-backend --init --type=email
   Use auth-frontend --init
   Use menu-backend --init
   Use menu-frontend --init
   Use category-manager --init
   Use board-generator --template notice
   ```
4. API 문서 확인 (http://localhost:8000/docs)
5. 프론트엔드 접속 (http://localhost:3000)

---

## 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Next.js 공식 문서](https://nextjs.org/docs)
- [SQLAlchemy 공식 문서](https://docs.sqlalchemy.org/)
- [TanStack Query 공식 문서](https://tanstack.com/query/latest)
- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)

---

## 라이선스

MIT License

---

**생성 일시**: 2026-01-03
**Claude Code Agent**: project-init v1.0
