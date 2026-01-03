# Category Management System - Setup & Implementation

## Overview

A comprehensive category management system for FastAPI + Next.js application with support for:
- Hierarchical categories (infinite depth)
- Per-board category management
- Multi-tenant support
- Drag & drop reordering
- Permission-based access control
- PostgreSQL backend

## Database Schema

### Categories Table

```sql
CREATE TABLE categories (
  id BIGINT PRIMARY KEY,
  tenant_id BIGINT NOT NULL (FK: tenants.id),
  board_id BIGINT NOT NULL (FK: boards.id),
  parent_id BIGINT (FK: categories.id),
  depth INT (0 = root),
  path VARCHAR(500) -- e.g., '/1/3/7/'
  category_name VARCHAR(100),
  category_code VARCHAR(50) UNIQUE per board,
  description TEXT,
  sort_order INT,
  icon VARCHAR(50),
  color VARCHAR(20),
  read_permission VARCHAR(50) -- all, members, admin
  write_permission VARCHAR(50) -- all, members, admin
  post_count INT (cached),
  created_at TIMESTAMP,
  created_by VARCHAR(100),
  updated_at TIMESTAMP,
  updated_by VARCHAR(100),
  is_active BOOLEAN,
  is_deleted BOOLEAN (soft delete)
);
```

## Backend Setup

### 1. Models

**File**: `/backend/app/models/category.py`

- Category model with hierarchical structure
- Self-referential parent-child relationships
- Indexed for performance

### 2. Schemas

**File**: `/backend/app/schemas/category.py`

- CategoryCreate: Create request with validation
- CategoryUpdate: Update request (all fields optional)
- CategoryResponse: Response model
- CategoryTreeResponse: Hierarchical response
- CategoryReorderRequest: Drag & drop support

### 3. Service Layer

**File**: `/backend/app/services/category.py`

Key methods:
- `get_categories_tree()`: Hierarchical tree structure
- `get_categories_flat()`: Flat list with depth info
- `create_category()`: Create with parent validation
- `update_category()`: Update with cycle prevention
- `delete_category()`: Soft delete with safety checks
- `reorder_categories()`: Drag & drop support
- `get_category_breadcrumb()`: Breadcrumb navigation

### 4. API Endpoints

**File**: `/backend/app/api/v1/endpoints/categories.py`

```
GET    /api/v1/categories/board/{board_id}/tree
GET    /api/v1/categories/board/{board_id}/flat
GET    /api/v1/categories/{category_id}
POST   /api/v1/categories/
PUT    /api/v1/categories/{category_id}
DELETE /api/v1/categories/{category_id}
POST   /api/v1/categories/reorder
GET    /api/v1/categories/{category_id}/breadcrumb
```

### 5. Migration

**File**: `/backend/alembic/versions/002_create_categories_table.py`

Run migrations:
```bash
cd backend
alembic upgrade head
```

## Frontend Setup

### 1. Types

**File**: `/frontend/src/types/category.ts`

```typescript
interface Category { ... }
interface CategoryTree extends Category { children?: CategoryTree[] }
interface CategoryCreateRequest { ... }
interface CategoryUpdateRequest { ... }
interface CategoryReorderRequest { ... }
```

### 2. API Client

**File**: `/frontend/src/lib/api/categories.ts`

Functions:
- `getCategoriesTree()`: Get hierarchical structure
- `getCategoriesFlat()`: Get flat list
- `getCategory()`: Get single category
- `createCategory()`: Create new
- `updateCategory()`: Update existing
- `deleteCategory()`: Delete (soft delete)
- `reorderCategory()`: Drag & drop reorder
- `getCategoryBreadcrumb()`: Breadcrumb path

### 3. Components

#### CategoryTree Component
**File**: `/frontend/src/components/categories/CategoryTree.tsx`

Displays hierarchical category tree with:
- Expand/collapse navigation
- Color indicators
- Post count badges
- Edit/Delete buttons

#### CategoryForm Component
**File**: `/frontend/src/components/categories/CategoryForm.tsx`

Form for creating/editing categories:
- Input validation
- Parent selection
- Permission controls
- Color picker
- Sort order management

#### CategoryManager Component
**File**: `/frontend/src/components/categories/CategoryManager.tsx`

Full-featured manager with:
- Tree view on left
- Detail/form on right
- Create, read, update, delete operations
- Real-time synchronization

## Usage Examples

### Backend - Create Category

```python
from app.services.category import CategoryService
from app.schemas.category import CategoryCreate

category_data = CategoryCreate(
    tenant_id=1,
    board_id=1,
    category_name="General Discussion",
    category_code="general",
    parent_id=None,
    description="General category for discussions"
)

category = CategoryService.create_category(
    category_create=category_data,
    created_by="admin_user",
    session=db
)
```

### Frontend - Use CategoryManager

