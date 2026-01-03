# Category Management System - Deployment Guide

## Pre-Deployment Checklist

- [ ] All code reviewed and tested
- [ ] Database backups created
- [ ] Staging environment available
- [ ] Team notified of deployment
- [ ] Rollback plan prepared
- [ ] Monitoring configured
- [ ] Documentation updated

## Deployment Steps

### Phase 1: Database Migration (5 minutes)

#### 1. Backup Database
```bash
# PostgreSQL backup
pg_dump -h localhost -U postgres database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# Or using psql
psql -h localhost -U postgres database_name -c "SELECT pg_dump('database_name'::regclass);"
```

#### 2. Test Migration in Staging
```bash
# Connect to staging database
export DATABASE_URL=postgresql://user:pass@staging-db:5432/database

# Run migration
cd backend
alembic upgrade head

# Verify table created
alembic current
```

Output should show: `002_create_categories_table`

#### 3. Verify Table Structure
```sql
-- Connect to database
psql -h localhost -U postgres database_name

-- Check table
\d categories

-- Check indexes
\di categories*

-- Check constraints
SELECT * FROM information_schema.table_constraints
WHERE table_name = 'categories';
```

Expected output:
- 1 primary key (id)
- 1 unique constraint (board_id, category_code)
- 8 indexes
- 3 foreign keys (tenant_id, board_id, parent_id)

#### 4. Deploy to Production
```bash
# On production server
cd /path/to/backend

# Update code (pull from repo)
git pull origin main

# Run migration
alembic upgrade head

# Verify
alembic current
alembic history
```

### Phase 2: Backend Deployment (10 minutes)

#### 1. Update Environment

Ensure `.env` has required settings:
```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# API
API_V1_STR=/api/v1
PROJECT_NAME="Your Project"
ENVIRONMENT=production

# CORS
BACKEND_CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
```

#### 2. Update Backend Code
```bash
# Pull latest changes
git pull origin main

# Install dependencies (if updated)
pip install -r requirements.txt

# Run tests (if available)
pytest tests/test_categories.py -v

# Check imports
python -c "from app.models import Category; from app.api.v1.endpoints import categories; print('✓ Imports successful')"
```

#### 3. Restart FastAPI Server

**Option A: Using systemd**
```bash
sudo systemctl restart fastapi-app
sudo systemctl status fastapi-app

# Check logs
sudo journalctl -u fastapi-app -f
```

**Option B: Using Docker**
```bash
# Rebuild with new code
docker-compose down
docker-compose build
docker-compose up -d

# Check logs
docker-compose logs -f api
```

**Option C: Manual (Development)**
```bash
# Stop current process
# Start new process
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Or with gunicorn (production)
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

#### 4. Verify API is Working
```bash
# Health check
curl http://localhost:8000/api/v1/health
# Response: {"status":"healthy","version":"1.0.0"}

# Test categories endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/categories/board/1/tree?tenant_id=1"
```

### Phase 3: Frontend Deployment (10 minutes)

#### 1. Update Frontend Code
```bash
# Pull latest changes
git pull origin main

# Install dependencies (if updated)
npm install

# Build for production
npm run build

# Run tests (if available)
npm test

# Check for errors
npm run lint
```

#### 2. Deploy Built Files

**Option A: Using Vercel**
```bash
# Automatic deployment on push
git push origin main

# Or manual deployment
npm run build
vercel --prod
```

**Option B: Using Docker**
```bash
# Build Docker image
docker build -f frontend/Dockerfile -t myapp-frontend:latest .

# Push to registry
docker push myapp-frontend:latest

# Update Docker Compose or K8s deployment
docker-compose up -d
```

**Option C: Traditional Server**
```bash
# Build
npm run build

