# Backend - FastAPI

FastAPI 기반 백엔드 서버

## 빠른 시작

### 1. 환경 설정

```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (DATABASE_URL, SECRET_KEY 등)
nano .env
```

### 3. 데이터베이스 마이그레이션

```bash
# 마이그레이션 실행
alembic upgrade head
```

### 4. 서버 실행

```bash
# 개발 서버 실행 (자동 리로드)
uvicorn app.main:app --reload

# 또는
python -m app.main
```

서버 실행 후:
- API 문서: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 프로젝트 구조

```
backend/
├── app/
│   ├── api/              # API 엔드포인트
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   └── __init__.py
│   │   └── deps.py       # 의존성 주입
│   ├── core/             # 설정
│   │   └── config.py
│   ├── db/               # 데이터베이스
│   │   ├── session.py
│   │   └── base.py
│   ├── models/           # SQLAlchemy 모델
│   ├── schemas/          # Pydantic 스키마
│   ├── services/         # 비즈니스 로직
│   └── main.py
├── alembic/              # DB 마이그레이션
├── tests/
├── requirements.txt
└── .env.example
```

## 개발 가이드

### 새 엔드포인트 추가

1. **모델 정의** (`app/models/`)
```python
# app/models/item.py
from sqlalchemy import Column, Integer, String
from app.db.session import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
```

2. **스키마 정의** (`app/schemas/`)
```python
# app/schemas/item.py
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    description: str

class Item(ItemCreate):
    id: int

    class Config:
        from_attributes = True
```

3. **서비스 로직** (`app/services/`)
```python
# app/services/item.py
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate

def create_item(db: Session, item: ItemCreate):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
```

4. **API 엔드포인트** (`app/api/v1/endpoints/`)
```python
# app/api/v1/endpoints/items.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.item import Item, ItemCreate
from app.services.item import create_item

router = APIRouter()

@router.post("/", response_model=Item)
def create_item_endpoint(
    item: ItemCreate,
    db: Session = Depends(get_db)
):
    return create_item(db, item)
```

5. **라우터 등록** (`app/api/v1/__init__.py`)
```python
from app.api.v1.endpoints import items
api_router.include_router(items.router, prefix="/items", tags=["items"])
```

### 데이터베이스 마이그레이션

```bash
# 마이그레이션 생성
alembic revision --autogenerate -m "Add items table"

# 마이그레이션 적용
alembic upgrade head

# 롤백
alembic downgrade -1

# 히스토리 확인
alembic history
```

### 테스트

```bash
# 모든 테스트 실행
pytest

# 특정 파일 테스트
pytest tests/test_items.py

# 커버리지 포함
pytest --cov=app tests/
```

## API 문서

서버 실행 후 자동 생성되는 API 문서:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/api/v1/openapi.json

## 환경 변수

`.env` 파일에 필요한 환경 변수 (.env.example 참조):

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## 트러블슈팅

### DB 연결 실패
```bash
# PostgreSQL 실행 확인
pg_isready -h localhost -p 5432

# DATABASE_URL 확인
cat .env | grep DATABASE_URL
```

### 마이그레이션 에러
```bash
# 현재 버전 확인
alembic current

# 모든 마이그레이션 취소 후 재실행
alembic downgrade base
alembic upgrade head
```

## 다음 단계

1. 인증 시스템 추가: `Use auth-backend --init`
2. 메뉴 관리 추가: `Use menu-backend --init`
3. 카테고리 관리 추가: `Use category-manager --init`
