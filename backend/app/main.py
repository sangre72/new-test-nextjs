from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="New Test API",
    description="FastAPI + Next.js 프로젝트",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