# Copy to web server
scp -r out/* user@server:/var/www/myapp/

# Or sync with S3
aws s3 sync out/ s3://my-bucket/
```

#### 3. Verify Frontend is Working
```bash
# Check app loads
curl https://yourdomain.com/

# Check API connectivity
# Open browser console and verify no CORS errors
```

### Phase 4: Testing (15 minutes)

#### 1. Manual Testing

```bash
# Test create category
curl -X POST http://localhost:8000/api/v1/categories/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "tenant_id": 1,
    "board_id": 1,
    "category_name": "Test Category",
    "category_code": "test_category",
    "description": "Test"
  }'

# Test get categories
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/categories/board/1/tree?tenant_id=1"

# Test update
curl -X PUT http://localhost:8000/api/v1/categories/1?tenant_id=1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"category_name": "Updated Name"}'

# Test delete
curl -X DELETE http://localhost:8000/api/v1/categories/1?tenant_id=1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 2. Browser Testing

Open browser console:
```javascript
// Test API client
import { getCategoriesTree } from '@/lib/api/categories'

// Fetch categories
getCategoriesTree(1, 1)
  .then(data => console.log('✓ Success:', data))
  .catch(err => console.error('✗ Error:', err))
```

#### 3. Check Logs
```bash
# Backend logs
tail -f /var/log/fastapi/app.log

# Frontend logs (browser console)
# Browser DevTools → Console tab

# Database logs (if configured)
tail -f /var/log/postgresql/postgresql.log
```

### Phase 5: Monitoring Setup (5 minutes)

#### 1. Set Up Alerts

**Application Monitoring**
```bash
# Monitor API response time
GET /api/v1/health
# Alert if > 1000ms

# Monitor error rate
# Alert if 5xx errors > 5% of requests

# Monitor database connections
# Alert if > 80% of max connections
```

**Database Monitoring**
```sql
-- Monitor table size
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename = 'categories';

-- Monitor index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE tablename = 'categories';
```

#### 2. Configure Logging
```python
# In app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### Phase 6: Post-Deployment (30 minutes)

#### 1. Verify All Features
- [ ] Can create categories
- [ ] Can view categories in tree format
- [ ] Can view categories in flat format
- [ ] Can edit categories
- [ ] Can delete categories
- [ ] Can reorder categories
- [ ] Breadcrumb navigation works
- [ ] Permissions enforced
- [ ] Error messages display correctly

#### 2. Performance Testing
```bash
# Load test with 100 concurrent users
ab -n 1000 -c 100 http://localhost:8000/api/v1/categories/board/1/tree?tenant_id=1

# Or using Apache Bench
# Expected response time: < 500ms
# Success rate: > 99.9%
```

#### 3. Data Validation
```sql
-- Verify no orphaned categories
SELECT * FROM categories WHERE parent_id IS NOT NULL
  AND parent_id NOT IN (SELECT id FROM categories WHERE is_deleted = false);

-- Verify path integrity
SELECT * FROM categories
WHERE parent_id IS NOT NULL
  AND path NOT LIKE (
    SELECT path FROM categories WHERE id = parent_id
  ) || '%';

-- Count total categories
SELECT COUNT(*) FROM categories WHERE is_deleted = false;
```

#### 4. Backup & Rollback Test
```bash
# Create backup
pg_dump database_name > backup_post_deploy.sql

# Test restore in staging
psql staging_db < backup_post_deploy.sql

# Verify restored data
psql staging_db -c "SELECT COUNT(*) FROM categories;"
```

## Rollback Procedures

### If Deployment Fails

#### Database Rollback
```bash
# Roll back migration
alembic downgrade -1

# Or rollback to specific revision
alembic downgrade 001_create_shared_schema
```

#### Code Rollback
```bash
# Revert to previous version
git revert <commit-hash>
git push origin main

# Or rollback to tag
git checkout tags/v1.0.0
git push origin main
```

#### Docker Rollback
```bash
# Redeploy previous image
docker-compose down
docker pull myapp:previous-tag
docker-compose up -d
```

### Full Rollback Checklist
- [ ] Stop current deployment
- [ ] Revert database migration
- [ ] Revert code to previous version
- [ ] Restart services
- [ ] Verify functionality
- [ ] Notify team

## Monitoring in Production

### Key Metrics to Track

1. **API Performance**
   - Response time per endpoint
   - Requests per second
   - Error rate

2. **Database**
   - Query execution time
   - Connection pool usage
   - Table/index sizes

3. **Application**
   - Memory usage
   - CPU usage
   - Active connections

### Setup Monitoring Tools

**Option 1: Datadog**
```python
# Install DDTrace
pip install ddtrace

# Run with tracing
ddtrace-run python -m uvicorn app.main:app
```

**Option 2: New Relic**
```python
# Install agent
pip install newrelic

# Update requirements.txt and deploy
```

**Option 3: Prometheus + Grafana**
```python
# Add prometheus client
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')
```

## Database Maintenance

### Regular Tasks

```bash
# Daily (in cron)
0 2 * * * psql -U postgres dbname -c "VACUUM ANALYZE categories;"

# Weekly (in cron)
0 3 * * 0 pg_dump dbname > /backups/daily_$(date +%Y%m%d).sql

# Monthly (in cron)
0 4 1 * * psql -U postgres dbname -c "REINDEX TABLE categories;"
```

### Monitoring Query Performance

```sql
-- Slow query log
SET log_min_duration_statement = 1000; -- Log queries > 1 second

-- Analyze query plans
EXPLAIN ANALYZE
SELECT * FROM categories
WHERE board_id = 1 AND is_deleted = false
ORDER BY sort_order;
```

## Scaling Considerations

### Vertical Scaling (Single Server)
- Increase PostgreSQL work_mem
- Increase shared_buffers
- Increase effective_cache_size

### Horizontal Scaling
- Use read replicas for queries
- Implement caching layer (Redis)
- Use connection pooling (PgBouncer)

### Database Optimization
```sql
-- Monitor table bloat
SELECT schemaname, tablename, round(n_dead_tup / n_live_tup * 100) AS dead_pct
FROM pg_stat_user_tables
WHERE tablename = 'categories';

-- Reindex if needed
REINDEX TABLE CONCURRENTLY categories;
```

## Documentation Updates

After successful deployment:

- [ ] Update deployment runbook
- [ ] Document any changes made
- [ ] Update architecture diagram
- [ ] Record version numbers
- [ ] Document rollback procedures
- [ ] Update team knowledge base

## Communication Plan

### Pre-Deployment
- [ ] Notify stakeholders 24 hours before
- [ ] Schedule maintenance window if needed
- [ ] Prepare status page message

### During Deployment
- [ ] Post status updates every 15 minutes
- [ ] Monitor actively
- [ ] Have rollback team ready

### Post-Deployment
- [ ] Announce success/completion
- [ ] Update documentation
- [ ] Schedule post-mortem if issues occurred

## Success Criteria

✅ All endpoints responding with correct status codes
✅ Database contains expected schema and data
✅ Frontend components load without errors
✅ API performance meets SLA (< 500ms response time)
✅ No critical errors in logs
✅ All validation tests passing
✅ Monitoring alerts configured
✅ Backup created and tested

## Troubleshooting During Deployment

### Common Issues

**1. Migration Fails**
```bash
# Check current state
alembic current

# Check history
alembic history

# If stuck, manually mark
alembic stamp 002_create_categories_table
```

**2. API Returns 500 Error**
```bash
# Check logs
tail -f /var/log/fastapi/app.log

# Check database connection
psql -h localhost -U user -d database -c "SELECT 1"

# Restart service
systemctl restart fastapi-app
```

**3. Frontend Components Not Found**
```bash
# Check build output
npm run build

# Verify imports
grep -r "from '@/components/categories'" src/

# Check tsconfig.json
cat tsconfig.json | grep baseUrl
```

## Performance After Deployment

### Query Performance Expected Times
- Get tree (100 categories): < 50ms
- Get flat (1000 categories): < 100ms
- Create category: < 100ms
- Update category: < 100ms
- Delete category: < 100ms

### Resource Usage Expected
- Memory: < 200MB for app
- CPU: < 10% at rest
- Database connections: < 10 active

## Post-Deployment Review

Conduct review meeting with:
- [ ] Development team
- [ ] Operations team
- [ ] Product team

Discuss:
- [ ] What went well
- [ ] What could be improved
- [ ] Action items for next release
- [ ] Performance metrics
- [ ] User feedback

## Deployment Checklist Template

```
Deployment Date: ___________
Deploy By: ___________
Reviewed By: ___________

[ ] Code reviewed
[ ] Tests passing
[ ] Database backup created
[ ] Migration tested in staging
[ ] Database migrated
[ ] Backend deployed
[ ] Frontend built and deployed
[ ] All endpoints tested
[ ] Monitoring configured
[ ] Team notified
[ ] Post-deployment review scheduled

Issues Encountered: _______________________
Resolution: _______________________________
Time to Deploy: ______________________
Status: ___SUCCESSFUL / ___ROLLED_BACK
```

## Contact & Support

For deployment issues:
1. Check logs first
2. Consult troubleshooting guide
3. Contact DevOps team
4. Prepare for rollback if needed

Deployment Team Contact:
- Lead: _______________
- Backup: _______________
- On-call: _______________
