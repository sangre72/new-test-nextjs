# Shared Database Schema - Setup Guide

## Overview

This guide covers the complete setup of the shared database schema for a multi-tenant FastAPI + Next.js + PostgreSQL application with SQLAlchemy and Alembic.

The shared schema includes:
- **Tenants**: Multi-tenant support for multiple sites/organizations
- **Users**: User management with authentication
- **Roles & Permissions**: Role-based access control (RBAC)
- **User Groups**: User segmentation and grouping
- **Menus**: Navigation menu management
- **Boards**: Community/forum board management

## Database Architecture

```
┌─────────────────────────────────────────────┐
│           Shared Schema (Public)             │
├─────────────────────────────────────────────┤
│                                              │
│  ┌─ tenants (multi-tenant support)          │
│  │  ├─ users                                │
│  │  ├─ user_groups                          │
│  │  ├─ menus                                │
│  │  └─ boards                               │
│  │                                           │
│  └─ roles (global)                          │
│     ├─ permissions                          │
│     ├─ role_permissions                     │
│     └─ user_roles                           │
│                                              │
└─────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- FastAPI 0.128.0+
- SQLAlchemy 2.0+
- Alembic

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Required packages** (if not in requirements.txt):
```
fastapi==0.128.0
sqlalchemy==2.0.23
alembic==1.13.1
psycopg2-binary==2.9.9  # PostgreSQL adapter
passlib[bcrypt]==1.7.4  # Password hashing
pydantic-settings==2.1.0
```

### 2. Set Environment Variables

Create `.env` file in the `backend` directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/myapp_db

# Application
PROJECT_NAME=MyApp
VERSION=1.0.0
ENVIRONMENT=development

# Security
SECRET_KEY=your-secret-key-here-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Multi-Tenancy
ENABLE_MULTI_TENANCY=true
DEFAULT_TENANT_SCHEMA=public
```

### 3. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE myapp_db;
```

### 4. Run Migrations

```bash
cd backend

# Apply all migrations
alembic upgrade head

# Or apply a specific migration
alembic upgrade 001_create_shared_schema
```

### 5. Seed Initial Data

```python
# From Python shell or script
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.init_seed import init_db

# Create tables
Base.metadata.create_all(bind=engine)

# Seed data
db = SessionLocal()
try:
    init_db(db)
finally:
    db.close()
```

Or create a script file:

```bash
# backend/scripts/seed_db.py
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.init_seed import init_db

if __name__ == "__main__":
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Seed initial data
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
```

Run it:
```bash
cd backend
python scripts/seed_db.py
```

### 6. Start Backend Server

```bash
cd backend
python app/main.py

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit API docs: http://localhost:8000/docs

## Database Schema Details

### tenants Table

Represents a tenant (site/organization) in multi-tenant architecture.

| Column | Type | Description |
|--------|------|-------------|
| id | BigInteger | Primary key |
| tenant_code | String(50) | Unique code (e.g., "default", "siteA") |
| tenant_name | String(100) | Display name |
| domain | String(255) | Custom domain (e.g., siteA.com) |
| subdomain | String(100) | Subdomain (e.g., siteA) |
| settings | JSON | Tenant-specific settings (theme, logo, etc) |
| status | Enum | active, suspended, inactive |
| created_at | DateTime | Creation timestamp |
| is_active | Boolean | Soft delete flag |
| is_deleted | Boolean | Hard delete flag |

**Example:**
```sql
INSERT INTO tenants (tenant_code, tenant_name, domain, subdomain, status)
VALUES ('default', 'Default Site', 'localhost', 'localhost', 'active');
```

### users Table

Represents a user account.

| Column | Type | Description |
|--------|------|-------------|
| id | BigInteger | Primary key |
| tenant_id | BigInteger | Foreign key to tenants |
| username | String(100) | Unique within tenant |
| email | String(255) | Unique within tenant |
| hashed_password | String(255) | Hashed password |
| full_name | String(100) | Display name |
| is_superuser | Boolean | System-wide admin |
| status | Enum | active, inactive, suspended, deleted |
| is_email_verified | Boolean | Email verification flag |
| last_login_at | DateTime | Last login timestamp |

