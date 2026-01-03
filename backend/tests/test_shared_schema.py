"""
Tests for Shared Schema Models and Services
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.session import Base
from app.models.shared import (
    Tenant, User, UserGroup, UserGroupMember, Role, UserRole,
    Permission, RolePermission
)
from app.services.shared import (
    TenantService, UserService, UserGroupService, RoleService,
    PermissionService, UserRoleService
)
from app.schemas.shared import (
    TenantCreate, UserCreate, UserGroupCreate, RoleCreate, PermissionCreate
)


# Setup in-memory SQLite database for testing
@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for a test"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    engine.dispose()


class TestTenantService:
    """Tests for TenantService"""

    def test_create_tenant(self, db_session):
        """Test creating a tenant"""
        service = TenantService(db_session)

        tenant_in = TenantCreate(
            tenant_code="test_site",
            tenant_name="Test Site",
            domain="test.com"
        )

        tenant = service.create(tenant_in)

        assert tenant.id is not None
        assert tenant.tenant_code == "test_site"
        assert tenant.tenant_name == "Test Site"
        assert tenant.is_active is True
        assert tenant.is_deleted is False

    def test_get_tenant_by_code(self, db_session):
        """Test getting tenant by code"""
        service = TenantService(db_session)

        tenant_in = TenantCreate(
            tenant_code="unique_code",
            tenant_name="Unique Site"
        )
        created = service.create(tenant_in)

        found = service.get_by_code("unique_code")

        assert found is not None
        assert found.id == created.id
        assert found.tenant_code == "unique_code"

    def test_get_tenant_by_domain(self, db_session):
        """Test getting tenant by domain"""
        service = TenantService(db_session)

        tenant_in = TenantCreate(
            tenant_code="domain_test",
            tenant_name="Domain Test",
            domain="unique.com"
        )
        created = service.create(tenant_in)

        found = service.get_by_domain("unique.com")

        assert found is not None
        assert found.id == created.id

    def test_update_tenant(self, db_session):
        """Test updating a tenant"""
        service = TenantService(db_session)

        tenant_in = TenantCreate(
            tenant_code="update_test",
            tenant_name="Original Name"
        )
        tenant = service.create(tenant_in)

        from app.schemas.shared import TenantUpdate
        update_data = TenantUpdate(tenant_name="Updated Name")
        updated = service.update(tenant.id, update_data)

        assert updated.tenant_name == "Updated Name"

    def test_soft_delete_tenant(self, db_session):
        """Test soft deleting a tenant"""
        service = TenantService(db_session)

        tenant_in = TenantCreate(
            tenant_code="delete_test",
            tenant_name="Delete Test"
        )
        tenant = service.create(tenant_in)

        service.delete(tenant.id)

        # Check soft delete flag
        deleted = service.get(tenant.id)
        assert deleted.is_deleted is True


class TestUserService:
    """Tests for UserService"""

    def setup_method(self, method):
        """Create a tenant for each test"""
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db = self.SessionLocal()

        # Create a test tenant
        tenant = Tenant(
            tenant_code="test",
            tenant_name="Test Tenant",
            created_by="test"
        )
        self.db.add(tenant)
        self.db.commit()
        self.tenant_id = tenant.id

    def teardown_method(self, method):
        """Cleanup"""
        self.db.close()
        self.engine.dispose()

    def test_create_user(self):
        """Test creating a user"""
        service = UserService(self.db)

        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123",
            tenant_id=self.tenant_id
        )

        user = service.create(user_in)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True

    def test_get_user_by_username(self):
        """Test getting user by username"""
        service = UserService(self.db)

        user_in = UserCreate(
            username="findme",
            email="findme@example.com",
            password="password123",
            tenant_id=self.tenant_id
        )
        created = service.create(user_in)

        found = service.get_by_username(self.tenant_id, "findme")

        assert found is not None
        assert found.id == created.id

    def test_get_user_by_email(self):
        """Test getting user by email"""
        service = UserService(self.db)

        user_in = UserCreate(
            username="emailtest",
            email="unique@example.com",
            password="password123",
            tenant_id=self.tenant_id
        )
        created = service.create(user_in)

        found = service.get_by_email(self.tenant_id, "unique@example.com")

        assert found is not None
        assert found.id == created.id

    def test_verify_password(self):
        """Test password verification"""
        service = UserService(self.db)

        user_in = UserCreate(
            username="passtest",
            email="passtest@example.com",
            password="mypassword",
            tenant_id=self.tenant_id
        )
        user = service.create(user_in)

        # Correct password
        assert service.verify_password(user, "mypassword") is True

        # Wrong password
        assert service.verify_password(user, "wrongpassword") is False


class TestRoleService:
    """Tests for RoleService"""

    def test_create_role(self, db_session):
        """Test creating a role"""
        service = RoleService(db_session)

        role_in = RoleCreate(
            role_code="test_role",
            role_name="Test Role",
            priority=50
        )

        role = service.create(role_in)

        assert role.id is not None
        assert role.role_code == "test_role"
        assert role.role_name == "Test Role"
        assert role.priority == 50

    def test_get_role_by_code(self, db_session):
        """Test getting role by code"""
        service = RoleService(db_session)

        role_in = RoleCreate(
            role_code="unique_role",
            role_name="Unique Role"
        )
        created = service.create(role_in)

        found = service.get_by_code("unique_role")

        assert found is not None
        assert found.id == created.id


class TestUserGroupService:
    """Tests for UserGroupService"""

    def setup_method(self, method):
        """Create a tenant for each test"""
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db = self.SessionLocal()

        # Create a test tenant
        tenant = Tenant(
            tenant_code="test",
            tenant_name="Test Tenant",
            created_by="test"
        )
        self.db.add(tenant)
        self.db.commit()
        self.tenant_id = tenant.id

    def teardown_method(self, method):
        """Cleanup"""
        self.db.close()
        self.engine.dispose()

    def test_create_user_group(self):
        """Test creating a user group"""
        service = UserGroupService(self.db)

        group_in = UserGroupCreate(
            group_code="test_group",
            group_name="Test Group",
            tenant_id=self.tenant_id
        )

        group = service.create(group_in)

        assert group.id is not None
        assert group.group_code == "test_group"
        assert group.tenant_id == self.tenant_id

    def test_add_user_to_group(self):
        """Test adding user to group"""
        user_service = UserService(self.db)
        group_service = UserGroupService(self.db)

        # Create user
        user_in = UserCreate(
            username="groupuser",
            email="groupuser@example.com",
            password="password123",
            tenant_id=self.tenant_id
        )
        user = user_service.create(user_in)

        # Create group
        group_in = UserGroupCreate(
            group_code="mygroup",
            group_name="My Group",
            tenant_id=self.tenant_id
        )
        group = group_service.create(group_in)

        # Add user to group
        membership = group_service.add_user(group.id, user.id)

        assert membership.user_id == user.id
        assert membership.group_id == group.id

    def test_get_group_members(self):
        """Test getting group members"""
        user_service = UserService(self.db)
        group_service = UserGroupService(self.db)

        # Create users
        users = []
        for i in range(3):
            user_in = UserCreate(
                username=f"member{i}",
                email=f"member{i}@example.com",
                password="password123",
                tenant_id=self.tenant_id
            )
            users.append(user_service.create(user_in))

        # Create group
        group_in = UserGroupCreate(
            group_code="testgroup",
            group_name="Test Group",
            tenant_id=self.tenant_id
        )
        group = group_service.create(group_in)

        # Add users to group
        for user in users:
            group_service.add_user(group.id, user.id)

        # Get members
        members = group_service.get_group_members(group.id)

        assert len(members) == 3


class TestUserRoleService:
    """Tests for UserRoleService"""

    def setup_method(self, method):
        """Create test data"""
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db = self.SessionLocal()

        # Create tenant
        tenant = Tenant(
            tenant_code="test",
            tenant_name="Test Tenant",
            created_by="test"
        )
        self.db.add(tenant)
        self.db.commit()
        self.tenant_id = tenant.id

        # Create user
        user = User(
            tenant_id=self.tenant_id,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            created_by="test"
        )
        self.db.add(user)
        self.db.commit()
        self.user_id = user.id

        # Create role
        role = Role(
            role_code="testrole",
            role_name="Test Role",
            created_by="test"
        )
        self.db.add(role)
        self.db.commit()
        self.role_id = role.id

        # Create permission
        perm = Permission(
            permission_code="test_read",
            permission_name="Test Read",
            resource="user",
            action="read",
            created_by="test"
        )
        self.db.add(perm)
        self.db.commit()
        self.permission_id = perm.id

    def teardown_method(self, method):
        """Cleanup"""
        self.db.close()
        self.engine.dispose()

    def test_assign_role(self):
        """Test assigning role to user"""
        service = UserRoleService(self.db)

        user_role = service.assign_role(self.user_id, self.role_id)

        assert user_role.user_id == self.user_id
        assert user_role.role_id == self.role_id

    def test_has_role(self):
        """Test checking if user has role"""
        service = UserRoleService(self.db)

        service.assign_role(self.user_id, self.role_id)

        assert service.has_role(self.user_id, "testrole") is True
        assert service.has_role(self.user_id, "otherrole") is False

    def test_revoke_role(self):
        """Test revoking role from user"""
        service = UserRoleService(self.db)

        service.assign_role(self.user_id, self.role_id)
        result = service.revoke_role(self.user_id, self.role_id)

        assert result is True
        assert service.has_role(self.user_id, "testrole") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
