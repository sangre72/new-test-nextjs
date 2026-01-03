# MyApp

FastAPI + Next.js + PostgreSQL 풀스택 웹 애플리케이션

## 기술 스택

### Backend
- Python 3.11+
- FastAPI 0.128.0
- SQLAlchemy 2.0 (ORM)
- Alembic (DB Migration)
- PostgreSQL 15+

### Frontend
- React 19.2.3
- Next.js 16.1.1 (App Router)
- TypeScript 5.7.3
- TanStack Query 5.90.16
- Tailwind CSS 3.4.17

### DevOps
- Docker & Docker Compose
- PostgreSQL 15-alpine

## 빠른 시작

### Option 1: Docker Compose (권장)

가장 빠른 방법. PostgreSQL, Backend, Frontend 모두 자동 실행.

```bash
# 1. 환경 변수 설정
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# 2. Docker Compose 실행
docker-compose up -d

# 3. 로그 확인
docker-compose logs -f
```

접속:
- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs
- Backend ReDoc: http://localhost:8000/redoc

### Option 2: 로컬 개발

#### 1. PostgreSQL 실행

```bash
# Docker로 PostgreSQL만 실행
docker run -d \
  --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=myapp \
  -p 5432:5432 \
  postgres:15-alpine
```

#### 2. Backend 실행

```bash
cd backend

# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집 (DATABASE_URL, SECRET_KEY 등)

# DB 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload
```

Backend 실행 후:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### 3. Frontend 실행

```bash
cd frontend

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.local.example .env.local
# .env.local 파일 편집

# 개발 서버 실행
npm run dev
```

Frontend 실행 후:
- App: http://localhost:3000

## 프로젝트 구조

```
/Users/bumsuklee/git/new-test/
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Config
│   │   ├── db/          # Database
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── main.py
│   ├── alembic/         # DB migrations
│   ├── tests/
│   └── requirements.txt
│
├── frontend/            # Next.js Frontend
│   ├── src/
│   │   ├── app/        # App Router
│   │   ├── components/ # React components
│   │   ├── lib/        # Utilities
│   │   └── types/      # TypeScript types
│   └── package.json
│
├── docker-compose.yml
├── .gitignore
├── README.md
└── CLAUDE.md           # 상세 문서
```

## 주요 기능

현재 기본 설정만 되어 있습니다. 다음 기능들을 Claude Agent로 추가할 수 있습니다:

### 사용 가능한 Claude Agents

#### 핵심 시스템
```bash
Use shared-schema --init              # 공유 스키마 (테넌트, 사용자, 권한)
Use tenant-manager --init             # 멀티테넌트 관리
Use auth-backend --init --type=phone  # 인증 (휴대폰 OTP)
Use auth-backend --init --type=email  # 인증 (이메일/비밀번호)
Use auth-backend --init --type=social # 소셜 로그인
Use auth-frontend --init              # 인증 UI
Use menu-backend --init               # 메뉴 관리 백엔드
Use menu-frontend --init              # 메뉴 관리 프론트엔드
Use category-manager --init           # 카테고리 관리
```

#### 게시판
```bash
Use board-generator --template notice   # 공지사항
Use board-generator --template free     # 자유게시판
Use board-generator --template qna      # Q&A
Use board-generator --template faq      # FAQ
Use board-generator --template gallery  # 갤러리
Use board-generator --template review   # 리뷰
```

자세한 내용은 `CLAUDE.md` 참조

## 개발 워크플로우

### 1. 새 기능 개발

```bash
# Feature 브랜치 생성
git checkout -b feature/new-feature

# Backend: 모델, 스키마, 서비스, API 작성
# Frontend: 컴포넌트, API 클라이언트 작성

# DB 마이그레이션
cd backend
alembic revision --autogenerate -m "Add new feature"
alembic upgrade head

# 커밋
git add .
git commit -m "feat: Add new feature"
git push origin feature/new-feature
```

### 2. API 개발

Backend:
1. `app/models/` - SQLAlchemy 모델 정의
2. `app/schemas/` - Pydantic 스키마 정의
3. `app/services/` - 비즈니스 로직 작성
4. `app/api/v1/endpoints/` - API 엔드포인트 작성
5. `app/api/v1/__init__.py` - 라우터 등록

Frontend:
1. `src/types/` - TypeScript 타입 정의
2. `src/lib/api/` - API 클라이언트 함수
3. `src/components/` - React 컴포넌트

### 3. 테스트

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## 환경 변수

### Backend (.env)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/myapp
SECRET_KEY=your-secret-key-change-this
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 문제 해결

### Docker 관련

```bash
# 컨테이너 재시작
docker-compose restart

# 로그 확인
docker-compose logs -f backend
docker-compose logs -f frontend

# 컨테이너 삭제 후 재생성
docker-compose down
docker-compose up -d
```

### Backend 관련

```bash
# DB 연결 확인
pg_isready -h localhost -p 5432

# 마이그레이션 상태 확인
alembic current
alembic history

# 마이그레이션 초기화 (주의: 데이터 손실)
alembic downgrade base
alembic upgrade head
```

### Frontend 관련

```bash
# 캐시 삭제
rm -rf .next node_modules
npm install
npm run dev
```

## 배포

### Docker로 배포

```bash
# 프로덕션 빌드
docker-compose -f docker-compose.prod.yml up -d
```

### 개별 배포

Backend:
- Heroku, AWS Elastic Beanstalk, Google Cloud Run 등
- 환경 변수 설정 필수

Frontend:
- Vercel (권장), Netlify, AWS Amplify 등
- `npm run build` 후 배포

## 문서

- [CLAUDE.md](./CLAUDE.md) - 상세 프로젝트 가이드
- [backend/README.md](./backend/README.md) - Backend 문서
- [frontend/README.md](./frontend/README.md) - Frontend 문서

## 라이선스

MIT License

## 기여

이슈 및 PR 환영합니다.
