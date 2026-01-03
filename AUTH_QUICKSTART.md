# 인증 시스템 빠른 시작 가이드

## 1분 요약

인증 프론트엔드 컴포넌트가 생성되었습니다. 이제 백엔드 API만 연결하면 됩니다!

---

## 생성된 페이지

1. **로그인 페이지**: http://localhost:3000/login
2. **회원가입 페이지**: http://localhost:3000/register
3. **비밀번호 변경 페이지**: http://localhost:3000/change-password

---

## 빠른 시작

### 1. 프론트엔드 실행

```bash
cd frontend
npm run dev
```

브라우저에서 http://localhost:3000 접속

### 2. 백엔드 API 필요

다음 엔드포인트를 FastAPI에 구현해야 합니다:

```
POST   /api/v1/auth/login       # 로그인
POST   /api/v1/auth/register    # 회원가입
POST   /api/v1/auth/logout      # 로그아웃
GET    /api/v1/auth/me          # 현재 사용자 정보
PUT    /api/v1/auth/password    # 비밀번호 변경
```

---

## 사용 예시

### 1. 로그인 상태 확인

```tsx
import { useAuth } from '@/contexts/AuthContext'

function MyComponent() {
  const { user, isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return <div>로그인이 필요합니다</div>
  }

  return <div>안녕하세요, {user?.name}님!</div>
}
```

### 2. Protected Route (인증 필요 페이지)

```tsx
import { ProtectedRoute } from '@/components/auth'

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div>인증된 사용자만 접근 가능</div>
    </ProtectedRoute>
  )
}
```

### 3. 네비게이션에 로그인/로그아웃 버튼 추가

```tsx
import { UserMenu } from '@/components/auth'

function Navbar() {
  return (
    <nav className="bg-white shadow">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold">MyApp</h1>
          <UserMenu />  {/* 로그인/로그아웃 버튼 */}
        </div>
      </div>
    </nav>
  )
}
```

---

## 디렉토리 구조

```
frontend/src/
├── types/
│   └── auth.ts                    # 인증 타입 정의
├── lib/
│   ├── api.ts                     # API 클라이언트 (업데이트됨)
│   └── api/
│       └── auth.ts                # 인증 API 함수
├── contexts/
│   └── AuthContext.tsx            # 인증 Context & Provider
├── components/
│   └── auth/
│       ├── ProtectedRoute.tsx     # 보호된 라우트
│       ├── AuthButtons.tsx        # 로그인/로그아웃 버튼
│       └── index.ts               # Export
└── app/
    ├── providers.tsx              # AuthProvider 추가됨
    ├── login/
    │   └── page.tsx               # 로그인 페이지
    ├── register/
    │   └── page.tsx               # 회원가입 페이지
    └── change-password/
        └── page.tsx               # 비밀번호 변경 페이지
```

---

## 주요 기능

### Security First
- ✅ sessionStorage 사용 (XSS 방지)
- ✅ 비밀번호 표시/숨기기
- ✅ 폼 검증 (이메일, 비밀번호 강도)
- ✅ 401 에러 시 자동 로그아웃
- ✅ 에러 처리

### UX
- ✅ 로딩 상태 표시
- ✅ 에러/성공 메시지
- ✅ 실시간 폼 검증
- ✅ Tailwind CSS 스타일링
- ✅ 반응형 디자인

---

## 다음 단계

1. **백엔드 인증 API 구현**
   ```bash
   # FastAPI 인증 에이전트 사용 (예정)
   Use auth-backend --init
   ```

2. **페이지 테스트**
   - http://localhost:3000/login
   - http://localhost:3000/register
   - http://localhost:3000/change-password

3. **커스터마이징**
   - 스타일 변경 (Tailwind CSS)
   - 폼 검증 규칙 수정
   - 에러 메시지 커스터마이징

---

## 문제 해결

### Q: 로그인 후 페이지 새로고침 시 로그아웃됨
A: sessionStorage 사용 중이므로 정상입니다. 지속성 필요 시 localStorage 또는 httpOnly Cookie 사용 검토.

### Q: CORS 에러 발생
A: 백엔드에서 CORS 설정 필요:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q: 401 에러 발생
A: 백엔드 JWT 토큰 검증 확인, Authorization 헤더 형식: `Bearer <token>`

---

## 참고 문서

- 상세 문서: `AUTH_FRONTEND_README.md`
- 프로젝트 설정: `CLAUDE.md`
- API 문서: http://localhost:8000/docs

---

## 라이센스

MIT
