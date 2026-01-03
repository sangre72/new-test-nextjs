# 인증 프론트엔드 컴포넌트

FastAPI + Next.js 프로젝트에 인증 프론트엔드 컴포넌트가 추가되었습니다.

## 생성된 파일

### 1. 타입 정의
- `/frontend/src/types/auth.ts` - 인증 관련 TypeScript 타입

### 2. API Client
- `/frontend/src/lib/api/auth.ts` - 인증 API 호출 함수
  - login, register, logout, getCurrentUser, changePassword, refreshToken

### 3. Context & Provider
- `/frontend/src/contexts/AuthContext.tsx` - 전역 인증 상태 관리
  - useAuth hook 제공

### 4. 페이지
- `/frontend/src/app/login/page.tsx` - 로그인 페이지
- `/frontend/src/app/register/page.tsx` - 회원가입 페이지
- `/frontend/src/app/change-password/page.tsx` - 비밀번호 변경 페이지

### 5. 컴포넌트
- `/frontend/src/components/auth/ProtectedRoute.tsx` - 인증 보호 라우트
- `/frontend/src/components/auth/AuthButtons.tsx` - 로그인/로그아웃 버튼
- `/frontend/src/components/auth/index.ts` - Export 파일

### 6. 업데이트된 파일
- `/frontend/src/app/providers.tsx` - AuthProvider 추가
- `/frontend/src/lib/api.ts` - sessionStorage 사용으로 변경
- `/frontend/src/app/page.tsx` - 홈페이지에 UserMenu 추가

---

## 주요 기능

### 1. Security First 원칙
- **토큰 저장**: sessionStorage 사용 (탭 닫으면 자동 삭제)
- **비밀번호 필드**: type="password", 표시/숨기기 토글
- **에러 처리**: 모든 API 호출에 try-catch, 상세 에러 메시지
- **입력 검증**: 실시간 검증 + 제출 시 검증

### 2. 폼 검증
- 이메일: 형식 검증
- 비밀번호: 8자 이상, 대소문자/숫자 포함
- 비밀번호 확인: 일치 확인
- 실시간 에러 표시

### 3. UX
- 로딩 상태 표시
- 에러/성공 메시지
- 비밀번호 표시/숨기기
- Tailwind CSS 스타일링

---

## 사용 방법

### 1. 기본 사용

```tsx
// 로그인 상태 확인
import { useAuth } from '@/contexts/AuthContext'

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth()

  if (isAuthenticated) {
    return <div>환영합니다, {user?.name}님!</div>
  }

  return <button onClick={() => login(email, password)}>로그인</button>
}
```

### 2. Protected Route

```tsx
import { ProtectedRoute } from '@/components/auth'

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div>인증된 사용자만 볼 수 있는 페이지</div>
    </ProtectedRoute>
  )
}
```

### 3. 인증 버튼

```tsx
import { AuthButtons, UserMenu } from '@/components/auth'

// 간단한 버튼
<AuthButtons />

// 드롭다운 메뉴
<UserMenu />
```

---

## API 엔드포인트 (백엔드 필요)

다음 FastAPI 엔드포인트가 필요합니다:

```python
POST   /api/v1/auth/login       # 로그인
POST   /api/v1/auth/register    # 회원가입
POST   /api/v1/auth/logout      # 로그아웃
GET    /api/v1/auth/me          # 현재 사용자 정보
PUT    /api/v1/auth/password    # 비밀번호 변경
POST   /api/v1/auth/refresh     # 토큰 갱신
```

### 요청/응답 형식

**로그인 (POST /api/v1/auth/login)**
```typescript
// 요청 (Form Data)
username: string  // 이메일
password: string

// 응답
{
  access_token: string
  token_type: "bearer"
  user: {
    id: number
    email: string
    name: string
    role?: string
  }
}
```

**회원가입 (POST /api/v1/auth/register)**
```typescript
// 요청
{
  email: string
  password: string
  name: string
  phone?: string
}

// 응답
{
  id: number
  email: string
  name: string
  message: string
}
```

**현재 사용자 (GET /api/v1/auth/me)**
```typescript
// 응답
{
  id: number
  email: string
  name: string
  role?: string
}
```

**비밀번호 변경 (PUT /api/v1/auth/password)**
```typescript
// 요청
{
  current_password: string
  new_password: string
}

// 응답
{
  message: string
}
```

---

## 환경 변수

`.env.local` 파일에 추가:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 보안 체크리스트

- [x] sessionStorage 사용 (XSS 대비)
- [x] 비밀번호 필드 type="password"
- [x] 401 에러 시 자동 로그아웃
- [x] 폼 제출 후 비밀번호 초기화
- [x] HTTPS 사용 권장 (프로덕션)
- [x] CORS 설정 (백엔드)

---

## 다음 단계

1. **백엔드 인증 API 구현**
   - FastAPI OAuth2 with Password Flow
   - JWT 토큰 생성/검증
   - 비밀번호 해싱 (bcrypt)

2. **추가 기능**
   - 이메일 인증
   - 비밀번호 찾기/재설정
   - 소셜 로그인 (Google, GitHub)
   - 2FA (Two-Factor Authentication)

3. **테스트**
   - 단위 테스트 (Jest, React Testing Library)
   - E2E 테스트 (Playwright)

---

## 문제 해결

### 1. 토큰이 저장되지 않음
- 브라우저 개발자 도구 > Application > Session Storage 확인
- CORS 설정 확인 (withCredentials: true)

### 2. 401 에러 발생
- 토큰 만료 확인
- 백엔드 JWT 검증 로직 확인
- Authorization 헤더 형식: `Bearer <token>`

### 3. 페이지 새로고침 시 로그아웃됨
- sessionStorage 사용 중이므로 정상 동작
- 지속성 필요 시 localStorage 또는 httpOnly Cookie 사용

---

## 라이센스

MIT