**Example:**
```python
from app.services.shared import UserService
from app.db.session import SessionLocal

db = SessionLocal()
service = UserService(db)

user = service.create(UserCreate(
    username="john",
    email="john@example.com",
    password="secure_password_123",
    tenant_id=1
))
```

### roles Table

Represents a role in the system.

| Column | Type | Description |
|--------|------|-------------|
| id | BigInteger | Primary key |
| role_code | String(50) | Unique code (e.g., "admin", "viewer") |
| role_name | String(100) | Display name |
| priority | BigInteger | Higher = more authority |
| role_type | Enum | admin, user, both |

**Default Roles:**
- `super_admin` (Priority: 100) - Full system access
- `admin` (Priority: 50) - Administrative access
- `manager` (Priority: 30) - Management access
- `editor` (Priority: 20) - Content editing
- `viewer` (Priority: 10) - Read-only access

### permissions Table

Represents a permission in the system.

| Column | Type | Description |
|--------|------|-------------|
| id | BigInteger | Primary key |
| permission_code | String(100) | Unique code (e.g., "user_read") |
| permission_name | String(100) | Display name |
| resource | Enum | tenant, user, menu, board, category, role, permission |
| action | Enum | create, read, update, delete, manage |

**Permission Format:**
```
{resource}_{action}

Examples:
- user_read: Read users
- user_create: Create users
- user_manage: Full user management
- menu_update: Update menu items
```

### user_groups Table

Groups users for segmentation (e.g., VIP members, regular members).

| Column | Type | Description |
|--------|------|-------------|
| id | BigInteger | Primary key |
| tenant_id | BigInteger | Foreign key to tenants (optional) |
| group_code | String(50) | Unique code within tenant |
| group_name | String(100) | Display name |
| priority | BigInteger | Higher = higher precedence |
| group_type | Enum | system (built-in), custom |

**Default Groups:**
- `all_members` - All users
- `regular_users` - Regular users
- `vip_users` - VIP members
- `premium_users` - Premium members

### Relationship Tables

#### user_roles
Links users to roles.

```sql
CREATE TABLE user_roles (
  id BIGINT PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  role_id BIGINT REFERENCES roles(id) ON DELETE CASCADE,
  UNIQUE(user_id, role_id)
);
```

#### user_group_members
Links users to groups.

```sql
CREATE TABLE user_group_members (
  id BIGINT PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  group_id BIGINT REFERENCES user_groups(id) ON DELETE CASCADE,
  UNIQUE(user_id, group_id)
);
```

#### role_permissions
Links roles to permissions.

```sql
CREATE TABLE role_permissions (
  id BIGINT PRIMARY KEY,
  role_id BIGINT REFERENCES roles(id) ON DELETE CASCADE,
  permission_id BIGINT REFERENCES permissions(id) ON DELETE CASCADE,
  UNIQUE(role_id, permission_id)
);
```

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Tenants

```bash
# Create tenant
POST /tenants
{
  "tenant_code": "siteA",
  "tenant_name": "Site A",
  "domain": "siteA.com",
  "admin_email": "admin@siteA.com"
}

# List tenants
GET /tenants?skip=0&limit=100

# Get tenant by ID
GET /tenants/{tenant_id}

# Get tenant by code
GET /tenants/code/{code}

# Update tenant
PATCH /tenants/{tenant_id}

# Delete tenant (soft delete)
DELETE /tenants/{tenant_id}
```

### Users

```bash
# Create user
POST /users
{
  "username": "john",
  "email": "john@example.com",
  "full_name": "John Doe",
  "password": "secure_password_123",
  "tenant_id": 1
}

# List users
GET /users?skip=0&limit=100

# Get user
GET /users/{user_id}

# Get tenant users
GET /tenants/{tenant_id}/users

# Update user
PATCH /users/{user_id}
{
  "full_name": "Jane Doe",
  "phone": "+1234567890"
}

# Delete user
DELETE /users/{user_id}
```

