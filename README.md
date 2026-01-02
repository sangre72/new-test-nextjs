# New Test Project

FastAPI + Next.js 15 + TypeScript + PostgreSQL 기반 웹 애플리케이션

## 기술 스택

### Backend
- FastAPI 0.109+
- Python 3.11+
- PostgreSQL 15
- Redis 7
- SQLAlchemy 2.0 (AsyncIO)
- Alembic (마이그레이션)

### Frontend
- Next.js 15
- React 19
- TypeScript 5
- Tailwind CSS 3.4
- Zustand (상태 관리)

## 시작하기

### 1. 사전 요구사항

- Python 3.11+
- Node.js 20+
- PostgreSQL 15
- Redis 7
- Docker (선택)

### 2. 데이터베이스 설정 (Docker 사용)

```bash
# PostgreSQL
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=newtest \
  -p 5432:5432 \
  postgres:15

# Redis
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7
```

### 3. Backend 설정

```bash
cd backend

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일 편집 (DATABASE_URL, SECRET_KEY 등)

# 마이그레이션 실행 (인증 시스템 구축 후)
# alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend 설정

```bash
cd frontend

# 의존성 설치
npm install

# 환경변수 설정
cp .env.local.example .env.local
# .env.local 파일 편집 (API URL 등)

# 개발 서버 실행
npm run dev
```

### 5. 접속

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- API Redoc: http://localhost:8000/redoc

## 프로젝트 초기화

CLAUDE.md 파일을 참조하여 다음 순서로 초기화하세요:

```bash
# 1. 공유 스키마 초기화
Use shared-schema --init

# 2. 인증 시스템 구축
Use auth-backend --init --type=phone
Use auth-frontend --init

# 3. 메뉴 관리 시스템 구축
Use menu-backend --init
Use menu-frontend --init

# 4. 게시판 생성
Use board-generator --init
Use board-generator --template notice
```

## 프로젝트 구조

```
new-test/
├── backend/                 # FastAPI 백엔드
│   ├── alembic/            # DB 마이그레이션
│   ├── app/
│   │   ├── api/            # API 엔드포인트
│   │   ├── core/           # 핵심 설정
│   │   ├── db/             # 데이터베이스
│   │   ├── models/         # SQLAlchemy 모델
│   │   ├── schemas/        # Pydantic 스키마
│   │   ├── services/       # 비즈니스 로직
│   │   └── main.py         # FastAPI 앱
│   ├── requirements.txt
│   └── .env
├── frontend/                # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/            # App Router
│   │   ├── components/     # React 컴포넌트
│   │   ├── hooks/          # Custom Hooks
│   │   ├── lib/            # 유틸리티
│   │   ├── stores/         # 상태 관리
│   │   └── types/          # TypeScript 타입
│   ├── package.json
│   └── .env.local
├── CLAUDE.md                # Claude Code 가이드
└── README.md
```

## 개발 가이드

자세한 개발 가이드는 [CLAUDE.md](./CLAUDE.md) 파일을 참조하세요.

주요 내용:
- 사용 가능한 Agents 목록
- 사용 가능한 Skills 목록
- API 엔드포인트 문서
- 코딩 규칙 및 컨벤션
- 환경 변수 설정
- 보안 가이드

## 라이선스

MIT
