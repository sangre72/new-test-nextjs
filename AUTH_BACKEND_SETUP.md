# FastAPI 인증 백엔드 API 가이드

FastAPI + PostgreSQL 기반 인증 시스템 구현 완료

## 목차

1. [개요](#개요)
2. [기술 스택](#기술-스택)
3. [보안 원칙](#보안-원칙)
4. [API 엔드포인트](#api-엔드포인트)
5. [설치 및 설정](#설치-및-설정)
6. [사용 예시](#사용-예시)
7. [소셜 로그인 설정](#소셜-로그인-설정)

---

## 개요

이 프로젝트는 다음 인증 기능을 제공합니다:

- ✅ **회원가입** (이메일/비밀번호)
- ✅ **로그인** (JWT Access Token + Refresh Token)
- ✅ **로그아웃** (클라이언트 토큰 삭제)
- ✅ **토큰 갱신** (Refresh Token으로 새 Access Token 발급)
- ✅ **현재 사용자 정보 조회**
- ✅ **프로필 업데이트**
- ✅ **비밀번호 변경**
- 🔧 **소셜 로그인** (카카오, 네이버, 구글) - 설정만 완료

---

## 기술 스택

### Backend
- **FastAPI 0.128.0**: 최신 Python 웹 프레임워크
- **SQLAlchemy 2.0+**: ORM
- **Alembic**: 데이터베이스 마이그레이션
- **PostgreSQL 15+**: 데이터베이스

### 인증 라이브러리
- **python-jose[cryptography]**: JWT 토큰 생성/검증
- **passlib[bcrypt]**: 비밀번호 해싱 (bcrypt)
- **pydantic**: 요청/응답 검증
- **email-validator**: 이메일 형식 검증

---

## 보안 원칙 (Security First)

### 1. 비밀번호 보안

#### ✅ bcrypt 해싱 사용
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 비밀번호 해싱
hashed = pwd_context.hash("user_password")

# 비밀번호 검증
is_valid = pwd_context.verify("user_password", hashed)
```

#### ✅ 비밀번호 복잡도 검증
- 최소 8자 이상
- 대문자, 소문자, 숫자 각 1개 이상 포함

#### ❌ 절대 금지
```python
# ❌ 평문 비밀번호 저장
user.password = request.password  # NEVER DO THIS

# ❌ 비밀번호 로깅
print(f"Password: {password}")  # NEVER DO THIS

# ❌ GET 요청으로 비밀번호 전송
@app.get("/login?password={pwd}")  # NEVER DO THIS
```

### 2. JWT 토큰 보안

#### ✅ Access Token + Refresh Token 패턴
- **Access Token**: 30분 (짧은 수명)
- **Refresh Token**: 7일 (긴 수명)

#### ✅ Token Payload 구조
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "tenant_id": 1,
  "is_superuser": false,
  "exp": 1234567890,
  "iat": 1234567890,
  "type": "access"
}
```

#### ✅ Token Type 검증
```python
if not validate_token_type(payload, "access"):
    raise HTTPException(401, "Invalid token type")
```

### 3. SQL Injection 방지

#### ✅ SQLAlchemy ORM 사용 (Parameterized Queries)
```python
# ✅ 안전 - ORM 사용
user = db.query(User).filter(User.email == email).first()

# ❌ 위험 - 문자열 연결
query = f"SELECT * FROM users WHERE email = '{email}'"  # NEVER
```

### 4. 입력 검증

#### ✅ Pydantic 모델 사용
```python
class UserRegisterRequest(BaseModel):
    email: EmailStr  # 이메일 형식 자동 검증
    password: str = Field(..., min_length=8, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)

    @validator("password")
    def validate_password(cls, v: str) -> str:
        # 비밀번호 복잡도 검증
        if not re.search(r"[A-Z]", v):
            raise ValueError("Must contain uppercase")
        return v
```

---

## API 엔드포인트

### Base URL
```
http://localhost:8000/api/v1
```

### 1. 회원가입

#### `POST /auth/register`

**Request Body:**
```json
{
  "tenant_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "phone": "010-1234-5678"
}
```

**Response (201):**
```json
{
  "id": 123,
  "tenant_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "phone": "010-1234-5678",
  "status": "active",
  "is_superuser": false,
  "is_email_verified": false,
  "created_at": "2024-01-03T10:00:00Z",
  "updated_at": "2024-01-03T10:00:00Z"
}
```

**Error Responses:**
- `400`: Email already registered
- `400`: Username already taken
- `404`: Tenant not found
- `422`: Validation error (weak password, invalid email, etc.)

---

### 2. 로그인

#### `POST /auth/login`

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!",
  "tenant_id": 1
}
```

**Response (200):**
```json
{
  "user": {
    "id": 123,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "status": "active",
    "is_superuser": false,
    "last_login_at": "2024-01-03T10:30:00Z"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

**Error Responses:**
- `401`: Incorrect email or password
- `403`: User account is suspended/inactive

---

### 3. 토큰 갱신

#### `POST /auth/refresh`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### 4. 현재 사용자 정보 조회

#### `GET /auth/me`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "id": 123,
  "tenant_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "phone": "010-1234-5678",
  "profile_image_url": null,
  "bio": null,
  "status": "active",
  "is_superuser": false,
  "is_email_verified": true,
  "last_login_at": "2024-01-03T10:30:00Z"
}
```

**Error Responses:**
- `401`: Not authenticated
- `401`: Invalid token
- `403`: User account is inactive

---

### 5. 프로필 업데이트

#### `PUT /auth/profile`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "full_name": "John Doe Updated",
  "phone": "010-9876-5432",
  "bio": "Software Engineer",
  "profile_image_url": "https://example.com/profile.jpg"
}
```

**Response (200):**
```json
{
  "id": 123,
  "full_name": "John Doe Updated",
  "phone": "010-9876-5432",
  "bio": "Software Engineer",
  "profile_image_url": "https://example.com/profile.jpg",
  "updated_at": "2024-01-03T11:00:00Z"
}
```

---

### 6. 비밀번호 변경

#### `PUT /auth/password`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewSecurePass456!"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully",
  "detail": "Please login again with the new password"
}
```

**Error Responses:**
- `400`: Current password is incorrect
- `400`: New password must be different from current password
- `422`: New password does not meet requirements

---

### 7. 로그아웃

#### `POST /auth/logout`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "message": "Logout successful",
  "detail": "Please remove the token from client storage"
}
```

**Note:** JWT는 stateless이므로 서버에서 토큰을 무효화할 수 없습니다. 클라이언트에서 토큰을 삭제해야 합니다.

---

## 설치 및 설정

### 1. 환경 변수 설정

`.env` 파일 생성 (`.env.example` 참고):

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/myapp

# Security (IMPORTANT: Change these!)
SECRET_KEY=your-super-secret-key-please-change-this-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Environment
ENVIRONMENT=development
```

**🔴 중요: SECRET_KEY는 반드시 변경하세요!**

```bash
# 안전한 SECRET_KEY 생성
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. 데이터베이스 초기화

```bash
cd backend

# 데이터베이스 생성 (PostgreSQL)
createdb myapp

# 마이그레이션 실행
alembic upgrade head

# 또는 초기 데이터 생성 스크립트 실행
python -m app.db.init_seed
```

### 3. 서버 실행

```bash
# 개발 모드 (Hot Reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 모드
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. API 문서 확인

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 사용 예시

### Python (httpx)

```python
import httpx

# 1. 회원가입
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/auth/register",
        json={
            "tenant_id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "password": "SecurePass123!",
            "full_name": "John Doe"
        }
    )
    print(response.json())

# 2. 로그인
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/auth/login",
        json={
            "email": "john@example.com",
            "password": "SecurePass123!"
        }
    )
    data = response.json()
    access_token = data["tokens"]["access_token"]

# 3. 인증 필요한 API 호출
async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://localhost:8000/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(response.json())
```

### JavaScript (Fetch API)

```javascript
// 1. 회원가입
const registerResponse = await fetch('http://localhost:8000/api/v1/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tenant_id: 1,
    username: 'john_doe',
    email: 'john@example.com',
    password: 'SecurePass123!',
    full_name: 'John Doe'
  })
});
const user = await registerResponse.json();

// 2. 로그인
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'john@example.com',
    password: 'SecurePass123!'
  })
});
const loginData = await loginResponse.json();
const accessToken = loginData.tokens.access_token;