### Roles

```bash
# Create role
POST /roles
{
  "role_code": "custom_admin",
  "role_name": "Custom Admin",
  "priority": 75,
  "role_type": "admin"
}

# List roles
GET /roles

# Get role
GET /roles/{role_id}

# Assign role to user
POST /users/{user_id}/roles
{
  "role_id": 1
}

# Revoke role from user
DELETE /users/{user_id}/roles/{role_id}

# Get user roles
GET /users/{user_id}/roles

# Get user permissions
GET /users/{user_id}/permissions
```

### Permissions

```bash
# Create permission
POST /permissions
{
  "permission_code": "custom_action",
  "permission_name": "Custom Action",
  "resource": "user",
  "action": "create"
}

# List permissions
GET /permissions

# Get permission
GET /permissions/{permission_id}

# Add permission to role
POST /roles/{role_id}/permissions
{
  "permission_id": 1
}

# Get role permissions
GET /roles/{role_id}/permissions
```

### User Groups

```bash
# Create group
POST /user-groups
{
  "group_code": "gold_members",
  "group_name": "Gold Members",
  "tenant_id": 1,
  "priority": 30
}

# Get user groups in tenant
GET /tenants/{tenant_id}/user-groups

# Add user to group
POST /user-groups/{group_id}/members
{
  "user_id": 5
}

# Remove user from group
DELETE /user-groups/{group_id}/members/{user_id}

# Get group members
GET /user-groups/{group_id}/members

# Get user groups
GET /users/{user_id}/groups
```

### Menus

```bash
# Create menu
POST /menus
{
  "menu_code": "dashboard",
  "menu_name": "Dashboard",
  "menu_url": "/dashboard",
  "menu_icon": "dashboard",
  "display_order": 1,
  "tenant_id": 1
}

# Get tenant menus
GET /tenants/{tenant_id}/menus

# Update menu
PATCH /menus/{menu_id}

# Delete menu
DELETE /menus/{menu_id}
```

### Boards

```bash
# Create board
POST /boards
{
  "board_code": "announcements",
  "board_name": "Announcements",
  "tenant_id": 1
}

# Get tenant boards
GET /tenants/{tenant_id}/boards

# Update board
PATCH /boards/{board_id}

# Delete board
DELETE /boards/{board_id}
```

## Service Layer Usage

The service layer provides business logic for all models.

### User Service

```python
from app.db.session import SessionLocal
from app.services.shared import UserService
from app.schemas.shared import UserCreate

db = SessionLocal()
service = UserService(db)

# Create user
user = service.create(UserCreate(
    username="alice",
    email="alice@example.com",
    password="password123",
    tenant_id=1
))

# Get user
user = service.get(1)

# Get by username
user = service.get_by_username(tenant_id=1, username="alice")

# Get by email
user = service.get_by_email(tenant_id=1, email="alice@example.com")

# Get active users
users = service.get_active_users(tenant_id=1)

# Verify password
is_valid = service.verify_password(user, "password123")

# Update user
user = service.update(1, {"full_name": "Alice Smith"})

# Delete user (soft)
service.delete(1)

# Delete user (hard)
service.hard_delete(1)
```

### Role Service

```python
from app.services.shared import RoleService

service = RoleService(db)

# Create role
role = service.create(RoleCreate(
    role_code="custom_role",
    role_name="Custom Role",
    role_type="both"
))

# Get role
role = service.get(1)

# Get by code
role = service.get_by_code("admin")

# Add permission to role
role_perm = service.add_permission(role_id=1, permission_id=5)

# Remove permission from role
service.remove_permission(role_id=1, permission_id=5)

# Get role permissions
permissions = service.get_role_permissions(role_id=1)

# Get user roles
roles = service.get_user_roles(user_id=1)
```

### User Group Service

