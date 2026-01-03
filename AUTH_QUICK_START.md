# 인증 시스템 빠른 시작 가이드

5분 안에 인증 API를 시작하세요!

## 1단계: 환경 변수 설정 (30초)

```bash
cd backend
cp .env.example .env
```

`.env` 파일을 열고 **SECRET_KEY만** 변경:

```bash
# 안전한 SECRET_KEY 생성
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

생성된 키를 `.env`에 붙여넣기:

```bash
SECRET_KEY=생성된_키를_여기에_붙여넣기
```

---

## 2단계: 데이터베이스 설정 (1분)

### Option A: Docker 사용 (권장)

```bash
# 프로젝트 루트에서
docker-compose up -d db

# 마이그레이션 실행
cd backend
alembic upgrade head
```

### Option B: 로컬 PostgreSQL 사용

```bash
# PostgreSQL이 설치되어 있다면
createdb myapp

# 마이그레이션 실행
cd backend
alembic upgrade head
```

---

## 3단계: 서버 실행 (10초)

```bash
cd backend
uvicorn app.main:app --reload
```

서버가 실행되면:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 4단계: API 테스트 (3분)

### 브라우저에서 테스트

1. http://localhost:8000/docs 접속
2. **POST /api/v1/auth/register** 클릭
3. "Try it out" 클릭
4. 아래 데이터 입력:

```json
{
  "tenant_id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "password": "TestPass123!",
  "full_name": "Test User"
}
```

5. "Execute" 클릭

### curl로 테스트

```bash
# 1. 회원가입
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'

# 2. 로그인
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# 3. 토큰 복사 후 현재 사용자 정보 조회
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 5단계: Frontend 연동 (선택)

### React/Next.js 예시

```javascript
// lib/auth.js
export async function register(userData) {
  const response = await fetch('http://localhost:8000/api/v1/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData)
  });
  return response.json();
}

export async function login(email, password) {
  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();

  // 토큰 저장
  if (data.tokens) {
    localStorage.setItem('access_token', data.tokens.access_token);
    localStorage.setItem('refresh_token', data.tokens.refresh_token);
  }

  return data;
}

export async function getCurrentUser() {
  const token = localStorage.getItem('access_token');
  const response = await fetch('http://localhost:8000/api/v1/auth/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

export function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}
```

### 사용 예시

```javascript
// pages/register.js
import { register } from '@/lib/auth';

async function handleRegister(e) {
  e.preventDefault();

  const user = await register({
    tenant_id: 1,
    username: 'john_doe',
    email: 'john@example.com',
    password: 'SecurePass123!',
    full_name: 'John Doe'
  });

  console.log('User created:', user);
}
```

---

## 완료!

이제 다음 기능을 사용할 수 있습니다:

- ✅ 회원가입: `POST /api/v1/auth/register`
- ✅ 로그인: `POST /api/v1/auth/login`
- ✅ 토큰 갱신: `POST /api/v1/auth/refresh`
- ✅ 현재 사용자 조회: `GET /api/v1/auth/me`
- ✅ 프로필 업데이트: `PUT /api/v1/auth/profile`
- ✅ 비밀번호 변경: `PUT /api/v1/auth/password`
- ✅ 로그아웃: `POST /api/v1/auth/logout`

---

## 문제 해결

### Tenant not found 오류

첫 번째 테넌트를 생성하세요:

```bash
# PostgreSQL 접속
psql myapp

# 테넌트 생성
INSERT INTO tenants (tenant_code, tenant_name, status, created_by, is_active)
VALUES ('default', 'Default Tenant', 'active', 'system', true);
```

또는 Python으로:

```python
# backend/create_tenant.py
from app.db.session import SessionLocal
from app.models.shared import Tenant

db = SessionLocal()
tenant = Tenant(
    tenant_code="default",
    tenant_name="Default Tenant",
    status="active",
    created_by="system"
)
db.add(tenant)
db.commit()
print(f"Tenant created with ID: {tenant.id}")
```

```bash
python create_tenant.py
```

---

## 다음 단계

- 상세 문서: [AUTH_BACKEND_SETUP.md](./AUTH_BACKEND_SETUP.md)
- 소셜 로그인 설정: [AUTH_BACKEND_SETUP.md#소셜-로그인-설정](./AUTH_BACKEND_SETUP.md#소셜-로그인-설정)
- API 문서: http://localhost:8000/docs
