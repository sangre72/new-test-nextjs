"""
테넌트 API 엔드포인트 테스트

pytest 기반의 단위 테스트

실행:
    pytest tests/test_tenants.py -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.db.base import Base
from app.models.shared import Tenant
from app.api.deps import get_session
from app.core.config import settings


@pytest.fixture
async def test_db():
    """테스트용 데이터베이스 설정"""
    # 테스트 DB URL (실제로는 별도의 테스트 DB 사용)
    test_db_url = settings.DATABASE_URL.replace("newtest", "newtest_test")

    engine = create_async_engine(test_db_url, echo=False)

    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_session():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    yield AsyncSessionLocal

    # 테이블 삭제
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def client(test_db):
    """FastAPI TestClient"""
    return TestClient(app)


class TestTenantCRUD:
    """테넌트 CRUD 테스트"""

    def test_list_tenants_empty(self, client):
        """빈 테넌트 목록 조회"""
        response = client.get("/api/v1/tenants")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total"] == 0
        assert data["data"] == []

    def test_create_tenant_success(self, client):
        """테넌트 생성 성공"""
        response = client.post(
            "/api/v1/tenants",
            json={
                "tenant_code": "shop_a",
                "tenant_name": "쇼핑몰 A",
                "description": "쇼핑몰",
                "subdomain": "shop_a",
                "admin_email": "admin@shopa.com",
                "admin_name": "관리자",
                "settings": {
                    "theme": "default",
                    "logo": "/uploads/logo.png",
                    "language": "ko"
                }
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["tenant_code"] == "shop_a"
        assert data["data"]["tenant_name"] == "쇼핑몰 A"
        assert data["message"] == "테넌트가 생성되었습니다."

    def test_create_tenant_invalid_code(self, client):
        """잘못된 테넌트 코드 (대문자)"""
        response = client.post(
            "/api/v1/tenants",
            json={
                "tenant_code": "SHOP_A",  # 대문자 불허
                "tenant_name": "쇼핑몰 A"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "소문자" in data["detail"]

    def test_create_tenant_duplicate_code(self, client):
        """중복된 테넌트 코드"""
        # 첫 번째 생성
        client.post(
            "/api/v1/tenants",
            json={
                "tenant_code": "shop_b",
                "tenant_name": "쇼핑몰 B"
            }
        )

        # 두 번째 생성 (중복)
        response = client.post(
            "/api/v1/tenants",
            json={
                "tenant_code": "shop_b",
                "tenant_name": "쇼핑몰 B2"
            }
        )
        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert "존재하는" in data["detail"]

    def test_create_tenant_invalid_email(self, client):
        """잘못된 이메일"""
        response = client.post(
            "/api/v1/tenants",
            json={
                "tenant_code": "shop_c",
                "tenant_name": "쇼핑몰 C",
                "admin_email": "invalid-email"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "이메일" in data["detail"]

    def test_get_tenant(self, client):
        """테넌트 상세 조회"""
        # 테넌트 생성
        create_response = client.post(
            "/api/v1/tenants",
            json={
                "tenant_code": "shop_d",
                "tenant_name": "쇼핑몰 D"
            }
        )
        tenant_id = create_response.json()["data"]["id"]

        # 상세 조회
        response = client.get(f"/api/v1/tenants/{tenant_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == tenant_id
        assert data["data"]["tenant_code"] == "shop_d"

    def test_get_tenant_not_found(self, client):
        """존재하지 않는 테넌트 조회"""
        response = client.get("/api/v1/tenants/99999")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False

    def test_update_tenant(self, client):
        """테넌트 수정"""
        # 테넌트 생성
        create_response = client.post(
            "/api/v1/tenants",
            json={
                "tenant_code": "shop_e",
                "tenant_name": "쇼핑몰 E"
            }
        )
        tenant_id = create_response.json()["data"]["id"]

        # 수정
        response = client.put(
            f"/api/v1/tenants/{tenant_id}",
            json={
                "tenant_name": "쇼핑몰 E (수정됨)",
                "admin_name": "새로운 관리자",
                "settings": {
                    "theme": "dark",
                    "primary_color": "#ffffff"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["tenant_name"] == "쇼핑몰 E (수정됨)"
        assert data["data"]["admin_name"] == "새로운 관리자"
        assert data["data"]["settings"]["theme"] == "dark"

    def test_delete_tenant(self, client):
        """테넌트 삭제"""
        # 테넌트 생성
        create_response = client.post(
            "/api/v1/tenants",
            json={
                "tenant_code": "shop_f",
                "tenant_name": "쇼핑몰 F"
            }
        )
        tenant_id = create_response.json()["data"]["id"]

        # 삭제
        response = client.delete(f"/api/v1/tenants/{tenant_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "테넌트가 삭제되었습니다."

        # 삭제 확인
        get_response = client.get(f"/api/v1/tenants/{tenant_id}")
        assert get_response.status_code == 404


class TestTenantSettings:
    """테넌트 설정 테스트"""

    def test_get_tenant_settings(self, client):
        """테넌트 설정 조회"""
        # 테넌트 생성
        create_response = client.post(
            "/api/v1/tenants",
            json={
                "tenant_code": "shop_g",
                "tenant_name": "쇼핑몰 G",
                "settings": {
                    "theme": "default",
                    "logo": "/uploads/logo.png",
                    "language": "ko"
                }
            }
        )
        tenant_id = create_response.json()["data"]["id"]

        # 설정 조회
        response = client.get(f"/api/v1/tenants/{tenant_id}/settings")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["theme"] == "default"
        assert data["data"]["logo"] == "/uploads/logo.png"

    def test_update_tenant_settings(self, client):
        """테넌트 설정 수정 (부분 업데이트)"""
        # 테넌트 생성
        create_response = client.post(
            "/api/v1/tenants",
            json={
                "tenant_code": "shop_h",
                "tenant_name": "쇼핑몰 H",
                "settings": {
                    "theme": "default",
                    "logo": "/uploads/logo.png",
                    "language": "ko"
                }
            }
        )
        tenant_id = create_response.json()["data"]["id"]

        # 설정 부분 수정
        response = client.patch(
            f"/api/v1/tenants/{tenant_id}/settings",
            json={
                "theme": "dark",
                "primary_color": "#ff6b6b"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # 기존 설정은 유지되어야 함
        assert data["data"]["theme"] == "dark"
        assert data["data"]["logo"] == "/uploads/logo.png"
        assert data["data"]["primary_color"] == "#ff6b6b"

    def test_update_tenant_settings_invalid_email(self, client):
        """테넌트 설정 수정 - 잘못된 이메일"""
        # 테넌트 생성
        create_response = client.post(
            "/api/v1/tenants",
            json={
                "tenant_code": "shop_i",
                "tenant_name": "쇼핑몰 I"
            }
        )
        tenant_id = create_response.json()["data"]["id"]

        # 잘못된 이메일로 수정
        response = client.patch(
            f"/api/v1/tenants/{tenant_id}/settings",
            json={
                "contact_email": "invalid-email"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "이메일" in data["detail"]


class TestTenantFiltering:
    """테넌트 필터링 테스트"""

    def test_list_tenants_with_pagination(self, client):
        """테넌트 목록 페이징"""
        # 5개 테넌트 생성
        for i in range(5):
            client.post(
                "/api/v1/tenants",
                json={
                    "tenant_code": f"shop_{i}",
                    "tenant_name": f"쇼핑몰 {i}"
                }
            )

        # 첫 페이지 (limit=2)
        response = client.get("/api/v1/tenants?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1

        # 두 번째 페이지
        response = client.get("/api/v1/tenants?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["page"] == 2

    def test_list_tenants_filter_active(self, client):
        """활성 테넌트 필터링"""
        # 활성 테넌트 생성
        create_response = client.post(
            "/api/v1/tenants",
            json={
                "tenant_code": "active_tenant",
                "tenant_name": "활성 테넌트"
            }
        )
        active_id = create_response.json()["data"]["id"]

        # 비활성 테넌트 생성 후 비활성화
        create_response = client.post(
            "/api/v1/tenants",
            json={
                "tenant_code": "inactive_tenant",
                "tenant_name": "비활성 테넌트"
            }
        )
        inactive_id = create_response.json()["data"]["id"]

        client.put(
            f"/api/v1/tenants/{inactive_id}",
            json={"is_active": False}
        )

        # 활성 테넌트만 조회
        response = client.get("/api/v1/tenants?is_active=true")
        assert response.status_code == 200
        data = response.json()
        assert all(t["is_active"] for t in data["data"])