// 로컬 스토리지에 토큰 저장
localStorage.setItem('access_token', accessToken);
localStorage.setItem('refresh_token', loginData.tokens.refresh_token);

// 3. 인증 필요한 API 호출
const meResponse = await fetch('http://localhost:8000/api/v1/auth/me', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
const currentUser = await meResponse.json();

// 4. 토큰 갱신
const refreshResponse = await fetch('http://localhost:8000/api/v1/auth/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    refresh_token: localStorage.getItem('refresh_token')
  })
});
const newTokens = await refreshResponse.json();
localStorage.setItem('access_token', newTokens.access_token);
```

### curl

```bash
# 1. 회원가입
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'

# 2. 로그인
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'

# 3. 현재 사용자 정보 (토큰 필요)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4. 비밀번호 변경
curl -X PUT http://localhost:8000/api/v1/auth/password \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPass123!",
    "new_password": "NewSecurePass456!"
  }'
```

---

## 소셜 로그인 설정

### 지원 플랫폼
- 카카오 (Kakao)
- 네이버 (Naver)
- 구글 (Google)

### 설정 방법

#### 1. OAuth 앱 등록

**카카오:**
1. https://developers.kakao.com/ 접속
2. 내 애플리케이션 > 애플리케이션 추가
3. REST API 키 확인
4. 플랫폼 설정 > Web > Redirect URI 추가: `http://localhost:8000/api/v1/auth/oauth/kakao/callback`
5. 동의 항목 > 이메일, 프로필 정보 설정

