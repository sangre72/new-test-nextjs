# New Test Project - Claude Code 가이드

## 프로젝트 정보

- **기술 스택**: FastAPI + Next.js 15 + TypeScript + PostgreSQL
- **생성일**: 2026-01-03
- **인증 방식**: 휴대폰 인증 (OTP) + 소셜 로그인
- **데이터베이스**: PostgreSQL + Redis

---

## 개발 원칙

### Security First (보안 우선)
- 모든 사용자 입력 검증 (SQL Injection, XSS 방지)
- Parameterized Query 필수 (SQLAlchemy ORM 사용)
- 비밀번호는 bcrypt로 해싱 (passlib 사용)
- JWT는 python-jose[cryptography] 사용
- API 키는 환경변수로 관리 (.env)
- httpOnly 쿠키로 토큰 저장 (XSS 방지)
- 인증번호는 개발모드에서 000000 고정 허용

### Error Handling First (오류 처리 우선)
- 모든 외부 호출에 try-except
- 적절한 에러 응답 (error_code, message)
- 로깅 (민감 정보 제외)
- 프로덕션에서 스택 트레이스 노출 금지

### API 응답 표준 형식
```typescript
// 성공 응답
{
  "success": true,
  "data": { ... }
}

// 실패 응답
{
  "success": false,
  "error_code": "INVALID_INPUT",
  "message": "이메일 형식이 올바르지 않습니다."
}
```

| Error Code | HTTP Status | 설명 |
|------------|-------------|------|
| `DATABASE_UNAVAILABLE` | 503 | DB 연결 실패 |
| `ACCESS_DENIED` | 403 | 권한 없음 |
| `INVALID_INPUT` | 400 | 입력값 검증 실패 |
| `NOT_FOUND` | 404 | 리소스 없음 |
| `INVALID_CREDENTIALS` | 401 | 인증 실패 |
| `INTERNAL_ERROR` | 500 | 서버 내부 오류 |

---

## 사용 가능한 Skills

### Git 관련
| 스킬 | 설명 | 사용법 |
|------|------|--------|
| `gitpush` | 자동 커밋 + push | `/gitpush` |
| `gitpull` | dev merge + pull | `/gitpull` |

### 코드 품질
| 스킬 | 설명 | 사용법 |
|------|------|--------|
| `coding-guide` | 코드 품질, 보안 규칙 | 자동 적용 |
| `refactor` | 모듈화/타입 리팩토링 | `/refactor` `/refactor --fix` |
| `modular-check` | 모듈화 상태 분석 | `/modular-check` |

---

## 사용 가능한 Agents

### 최우선 (순서대로 실행)

| 순서 | 에이전트 | 설명 | 사용법 |
|------|----------|------|--------|
| 1 | `shared-schema` | 공유 테이블 초기화 | `Use shared-schema --init` |
| 2 | `tenant-manager` | 테넌트(멀티사이트) 관리 | `Use tenant-manager --init` |
| 3 | `category-manager` | 카테고리 관리 | `Use category-manager --init` |

### 인증

| 에이전트 | 설명 | 사용법 |
|----------|------|--------|
| `auth-backend` | 인증 Backend API | `Use auth-backend --init` |
| `auth-frontend` | 인증 Frontend UI | `Use auth-frontend --init` |

**지원 인증 방식:**
- 휴대폰 번호 인증 (OTP) - 권장
- 이메일/비밀번호 인증
- 소셜 로그인 (카카오, 네이버, 구글)

### 메뉴 관리

| 에이전트 | 설명 | 사용법 |
|----------|------|--------|
| `menu-manager` | 통합 메뉴 관리 (프로토콜 문서) | `Use menu-manager --init` |
| `menu-backend` | 메뉴 Backend API | `Use menu-backend --init` |
| `menu-frontend` | 메뉴 Frontend UI | `Use menu-frontend --init` |

**메뉴 타입**: site, user, admin, header_utility, footer_utility

### 게시판

| 에이전트 | 설명 | 사용법 |
|----------|------|--------|
| `board-generator` | 멀티게시판 오케스트레이터 | `Use board-generator --init` |
| `board-schema` | DB 스키마 정의 (공유) | 참조용 |
| `board-templates` | 템플릿 정의 (공유) | 참조용 |
| `board-frontend-pages` | 페이지 템플릿 (공유) | 참조용 |
| `board-attachments` | 파일 첨부 기능 (공유) | 참조용 |

**템플릿**: notice, free, qna, gallery, faq, review

---

## 초기화 순서

