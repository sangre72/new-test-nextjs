"""
API v1 Router
Includes all v1 endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import shared

api_router = APIRouter()

# Include shared endpoints (tenants, users, roles, permissions, etc.)
api_router.include_router(shared.router, tags=["Shared"])

# Health check endpoint
@api_router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}