**네이버:**
1. https://developers.naver.com/apps/ 접속
2. 애플리케이션 등록
3. Client ID, Client Secret 확인
4. Callback URL 추가: `http://localhost:8000/api/v1/auth/oauth/naver/callback`
5. 제공 정보 선택: 이메일, 프로필 정보

**구글:**
1. https://console.cloud.google.com/ 접속
2. API 및 서비스 > OAuth 동의 화면 구성
3. 사용자 인증 정보 > OAuth 2.0 클라이언트 ID 만들기
4. 승인된 리디렉션 URI: `http://localhost:8000/api/v1/auth/oauth/google/callback`

#### 2. 환경 변수 설정

`.env` 파일에 추가:

```bash
# Kakao
KAKAO_CLIENT_ID=your_kakao_rest_api_key
KAKAO_CLIENT_SECRET=your_kakao_client_secret

# Naver
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret

# Google
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

#### 3. 구현 필요 사항

현재 소셜 로그인은 **설정만 완료**되었습니다. 실제 구현을 위해서는:

1. `app/core/social_auth.py` 파일의 구현 가이드 참고
2. OAuth callback 엔드포인트 구현
3. 소셜 계정 테이블 추가 (선택)

자세한 내용은 `backend/app/core/social_auth.py` 파일을 참고하세요.

---

## 디렉토리 구조

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                    # 인증 의존성 (get_current_user 등)
│   │   └── v1/
│   │       ├── __init__.py            # 라우터 통합
│   │       └── endpoints/
│   │           └── auth.py            # 인증 API 엔드포인트
│   ├── core/
│   │   ├── config.py                  # 설정
│   │   ├── security.py                # JWT, 비밀번호 해싱
│   │   └── social_auth.py             # 소셜 로그인 설정
│   ├── models/
│   │   └── shared.py                  # User 모델 (이미 존재)
│   ├── schemas/
│   │   └── auth.py                    # 인증 Pydantic 스키마
│   └── db/
│       ├── session.py                 # DB 세션
│       └── init_seed.py               # 초기 데이터 생성
├── requirements.txt                   # Python 패키지
├── .env.example                       # 환경 변수 예시
└── main.py                            # FastAPI 앱 엔트리포인트
```

---

## 보안 체크리스트

- [x] 비밀번호는 bcrypt로 해싱
- [x] JWT 토큰에 민감 정보 미포함 (비밀번호 등)
- [x] Access Token 짧은 수명 (30분)
- [x] Refresh Token으로 갱신
- [x] SQL Injection 방지 (ORM 사용)
- [x] 입력 검증 (Pydantic)
- [x] HTTPS 사용 (프로덕션 필수)
- [x] SECRET_KEY 환경 변수로 관리
- [x] CORS 설정
- [ ] Rate Limiting (향후 추가 권장)
- [ ] 이메일 인증 (향후 추가 권장)
- [ ] 2FA (향후 추가 권장)

---

## 다음 단계

### 추천 개선 사항

1. **이메일 인증**
   - SMTP 설정 후 이메일 발송
   - 인증 토큰 생성 및 검증

2. **비밀번호 재설정**
   - 이메일로 재설정 링크 발송
   - 토큰 기반 비밀번호 재설정

3. **Rate Limiting**
   - slowapi 또는 Redis 사용
   - 로그인 시도 제한 (Brute Force 방지)

4. **소셜 로그인 완성**
   - OAuth callback 구현
   - 소셜 계정 연동 테이블 추가

5. **토큰 블랙리스트**
   - Redis 사용
   - 로그아웃 시 토큰 무효화

6. **감사 로그**
   - 로그인 이력 테이블
   - IP 주소, User Agent 기록

---

## 문제 해결

### 1. JWT 토큰 오류

```
JWTError: Signature has expired
```

**해결:**
- Access Token 갱신 필요
- `/auth/refresh` 엔드포인트로 새 토큰 발급

### 2. 비밀번호 검증 실패

```
ValueError: Password must contain at least one uppercase letter
```

**해결:**
- 비밀번호는 8자 이상, 대문자+소문자+숫자 포함 필요

### 3. Tenant not found

```
404: Tenant not found or is inactive
```

**해결:**
- 유효한 tenant_id 확인
- 데이터베이스에 Tenant 생성:

```sql
INSERT INTO tenants (tenant_code, tenant_name, status, created_by)
VALUES ('default', 'Default Tenant', 'active', 'system');
```

---

## 참고 자료

- FastAPI 공식 문서: https://fastapi.tiangolo.com/
- JWT 공식 사이트: https://jwt.io/
- OWASP 인증 가이드: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- Passlib 문서: https://passlib.readthedocs.io/

---

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