```tsx
import { CategoryManager } from '@/components/categories'

export default function CategoriesPage() {
  return (
    <CategoryManager
      boardId={1}
      tenantId={1}
      boardName="General Discussion Board"
    />
  )
}
```

### API Calls

```typescript
// Get hierarchical tree
const tree = await getCategoriesTree(boardId, tenantId)

// Create category
const newCategory = await createCategory({
  tenant_id: 1,
  board_id: 1,
  category_name: "News",
  category_code: "news",
  parent_id: null
})

// Update category
await updateCategory(categoryId, tenantId, {
  category_name: "Updated Name",
  sort_order: 5
})

// Reorder (drag & drop)
await reorderCategory(tenantId, {
  category_id: 3,
  new_parent_id: 1,
  new_sort_order: 10
})
```

## Features

### Hierarchical Structure
- Unlimited nesting depth
- Path-based hierarchy (`/1/3/7/`)
- Cycle prevention (parent cannot be descendant)
- Auto-calculation of depth

### Drag & Drop Support
- Move categories between parents
- Reorder within same parent
- Real-time path/depth updates
- No circular reference creation

### Permission Model
- Read permissions (all, members, admin)
- Write permissions (all, members, admin)
- Per-category granular control

### Safety Features
- Soft delete (is_deleted flag)
- No deletion with children/posts
- Circular reference prevention
- Automatic path updates on move

### Performance
- Indexed paths for fast queries
- Depth-first traversal
- Flat list option for performance
- Post count caching

## Validation Rules

### Category Code
- Lowercase letters, numbers, underscores only
- 1-50 characters
- Unique per board
- Required

### Category Name
- 1-100 characters
- Required
- No HTML/script validation

### Parent Category
- Must exist in same board
- Cannot create circular references
- Cannot be its own parent
- Optional (NULL for root)

## Error Handling

### Common Errors

```
400 Bad Request
- Invalid category code format
- Missing required fields
- Circular reference attempted
- Duplicate category code

404 Not Found
- Category not found
- Board not found
- Parent category not found

409 Conflict
- Category code already exists
- Circular hierarchy detected

422 Unprocessable Entity
- Cannot delete category with children
- Cannot delete category with posts
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/test_categories.py -v
```

### Frontend Components

```bash
cd frontend
npm test -- categories.test.tsx
```

## Performance Considerations

1. **Path Indexing**: `idx_path` index enables efficient subtree queries
2. **Flat Queries**: Use `/flat` endpoint for list performance
3. **Lazy Loading**: Load children on expand for large trees
4. **Caching**: post_count cached in category row
5. **Pagination**: Consider pagination for 1000+ categories

## Future Enhancements

- [ ] Category visibility rules (IP-based, time-based)
- [ ] Category templates for quick setup
- [ ] Bulk category import/export
- [ ] Category statistics dashboard
- [ ] Category subscription notifications
- [ ] AI-powered category suggestions
- [ ] Multi-language category names
- [ ] Category moderation queue

## Integration with Posts

When implementing post system, add:

```python
# In posts table migration
category_id: BigInteger FK categories.id

# In post creation
if category_required and not post.category_id:
    raise ValidationError("Category is required")

# Update post count
category.post_count = session.query(Post).filter(
    Post.category_id == category.id,
    Post.is_deleted == False
).count()
```

## Troubleshooting

### Categories Not Showing
1. Check tenant_id matches current user's tenant
2. Verify board exists in user's tenant
3. Check is_deleted flag (soft deleted categories)

### Circular Reference Error
- Ensure parent is not a descendant of category
- Use `get_category_breadcrumb()` to verify hierarchy

### Path Updates Not Reflecting
- Run migration `002_create_categories_table.py`
- Check is_deleted flags in database
- Verify transaction commits

## Migration from Previous System

If migrating from flat categories:

```python
# Step 1: Create root categories
# Step 2: Migrate posts to categories
# Step 3: Calculate depth/path
# Step 4: Test thoroughly
# Step 5: Archive old data
```

## Security Checklist

- [x] Input validation on all fields
- [x] SQL injection prevention (parameterized queries)
- [x] Circular reference prevention
- [x] Soft delete protection
- [x] Tenant isolation enforced
- [x] Permission checks on all endpoints
- [x] Rate limiting recommended
- [x] Audit logging on all changes

## Deployment

1. **Database Migration**
   ```bash
   alembic upgrade head
   ```

2. **Environment Variables**
   ```
   DATABASE_URL=postgresql://...
   REDIS_URL=redis://...  (optional, for caching)
   ```

3. **Backend Startup**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. **Frontend Build**
   ```bash
   npm run build
   npm start
   ```

## Support

For issues or questions:
1. Check this documentation
2. Review test files for examples
3. Check API error responses
4. Review logs for details

## License

Same as main project

## Changelog

### v1.0.0 (Initial Release)
- Category CRUD operations
- Hierarchical structure support
- Drag & drop reordering
- Permission-based access
- Multi-tenant support
- Frontend component suite
