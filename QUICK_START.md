# Quick Start Guide - Shared Database Schema

Get your FastAPI + Next.js + PostgreSQL application up and running with the shared database schema in 5 minutes.

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Node.js 18+ (for frontend)
- pip

## Step 1: Backend Setup (3 minutes)

### 1.1 Navigate to backend directory
```bash
cd backend
```

### 1.2 Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 1.3 Install dependencies
```bash
pip install -r requirements.txt
```

### 1.4 Configure environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your database credentials
nano .env
```

**Minimum required settings:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/myapp_db
SECRET_KEY=your-secret-key-change-this-min-32-chars
ENVIRONMENT=development
```

### 1.5 Create PostgreSQL database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE myapp_db;
\q
```

### 1.6 Run migrations
```bash
cd backend
alembic upgrade head
```

### 1.7 Initialize database with seed data
```bash
python scripts/init_db.py
```

Output should show:
```
Creating tables...
✓ Tables created successfully
Seeding initial data...
✓ Initial data seeded successfully

Database initialization complete!

Default credentials:
  - Username: superadmin
  - Password: superadmin123
  - Email: superadmin@localhost.com
```

### 1.8 Start backend server
```bash
python app/main.py
```

Server running at: **http://localhost:8000**
API docs: **http://localhost:8000/docs**

## Step 2: Test the API (1 minute)

### Option 1: Using Swagger UI (Recommended)
1. Open browser: http://localhost:8000/docs
2. Try any endpoint (e.g., GET /health)

### Option 2: Using curl
```bash
# Health check
curl http://localhost:8000/api/v1/health

# List tenants
curl http://localhost:8000/api/v1/tenants

# List users
curl http://localhost:8000/api/v1/users
```

### Option 3: Using Python
```python
import requests

# Get list of tenants
response = requests.get("http://localhost:8000/api/v1/tenants")
print(response.json())
```

## Step 3: Common Operations

### Create a new tenant
```bash
curl -X POST http://localhost:8000/api/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_code": "siteA",
    "tenant_name": "Site A",
    "domain": "siteA.com",
    "admin_email": "admin@siteA.com"
  }'
```

### Create a new user
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "full_name": "John Doe",
    "password": "securepassword123",
    "tenant_id": 1
  }'
```

### Assign role to user
```bash
# Get user ID and role ID first
# Then run:
curl -X POST http://localhost:8000/api/v1/users/2/roles \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": 2
  }'
```

## Step 4: Frontend Setup (Optional)

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.local.example .env.local

# Update API URL if needed
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" >> .env.local

# Start development server
npm run dev
```

Frontend running at: **http://localhost:3000**

## Database Schema Overview

```
tenants (Organization/Site)
  ├─ users (User accounts)
  │  ├─ user_groups (User segments)
  │  └─ user_roles (Role assignments)
  ├─ menus (Navigation)
  └─ boards (Community)

roles (Global)
  ├─ permissions (Global)
  └─ role_permissions (Permission mapping)
```

## Key Files

| File | Purpose |
|------|---------|
| `backend/app/models/shared.py` | SQLAlchemy models |
| `backend/app/schemas/shared.py` | Pydantic schemas |
| `backend/app/services/shared.py` | Business logic |
| `backend/app/api/v1/endpoints/shared.py` | API endpoints |
| `backend/alembic/versions/001_create_shared_schema.py` | Database migration |
| `backend/app/db/init_seed.py` | Initial seed data |

## Testing the Schema

### Run unit tests
```bash
cd backend
pytest tests/test_shared_schema.py -v
```

### Interactive testing
```python
from app.db.session import SessionLocal
from app.services.shared import UserService
from app.schemas.shared import UserCreate

db = SessionLocal()

# Create a user
user = UserService(db).create(UserCreate(
    username="testuser",
    email="test@example.com",
    password="password123",
    tenant_id=1
))

print(f"Created user: {user.username}")

db.close()
```

## Troubleshooting

### Database connection error
```
Error: could not connect to server
```

**Solution:**
1. Ensure PostgreSQL is running: `sudo systemctl status postgresql`
2. Check DATABASE_URL in .env is correct
3. Verify database exists: `psql -U postgres -l | grep myapp_db`

### Port already in use
```
Error: Address already in use
```

**Solution:**
```bash
# Kill process on port 8000
lsof -i :8000  # Find process
kill -9 <PID>
```

### Migration errors
```
Error: Target database is not up to date
```

**Solution:**
```bash
# Reset and reapply migrations
cd backend
alembic downgrade base
alembic upgrade head
```

### Import errors
```
ModuleNotFoundError: No module named 'app'
```

**Solution:**
```bash
# Ensure you're in backend directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt
```

## Default Login Credentials

After running `scripts/init_db.py`:

| Username | Email | Password | Role |
|----------|-------|----------|------|
| superadmin | superadmin@localhost.com | superadmin123 | Super Admin |
| admin | admin@localhost.com | admin123 | Admin |
| manager | manager@localhost.com | manager123 | Manager |
| editor | editor@localhost.com | editor123 | Editor |
| viewer | viewer@localhost.com | viewer123 | Viewer |

## Next Steps

1. [Read Full Setup Guide](./SHARED_SCHEMA_SETUP.md)
2. [API Documentation](http://localhost:8000/docs)
3. [Add JWT Authentication](https://fastapi.tiangolo.com/tutorial/security/)
4. [Create Frontend Components](./frontend)
5. [Deploy to Production](./SHARED_SCHEMA_SETUP.md#security-best-practices)

## Common Tasks

### List all API endpoints
```bash
curl http://localhost:8000/docs  # View in browser
# or
curl http://localhost:8000/openapi.json  # Get JSON
```

### Check database structure
```bash
psql -U postgres -d myapp_db -c "\dt"  # List tables
psql -U postgres -d myapp_db -c "\d users"  # Show user table structure
```

### Backup database
```bash
pg_dump myapp_db > backup.sql
```

### Restore database
```bash
psql myapp_db < backup.sql
```

## Performance Tips

1. **Database Indexes**: Already included on frequently queried columns
2. **Soft Deletes**: Use `is_deleted` instead of removing records
3. **Pagination**: Always use `skip` and `limit` parameters
4. **Connection Pooling**: SQLAlchemy handles this automatically

## Security Notes

- Never commit `.env` file to version control
- Change `SECRET_KEY` in production
- Use strong passwords for default accounts
- Enable HTTPS in production
- Implement rate limiting on API endpoints
- Keep dependencies updated

## Need Help?

1. Check logs: `docker logs myapp-api` (if using Docker)
2. Review documentation: [SHARED_SCHEMA_SETUP.md](./SHARED_SCHEMA_SETUP.md)
3. Check API docs: http://localhost:8000/docs
4. Review code comments in source files

---

**You're all set!** Your API is now ready to use. Start building with confidence.

For detailed documentation, see [SHARED_SCHEMA_SETUP.md](./SHARED_SCHEMA_SETUP.md)
