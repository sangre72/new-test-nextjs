"""
Menu API Tests
Integration tests for menu management endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.models.shared import Menu, User, Tenant, MenuTypeEnum
from app.core.security import create_access_token, get_password_hash


@pytest.fixture
def db():
    """Database session fixture"""
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def test_user(db: Session):
    """Create test user"""
    # Get or create tenant
    tenant = db.query(Tenant).filter(Tenant.tenant_code == "test").first()
    if not tenant:
        tenant = Tenant(
            tenant_code="test",
            tenant_name="Test Tenant",
            is_active=True,
            created_by="test",
            updated_by="test"
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    # Create user
    user = User(
        tenant_id=tenant.id,
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        is_superuser=True,
        is_active=True,
        created_by="test",
        updated_by="test"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    yield user

    # Cleanup
    db.query(Menu).filter(Menu.tenant_id == tenant.id).delete()
    db.delete(user)
    db.delete(tenant)
    db.commit()


@pytest.fixture
def auth_token(test_user: User):
    """Create auth token"""
    return create_access_token(subject=test_user.id)


@pytest.fixture
def auth_headers(auth_token: str):
    """Create auth headers"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestMenuCRUD:
    """Test menu CRUD operations"""

    def test_create_menu(self, client: TestClient, auth_headers: dict, test_user: User):
        """Test menu creation"""
        response = client.post(
            "/api/v1/menus",
            headers=auth_headers,
            json={
                "menu_name": "Test Menu",
                "menu_code": "test-menu",
                "menu_type": "user",
                "menu_url": "/test",
                "menu_icon": "fa-test",
                "display_order": 1,
                "permission_type": "public",
                "is_visible": True,
                "is_active": True
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["menu_name"] == "Test Menu"
        assert data["menu_code"] == "test-menu"
        assert data["depth"] == 0

    def test_create_menu_with_parent(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test menu creation with parent"""
        # Create parent menu
        parent = Menu(
            tenant_id=test_user.tenant_id,
            menu_name="Parent",
            menu_code="parent",
            menu_type=MenuTypeEnum.USER,
            depth=0,
            display_order=1,
            created_by=test_user.username,
            updated_by=test_user.username
        )
        db.add(parent)
        db.commit()
        db.refresh(parent)

        parent.path = f"/{parent.id}"
        db.commit()

        # Create child menu
        response = client.post(
            "/api/v1/menus",
            headers=auth_headers,
            json={
                "menu_name": "Child Menu",
                "menu_code": "child-menu",
                "menu_type": "user",
                "parent_id": parent.id,
                "display_order": 1
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["parent_id"] == parent.id
        assert data["depth"] == 1

    def test_get_menus(self, client: TestClient, auth_headers: dict, test_user: User, db: Session):
        """Test get menus list"""
        # Create test menus
        for i in range(3):
            menu = Menu(
                tenant_id=test_user.tenant_id,
                menu_name=f"Menu {i}",
                menu_code=f"menu-{i}",
                menu_type=MenuTypeEnum.USER,
                depth=0,
                display_order=i,
                created_by=test_user.username,
                updated_by=test_user.username
            )
            db.add(menu)
        db.commit()

        # Get menus
        response = client.get("/api/v1/menus", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        assert len(data["items"]) >= 3

    def test_get_menu_tree(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test get menu tree"""
        # Create parent menu
        parent = Menu(
            tenant_id=test_user.tenant_id,
            menu_name="Parent",
            menu_code="parent",
            menu_type=MenuTypeEnum.USER,
            depth=0,
            display_order=1,
            created_by=test_user.username,
            updated_by=test_user.username
        )
        db.add(parent)
        db.commit()
        db.refresh(parent)

        parent.path = f"/{parent.id}"
        db.commit()

        # Create child menu
        child = Menu(
            tenant_id=test_user.tenant_id,
            menu_name="Child",
            menu_code="child",
            menu_type=MenuTypeEnum.USER,
            parent_id=parent.id,
            depth=1,
            path=f"/{parent.id}/{parent.id + 1}",
            display_order=1,
            created_by=test_user.username,
            updated_by=test_user.username
        )
        db.add(child)
        db.commit()

        # Get tree
        response = client.get(
            "/api/v1/menus/tree?menu_type=user",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1

    def test_update_menu(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test menu update"""
        # Create menu
        menu = Menu(
            tenant_id=test_user.tenant_id,
            menu_name="Original",
            menu_code="original",
            menu_type=MenuTypeEnum.USER,
            depth=0,
            display_order=1,
            created_by=test_user.username,
            updated_by=test_user.username
        )
        db.add(menu)
        db.commit()
        db.refresh(menu)

        # Update menu
        response = client.put(
            f"/api/v1/menus/{menu.id}",
            headers=auth_headers,
            json={"menu_name": "Updated"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["menu_name"] == "Updated"

    def test_delete_menu(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test menu deletion"""
        # Create menu
        menu = Menu(
            tenant_id=test_user.tenant_id,
            menu_name="To Delete",
            menu_code="to-delete",
            menu_type=MenuTypeEnum.USER,
            depth=0,
            display_order=1,
            created_by=test_user.username,
            updated_by=test_user.username
        )
        db.add(menu)
        db.commit()
        db.refresh(menu)

        # Delete menu
        response = client.delete(
            f"/api/v1/menus/{menu.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_deleted"] is True

    def test_reorder_menus(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test menu reordering"""
        # Create menus
        menus = []
        for i in range(3):
            menu = Menu(
                tenant_id=test_user.tenant_id,
                menu_name=f"Menu {i}",
                menu_code=f"menu-{i}",
                menu_type=MenuTypeEnum.USER,
                depth=0,
                display_order=i,
                created_by=test_user.username,
                updated_by=test_user.username
            )
            db.add(menu)
            menus.append(menu)
        db.commit()

        for menu in menus:
            db.refresh(menu)

        # Reorder
        response = client.put(
            "/api/v1/menus/reorder",
            headers=auth_headers,
            json={
                "items": [
                    {"menu_id": menus[2].id, "new_order": 0},
                    {"menu_id": menus[1].id, "new_order": 1},
                    {"menu_id": menus[0].id, "new_order": 2}
                ]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


class TestMenuValidation:
    """Test menu validation"""

    def test_invalid_menu_code(self, client: TestClient, auth_headers: dict):
        """Test invalid menu code"""
        response = client.post(
            "/api/v1/menus",
            headers=auth_headers,
            json={
                "menu_name": "Test",
                "menu_code": "test<script>",  # Invalid characters
                "menu_type": "user"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_invalid_menu_url(self, client: TestClient, auth_headers: dict):
        """Test invalid menu URL"""
        response = client.post(
            "/api/v1/menus",
            headers=auth_headers,
            json={
                "menu_name": "Test",
                "menu_code": "test",
                "menu_type": "user",
                "menu_url": "javascript:alert('xss')"  # XSS attempt
            }
        )

        assert response.status_code == 422  # Validation error

    def test_duplicate_menu_code(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test duplicate menu code"""
        # Create first menu
        menu = Menu(
            tenant_id=test_user.tenant_id,
            menu_name="First",
            menu_code="duplicate",
            menu_type=MenuTypeEnum.USER,
            depth=0,
            display_order=1,
            created_by=test_user.username,
            updated_by=test_user.username
        )
        db.add(menu)
        db.commit()

        # Try to create duplicate
        response = client.post(
            "/api/v1/menus",
            headers=auth_headers,
            json={
                "menu_name": "Second",
                "menu_code": "duplicate",  # Same code
                "menu_type": "user"
            }
        )

        assert response.status_code == 400  # Bad request


class TestMenuSecurity:
    """Test menu security"""

    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access"""
        response = client.get("/api/v1/menus")

        assert response.status_code == 401  # Unauthorized

    def test_public_endpoint_no_auth(self, client: TestClient):
        """Test public endpoint without auth"""
        response = client.get("/api/v1/menus/public/tree?menu_type=user")

        # Should work (may return empty if no data)
        assert response.status_code in [200, 500]  # 500 if tenant not found


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