```python
from app.services.shared import UserGroupService

service = UserGroupService(db)

# Create group
group = service.create(UserGroupCreate(
    group_code="special_users",
    group_name="Special Users",
    tenant_id=1
))

# Add user to group
membership = service.add_user(group_id=1, user_id=5)

# Remove user from group
service.remove_user(group_id=1, user_id=5)

# Get group members
members = service.get_group_members(group_id=1)

# Get user groups
groups = service.get_user_groups(user_id=1)
```

### User Role Service

```python
from app.services.shared import UserRoleService

service = UserRoleService(db)

# Assign role to user
user_role = service.assign_role(user_id=1, role_id=2)

# Revoke role from user
service.revoke_role(user_id=1, role_id=2)

# Check if user has role
has_admin = service.has_role(user_id=1, role_code="admin")

# Check if user has permission
can_read_users = service.has_permission(user_id=1, permission_code="user_read")

# Get user permissions
permissions = service.get_user_permissions(user_id=1)
```

## Migration Management

### Generate Migration

After modifying models, generate a migration:

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migration

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade 001_create_shared_schema

# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade 001_create_shared_schema
```

### View Migration Status

```bash
alembic current
alembic history
```

## Security Best Practices

1. **Password Hashing**: All passwords are hashed using bcrypt
2. **Soft Deletes**: Default delete operation is soft (sets `is_deleted=true`)
3. **Audit Trail**: All tables include `created_by`, `updated_by`, `created_at`, `updated_at`
4. **Permissions**: Implement permission checks in your API endpoints
5. **Multi-tenancy**: Always filter by `tenant_id` to prevent data leakage

### Example: Permission Check Middleware

```python
from fastapi import Depends, HTTPException, status
from app.services.shared import UserRoleService

def check_permission(
    required_permission: str,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Check if user has required permission"""
    service = UserRoleService(db)

    if not service.has_permission(user_id, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    return True

# Usage in endpoint
@app.post("/admin/users")
def create_user(
    user_in: UserCreate,
    _: bool = Depends(lambda: check_permission("user_create", current_user.id, db))
):
    """Create user (requires user_create permission)"""
    pass
```

## Troubleshooting

### Migration Issues

**Problem**: "Target database is not up to date"
```bash
# Check current version
alembic current

# Reset to specific version
alembic downgrade base
alembic upgrade head
```

**Problem**: "Can't find revision"
```bash
# List all revisions
alembic history --verbose

# Check migration file in alembic/versions/
```

### Database Connection

**Problem**: "psycopg2.OperationalError: could not connect to server"
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string in .env
# Format: postgresql://user:password@localhost:5432/dbname
```

### Permission Denied

**Problem**: "permission denied for schema public"
```bash
# Run as superuser
psql -U postgres

# Grant permissions
GRANT ALL PRIVILEGES ON DATABASE myapp_db TO your_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO your_user;
```

## Next Steps

1. Implement JWT authentication in `/app/api/deps.py`
2. Add request logging middleware
3. Set up monitoring and alerting
4. Create comprehensive API tests
5. Implement data backup strategy
6. Set up CI/CD pipeline

## File Structure

```
backend/
├── alembic/
│   ├── versions/
│   │   └── 001_create_shared_schema.py
│   └── env.py
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── shared.py
│   │       └── __init__.py
│   ├── db/
│   │   ├── base.py
│   │   ├── init_seed.py
│   │   └── session.py
│   ├── models/
│   │   ├── shared.py
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── shared.py
│   │   └── __init__.py
│   ├── services/
│   │   ├── shared.py
│   │   └── __init__.py
│   ├── core/
│   │   └── config.py
│   ├── main.py
│   └── __init__.py
├── tests/
├── alembic.ini
├── requirements.txt
└── .env
```

## Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Support

For issues or questions, refer to:
1. Check this documentation
2. Review code comments and docstrings
3. Check API documentation at `/docs` (Swagger UI)
4. Check API schema at `/redoc` (ReDoc)

---

**Last Updated**: 2024-01-03
**Version**: 1.0.0