```bash
# 1. 공유 스키마 (필수 - 가장 먼저)
Use shared-schema --init

# 2. 인증 시스템 (휴대폰 인증 권장)
Use auth-backend --init --type=phone
Use auth-frontend --init

# 3. 소셜 로그인 추가 (선택)
Use auth-backend --feature=social-kakao
Use auth-backend --feature=social-naver
Use auth-backend --feature=social-google

# 4. 테넌트 관리 (멀티사이트 필요 시)
Use tenant-manager --init

# 5. 카테고리 관리 (게시판 분류 필요 시)
Use category-manager --init

# 6. 메뉴 관리
Use menu-backend --init
Use menu-frontend --init
Use menu-manager --type=site       # 사이트 메뉴 (GNB)
Use menu-manager --type=user       # 마이페이지 메뉴
Use menu-manager --utility=header  # 헤더 유틸리티

# 7. 게시판 시스템
Use board-generator --init
Use board-generator --template notice    # 공지사항
Use board-generator --template free      # 자유게시판
Use board-generator --template qna       # Q&A
```

**휴대폰 인증 흐름:**
```
1. POST /api/auth/send-code       → 인증번호 발송 (SMS)
2. POST /api/auth/verify-code     → 인증번호 확인 (verification_token 발급)
3. POST /api/auth/register        → 회원가입 (verification_token 필요)
4. POST /api/auth/login           → 로그인 (휴대폰 + 인증번호)
```

> **개발 모드**: 인증번호 `000000` 입력 시 항상 인증 통과

---

## 프로젝트 구조

### Backend (FastAPI)

```
backend/
├── alembic/                     # DB 마이그레이션
│   ├── versions/
│   └── env.py
├── app/
│   ├── api/
│   │   ├── deps.py              # 의존성 (인증, DB 세션)
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── auth.py      # 인증 API
│   │           ├── users.py     # 사용자 API
│   │           ├── menus.py     # 메뉴 API
│   │           └── boards.py    # 게시판 API
│   ├── core/
│   │   ├── config.py            # 환경 설정
│   │   └── security.py          # JWT, 비밀번호 해싱
│   ├── db/
│   │   ├── base.py              # Base 클래스, TimestampMixin
│   │   └── session.py           # DB 세션
│   ├── models/
│   │   ├── user.py              # User 모델
│   │   ├── menu.py              # Menu 모델
│   │   ├── board.py             # Board 모델
│   │   ├── post.py              # Post 모델
│   │   └── verification.py      # 인증번호 모델
│   ├── schemas/
│   │   ├── auth.py              # 인증 스키마
│   │   ├── user.py              # 사용자 스키마
│   │   ├── menu.py              # 메뉴 스키마
│   │   └── board.py             # 게시판 스키마
│   ├── services/
│   │   ├── auth.py              # 인증 서비스
│   │   ├── sms.py               # SMS 발송 서비스
│   │   └── menu.py              # 메뉴 서비스
│   └── main.py                  # FastAPI 앱
├── requirements.txt
└── .env
```

### Frontend (Next.js 15)

```
frontend/
├── src/
│   ├── app/                     # Next.js App Router
│   │   ├── (auth)/              # 인증 그룹
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   ├── mypage/              # 마이페이지
│   │   │   └── page.tsx
│   │   ├── admin/               # 관리자
│   │   │   ├── menus/           # 메뉴 관리
│   │   │   └── boards/          # 게시판 관리
│   │   ├── boards/              # 게시판 목록
│   │   │   └── [boardCode]/
│   │   │       ├── page.tsx     # 게시글 목록
│   │   │       └── [postId]/
│   │   │           └── page.tsx # 게시글 상세
│   │   └── layout.tsx
│   ├── components/
│   │   ├── auth/                # 인증 컴포넌트
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── PhoneVerification.tsx
│   │   ├── admin/
│   │   │   └── menu/            # 메뉴 관리 컴포넌트
│   │   │       ├── MenuManager.tsx
│   │   │       ├── MenuTree.tsx
│   │   │       └── MenuForm.tsx
│   │   ├── board/               # 게시판 컴포넌트
│   │   │   ├── BoardList.tsx
│   │   │   ├── PostDetail.tsx
│   │   │   ├── PostForm.tsx
│   │   │   └── CommentList.tsx
│   │   └── ui/                  # 공통 UI (shadcn/ui)
│   ├── hooks/
│   │   ├── useAuth.ts           # 인증 훅
│   │   ├── useMenu.ts           # 메뉴 훅
│   │   └── useBoard.ts          # 게시판 훅
│   ├── lib/
│   │   ├── api.ts               # API 클라이언트
│   │   └── utils.ts             # 유틸리티
│   ├── stores/
│   │   └── authStore.ts         # 인증 상태 (Zustand)
│   └── types/
│       ├── auth.ts              # 인증 타입
│       ├── user.ts              # 사용자 타입
│       ├── menu.ts              # 메뉴 타입
│       └── board.ts             # 게시판 타입
├── public/
├── package.json
└── .env.local
```

