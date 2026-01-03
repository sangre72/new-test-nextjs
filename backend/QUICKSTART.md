# 메뉴 관리 API 빠른 시작 가이드

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
cd backend

# Python 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (데이터베이스 URL 등)
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### 3. 데이터베이스 마이그레이션

```bash
# 마이그레이션 실행
alembic upgrade head

# 또는 특정 리비전만
alembic upgrade 003_update_menus_table
```

### 4. 샘플 데이터 생성

```bash
# 샘플 메뉴 데이터 생성
python scripts/seed_menus.py
```

출력 예시:
```
🌲 Creating sample menus for tenant 1...

📱 User Menus:
  ✓ Created: Home (ID: 1, Type: user)
  ✓ Created: Products (ID: 2, Type: user)
    ✓ Created: All Products (ID: 3, Type: user)
    ✓ Created: New Arrivals (ID: 4, Type: user)
    ✓ Created: Sale (ID: 5, Type: user)
  ...

📊 Summary
============================================================
User Menus:  10
Admin Menus: 13
Site Menus:  3
Total:       26
============================================================
```

### 5. 서버 실행

```bash
# 개발 서버 (자동 리로드)
uvicorn app.main:app --reload

# 또는 포트 지정
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

서버가 실행되면:
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/v1/health

---

## 📝 기본 사용법

### 1. 인증 토큰 얻기

```bash
# 로그인 (샘플 데이터 생성 시 만들어진 admin 계정)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

응답:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

토큰을 환경 변수로 저장:
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 2. 메뉴 조회

#### 공개 메뉴 트리 (인증 불필요)

```bash
curl http://localhost:8000/api/v1/menus/public/tree?menu_type=user
```

#### 전체 메뉴 리스트 (관리자용)

```bash
curl http://localhost:8000/api/v1/menus \
  -H "Authorization: Bearer $TOKEN"
```

#### 메뉴 트리 (관리자용)

```bash
curl http://localhost:8000/api/v1/menus/tree?menu_type=admin \
  -H "Authorization: Bearer $TOKEN"
```

### 3. 메뉴 생성

```bash
curl -X POST http://localhost:8000/api/v1/menus \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "menu_name": "새 메뉴",
    "menu_code": "new-menu",
    "menu_type": "user",
    "menu_url": "/new-menu",
    "menu_icon": "fa-star",
    "display_order": 10,
    "permission_type": "public",
    "is_visible": true,
    "is_active": true
  }'
```

### 4. 메뉴 수정

```bash
curl -X PUT http://localhost:8000/api/v1/menus/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "menu_name": "수정된 메뉴"
  }'
```

### 5. 메뉴 삭제

```bash
curl -X DELETE http://localhost:8000/api/v1/menus/1 \
  -H "Authorization: Bearer $TOKEN"
```

### 6. 메뉴 순서 변경

```bash
curl -X PUT http://localhost:8000/api/v1/menus/reorder \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"menu_id": 1, "new_order": 0},
      {"menu_id": 2, "new_order": 1},
      {"menu_id": 3, "new_order": 2}
    ]
  }'
```

---

## 🧪 테스트 실행

```bash
# 전체 테스트
pytest

# 메뉴 API 테스트만
pytest tests/test_menu_api.py -v

# 커버리지 포함
pytest --cov=app tests/
```

---

## 📚 API 엔드포인트 목록

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/menus/public/tree` | 공개 메뉴 트리 조회 |

### Admin Endpoints (인증 필요)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/menus` | 메뉴 리스트 (페이지네이션) |
| GET | `/api/v1/menus/tree` | 메뉴 트리 (전체) |
| GET | `/api/v1/menus/{id}` | 메뉴 단건 조회 |
| POST | `/api/v1/menus` | 메뉴 생성 |
| PUT | `/api/v1/menus/{id}` | 메뉴 수정 |
| DELETE | `/api/v1/menus/{id}` | 메뉴 삭제 |
| POST | `/api/v1/menus/bulk-delete` | 벌크 삭제 |
| PUT | `/api/v1/menus/reorder` | 순서 변경 |
| PUT | `/api/v1/menus/{id}/move` | 메뉴 이동 |

---

## 🔍 문제 해결

### 마이그레이션 오류

```bash
# 현재 리비전 확인
alembic current

# 리비전 히스토리 확인
alembic history

# 특정 리비전으로 다운그레이드
alembic downgrade 002

# 다시 업그레이드
alembic upgrade 003
```

### 데이터베이스 연결 오류

1. PostgreSQL이 실행 중인지 확인
2. .env 파일의 DATABASE_URL 확인
3. 데이터베이스와 유저가 생성되었는지 확인

```bash
# PostgreSQL 접속 테스트
psql -h localhost -U your_user -d your_db
```

### 패키지 설치 오류

```bash
# pip 업그레이드
pip install --upgrade pip

# 캐시 삭제 후 재설치
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

---

## 📖 추가 문서

- [전체 API 가이드](./MENU_API_GUIDE.md) - 상세한 API 문서
- [FastAPI 자동 문서](http://localhost:8000/docs) - 서버 실행 후 접속
- [ReDoc](http://localhost:8000/redoc) - 대체 API 문서

---

## 🎯 다음 단계

1. ✅ 샘플 데이터 생성 완료
2. 🔨 프론트엔드 연동
3. 🎨 메뉴 편집기 UI 개발
4. 🔐 권한 기반 메뉴 필터링 구현
5. 📊 메뉴 사용 통계 추가

---

**작성일**: 2026-01-03
**버전**: 1.0.0
