"""
FastAPI 메인 애플리케이션

설정:
- CORS 활성화
- 테넌트 미들웨어
- API v1 라우터 등록
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.tenant_middleware import TenantDetectionMiddleware
from app.api.v1_tenants import router as tenants_router

app = FastAPI(
    title="New Test API",
    description="FastAPI + Next.js 프로젝트",
    version="1.0.0",
)

# ============================================================
# CORS 설정
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 커스텀 미들웨어
# ============================================================
app.add_middleware(TenantDetectionMiddleware)

# ============================================================
# 헬스 체크
# ============================================================


@app.get("/")
async def root():
    """API 상태 확인"""
    return {
        "success": True,
        "message": "New Test API is running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "success": True,
        "status": "healthy",
    }


# ============================================================
# API v1 라우터 등록
# ============================================================
app.include_router(tenants_router)

# 카테고리 라우터 등록
try:
    from app.api.v1.endpoints import categories_router
    app.include_router(categories_router, prefix="/api/v1")
except ImportError:
    pass

# 메뉴 라우터 등록
try:
    from app.api.v1.endpoints.menus import router as menus_router
    app.include_router(menus_router, prefix="/api/v1", tags=["menus"])
except ImportError:
    pass