---

## 코딩 규칙

### 네이밍 컨벤션

| 구분 | 규칙 | 예시 |
|------|------|------|
| 컴포넌트/클래스 | PascalCase | `MenuManager`, `AuthHandler` |
| 변수/함수 | camelCase | `getAllMenus`, `isLoading` |
| 상수 | UPPER_SNAKE_CASE | `API_BASE_URL`, `MAX_RETRIES` |
| Boolean | is/has/should 접두사 | `isActive`, `hasPermission` |
| API 엔드포인트 | kebab-case | `/api/send-code`, `/api/user-profile` |

### 필수 감사 컬럼 (TimestampMixin)

모든 테이블에 다음 컬럼 포함:

```python
# app/db/base.py
from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy.sql import func

class TimestampMixin:
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
```

### Import 순서

1. 표준 라이브러리 (os, sys 등)
2. 외부 라이브러리 (fastapi, sqlalchemy 등)
3. 내부 패키지 (app.models, app.schemas 등)
4. 타입 import (from typing import ...)

```python
# Good
import os
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest

from typing import Optional, List
```

---

## 환경 변수 설정

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/newtest

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
JWT_EXPIRES_IN=1h
JWT_REFRESH_EXPIRES_IN=7d

# SMS (프로덕션 전용)
SMS_API_KEY=
SMS_SENDER_NUMBER=

# 소셜 로그인
KAKAO_CLIENT_ID=
KAKAO_CLIENT_SECRET=
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# 개발 모드
DEV_MODE=true
DEV_VERIFICATION_CODE=000000

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend (.env.local)

```bash
# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# 소셜 로그인
NEXT_PUBLIC_KAKAO_CLIENT_ID=
NEXT_PUBLIC_NAVER_CLIENT_ID=
NEXT_PUBLIC_GOOGLE_CLIENT_ID=

# 지도 (선택)
NEXT_PUBLIC_KAKAO_MAP_KEY=
```

---

## API 엔드포인트

### 인증 (Authentication)

| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/api/auth/send-code` | 휴대폰/이메일 인증번호 발송 | Public |
| POST | `/api/auth/verify-code` | 인증번호 확인 | Public |
| POST | `/api/auth/register` | 회원가입 | Public |
| POST | `/api/auth/login` | 로그인 (이메일/비밀번호) | Public |
| POST | `/api/auth/phone-login` | 휴대폰 인증 로그인 | Public |
| POST | `/api/auth/logout` | 로그아웃 | User |
| POST | `/api/auth/refresh` | 토큰 갱신 | User |
| GET | `/api/auth/me` | 현재 사용자 정보 | User |
| PUT | `/api/auth/profile` | 프로필 수정 | User |
| PUT | `/api/auth/password` | 비밀번호 변경 | User |
| DELETE | `/api/auth/withdraw` | 회원 탈퇴 | User |
| POST | `/api/auth/kakao` | 카카오 로그인 | Public |
| POST | `/api/auth/naver` | 네이버 로그인 | Public |
| POST | `/api/auth/google` | 구글 로그인 | Public |

### 메뉴 관리 (Menu Management)

| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/api/menus` | 사용자용 메뉴 조회 | Public |
| GET | `/api/menus/:type` | 타입별 메뉴 조회 | Public |
| GET | `/api/admin/menus` | 메뉴 목록 조회 | Admin |
| GET | `/api/admin/menus/:id` | 메뉴 상세 조회 | Admin |
| POST | `/api/admin/menus` | 메뉴 생성 | Admin |
| PUT | `/api/admin/menus/:id` | 메뉴 수정 | Admin |
| DELETE | `/api/admin/menus/:id` | 메뉴 삭제 (Soft Delete) | Admin |
| PUT | `/api/admin/menus/reorder` | 메뉴 순서 변경 | Admin |
| PUT | `/api/admin/menus/:id/move` | 메뉴 이동 (부모 변경) | Admin |

### 게시판 (Board)

| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/api/boards` | 게시판 목록 조회 | Public |
| GET | `/api/boards/:boardCode` | 게시판 상세 | Public |
| GET | `/api/boards/:boardCode/posts` | 게시글 목록 | Public |
| GET | `/api/posts/:id` | 게시글 상세 | Public |
| POST | `/api/posts` | 게시글 작성 | User |
| PUT | `/api/posts/:id` | 게시글 수정 | Owner/Admin |
| DELETE | `/api/posts/:id` | 게시글 삭제 | Owner/Admin |
| POST | `/api/posts/:id/comments` | 댓글 작성 | User |
| PUT | `/api/comments/:id` | 댓글 수정 | Owner/Admin |
| DELETE | `/api/comments/:id` | 댓글 삭제 | Owner/Admin |
| POST | `/api/posts/:id/like` | 좋아요/추천 | User |
| POST | `/api/attachments/upload` | 파일 업로드 | User |

---

## 자주 쓰는 명령

```bash
# === 프로젝트 초기화 ===
Use shared-schema --init                   # 공유 테이블 생성
Use auth-backend --init --type=phone       # 휴대폰 인증 Backend
Use auth-frontend --init                   # 인증 Frontend

# === 인증 시스템 ===
Use auth-backend --feature=social-kakao    # 카카오 소셜 로그인 추가
Use auth-backend --feature=social-naver    # 네이버 소셜 로그인 추가
Use auth-frontend --page=phone-login       # 휴대폰 로그인 페이지

# === 메뉴 관리 ===
Use menu-backend --init                    # 메뉴 Backend API
Use menu-frontend --init                   # 메뉴 Frontend UI
Use menu-manager --type=site               # 사이트 메뉴 (GNB) 생성
Use menu-manager --type=user               # 마이페이지 메뉴 생성
Use menu-manager --type=admin              # 관리자 메뉴 생성
Use menu-manager --utility=header          # 헤더 유틸리티
Use menu-manager to add menu "메뉴명"       # 메뉴 추가

# === 게시판 생성 ===
Use board-generator --init                 # 게시판 시스템 초기화
Use board-generator --template notice      # 공지사항 템플릿
Use board-generator --template free        # 자유게시판 템플릿
Use board-generator --template qna         # Q&A 템플릿
Use board-generator to create "게시판명"    # 커스텀 게시판

# === Git ===
/gitpush                                   # 커밋 + push
/gitpull                                   # dev merge + pull

# === 개발 환경 ===
/dev-setup                                 # Docker, 의존성 설치
/lint --fix                                # 린트 오류 수정
/test                                      # 테스트 실행
/db-migrate --generate "설명"              # 마이그레이션 생성
```

---

## 개발 시작하기

### 1. 의존성 설치

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. 데이터베이스 설정

```bash
# PostgreSQL 설치 (Docker 사용 권장)
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=newtest \
  -p 5432:5432 \
  postgres:15

# Redis 설치
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7

# 마이그레이션 실행
cd backend
alembic upgrade head
```

### 3. 서버 실행

```bash
# Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

### 4. 접속

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 필수 Python 패키지

```txt
# requirements.txt (backend)
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-multipart>=0.0.6
httpx>=0.26.0
redis>=5.0.0
```

---

## 다음 단계

1. **공유 스키마 초기화**
   ```bash
   Use shared-schema --init
   ```

2. **인증 시스템 구축**
   ```bash
   Use auth-backend --init --type=phone
   Use auth-frontend --init
   ```

3. **메뉴 관리 시스템 구축**
   ```bash
   Use menu-backend --init
   Use menu-frontend --init
   Use menu-manager --type=site
   ```

4. **게시판 생성**
   ```bash
   Use board-generator --init
   Use board-generator --template notice
   ```

---

## 참고 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Next.js 15 문서](https://nextjs.org/docs)
- [SQLAlchemy 2.0 문서](https://docs.sqlalchemy.org/en/20/)
- [Pydantic 문서](https://docs.pydantic.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)

---

## 에이전트 참조

이 프로젝트는 다음 에이전트들을 사용합니다:

**최우선 (순서대로):**
- `~/.claude/agents/shared-schema.md` (공유 테이블)
- `~/.claude/agents/tenant-manager.md` (테넌트/멀티사이트)
- `~/.claude/agents/category-manager.md` (카테고리 관리)

**인증:**
- `~/.claude/agents/auth-backend.md`
- `~/.claude/agents/auth-frontend.md`

**메뉴 관리:**
- `~/.claude/agents/menu-manager.md` (프로토콜 문서)
- `~/.claude/agents/menu-backend.md`
- `~/.claude/agents/menu-frontend.md`

**게시판:**
- `~/.claude/agents/board-generator.md` (오케스트레이터)
- `~/.claude/agents/board-schema.md` (DB 스키마)
- `~/.claude/agents/board-templates.md` (템플릿)
- `~/.claude/agents/board-frontend-pages.md` (페이지 템플릿)
- `~/.claude/agents/board-attachments.md` (파일 첨부)

**스킬:**
- `~/.claude/skills/coding-guide/`
- `~/.claude/skills/gitpush/`
- `~/.claude/skills/gitpull/`
- `~/.claude/skills/refactor/`
- `~/.claude/skills/modular-check/`
