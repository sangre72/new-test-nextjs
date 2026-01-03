# Category Management - Quick Start Guide

## 5-Minute Setup

### Step 1: Run Database Migration

```bash
cd backend
alembic upgrade head
```

This creates the `categories` table with all necessary indexes.

### Step 2: Test Backend API

Start your FastAPI server:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

Test with curl:
```bash
# Get categories (tree format)
curl -X GET "http://localhost:8000/api/v1/categories/board/1/tree?tenant_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create a category
curl -X POST "http://localhost:8000/api/v1/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "tenant_id": 1,
    "board_id": 1,
    "category_name": "General",
    "category_code": "general",
    "description": "General discussion category"
  }'
```

### Step 3: Use Frontend Components

In your Next.js page:

```tsx
import { CategoryManager } from '@/components/categories'

export default function CategoriesPage() {
  return (
    <CategoryManager
      boardId={1}
      tenantId={1}
      boardName="My Discussion Board"
    />
  )
}
```

## Common Tasks

### Create a Category

**Backend API:**
```bash
POST /api/v1/categories/
{
  "tenant_id": 1,
  "board_id": 1,
  "category_name": "News",
  "category_code": "news",
  "description": "Latest news and updates",
  "icon": "newspaper",
  "color": "#FF5733"
}
```

**Frontend Code:**
```typescript
import { createCategory } from '@/lib/api/categories'

const newCategory = await createCategory({
  tenant_id: 1,
  board_id: 1,
  category_name: "News",
  category_code: "news"
})
```

### Create Subcategory

Just set the parent_id:

```bash
POST /api/v1/categories/
{
  "tenant_id": 1,
  "board_id": 1,
  "category_name": "Breaking News",
  "category_code": "breaking_news",
  "parent_id": 5  # parent category ID
}
```

### Get All Categories (Tree Format)

```bash
GET /api/v1/categories/board/1/tree?tenant_id=1
```

Response:
```json
[
  {
    "id": 1,
    "category_name": "General",
    "category_code": "general",
    "children": [
      {
        "id": 3,
        "category_name": "Announcements",
        "category_code": "announcements",
        "children": []
      }
    ]
  }
]
```

### Get All Categories (Flat Format)

```bash
GET /api/v1/categories/board/1/flat?tenant_id=1
```

Response:
```json
[
  {
    "id": 1,
    "category_name": "General",
    "category_code": "general",
    "depth": 0
  },
  {
    "id": 3,
    "category_name": "Announcements",
    "category_code": "announcements",
    "depth": 1
  }
]
```

### Update a Category

```bash
PUT /api/v1/categories/1?tenant_id=1
{
  "category_name": "General Discussion",
  "description": "Updated description",
  "sort_order": 5
}
```

### Delete a Category

```bash
DELETE /api/v1/categories/1?tenant_id=1
```

Note: Category must not have:
- Child categories
- Posts (depends on post system implementation)

### Reorder Category (Drag & Drop)

Move category to different parent and position:

```bash
POST /api/v1/categories/reorder?tenant_id=1
{
  "category_id": 5,
  "new_parent_id": 2,
  "new_sort_order": 10
}
```

### Get Breadcrumb Path

Get the hierarchy path to a category:

```bash
GET /api/v1/categories/7/breadcrumb
```

Response:
```json
{
  "breadcrumb": [
    { "id": 1, "name": "General", "code": "general" },
    { "id": 3, "name": "Announcements", "code": "announcements" },
    { "id": 7, "name": "Important", "code": "important" }
  ]
}
```

## Frontend Components

### CategoryManager (Full-Featured)

Complete UI with tree view, form, and management:

```tsx
<CategoryManager
  boardId={1}
  tenantId={1}
  boardName="Discussion Board"
/>
```

Features:
- Tree navigation on left
- Detail/form on right
- Create, read, update, delete
- Expand/collapse categories
- Edit inline

### CategoryTree (View Only)

Display categories in tree format:

```tsx
<CategoryTreeComponent
  categories={categories}
  selectedId={selectedId}
  onSelect={(id) => console.log('Selected:', id)}
  expandedIds={expandedIds}
  onToggleExpand={(id) => toggleExpand(id)}
/>
```

### CategoryForm (Form Only)

Standalone form for create/edit:

```tsx
<CategoryForm
  isEdit={true}
  category={selectedCategory}
  parentCategories={allCategories}
  onSubmit={(data) => updateCategory(data)}
  onCancel={() => resetForm()}
/>
```

## Data Structure

### Category Object

```typescript
interface Category {
  id: number                           // Unique ID
  tenant_id: number                    // Tenant owner
  board_id: number                     // Board owner
  parent_id: number | null             // Parent category (NULL for root)
  depth: number                        // 0 = root, increases with nesting
  path: string                         // e.g., '/1/3/7/'
  category_name: string                // Display name
  category_code: string                // Slug (unique per board)
  description?: string                 // Optional description
  sort_order: number                   // Display order
  icon?: string                        // Icon name
  color?: string                       // Hex color
  read_permission: string              // 'all', 'members', 'admin'
  write_permission: string             // 'all', 'members', 'admin'
  post_count: number                   // Cached post count
  created_at: string                   // ISO timestamp
  created_by?: string                  // Creator ID
  updated_at: string                   // ISO timestamp
  updated_by?: string                  // Last modifier ID
  is_active: boolean                   // Visible/usable
}
```

## Permission Examples

```typescript
// Everyone can read and write
{
  read_permission: "all",
  write_permission: "all"
}

// Everyone can read, only members can write
{
  read_permission: "all",
  write_permission: "members"
}

// Only admins can see and write
{
  read_permission: "admin",
  write_permission: "admin"
}
```

## Category Codes (Best Practices)

Always use lowercase, numbers, and underscores:

```
✅ good_code
✅ news_2024
✅ general_discussion

❌ Good Code (spaces)
❌ GoodCode (uppercase)
❌ good-code (hyphens)
```

## Error Handling

### Frontend

```typescript
try {
  const category = await createCategory(data)
  console.log('Success:', category)
} catch (error: any) {
  console.error('Error:', error.response?.data?.detail)
  // Handle specific errors:
  if (error.response?.status === 400) {
    // Validation error
  } else if (error.response?.status === 409) {
    // Conflict (code exists)
  }
}
```

### Common Errors

| Code | Message | Solution |
|------|---------|----------|
| 400 | Invalid category code format | Use only lowercase/numbers/underscores |
| 400 | Category code already exists | Use unique code per board |
| 404 | Category not found | Check ID and tenant_id |
| 409 | Cannot create circular reference | Parent cannot be descendant |
| 422 | Cannot delete category with children | Delete children first |

## Styling

Components use Tailwind CSS classes. Customize with:

```tsx
<CategoryManager
  boardId={1}
  tenantId={1}
  className="custom-class"  // Add custom class
/>
```

Or modify component files directly in:
- `/frontend/src/components/categories/CategoryManager.tsx`
- `/frontend/src/components/categories/CategoryTree.tsx`
- `/frontend/src/components/categories/CategoryForm.tsx`

## Testing

### Manual Testing

1. Create root category
2. Create subcategory under root
3. Create sub-subcategory (3 levels)
4. Edit category name
5. Change parent (reorder)
6. Delete leaf category
7. Verify error when trying to delete with children

### API Testing with Postman

Import this collection:

```json
{
  "info": {
    "name": "Categories API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Categories (Tree)",
      "request": {
        "method": "GET",
        "url": "{{BASE_URL}}/api/v1/categories/board/1/tree?tenant_id=1"
      }
    },
    {
      "name": "Create Category",
      "request": {
        "method": "POST",
        "url": "{{BASE_URL}}/api/v1/categories/",
        "body": {
          "mode": "raw",
          "raw": "{ \"tenant_id\": 1, \"board_id\": 1, \"category_name\": \"Test\", \"category_code\": \"test\" }"
        }
      }
    }
  ]
}
```

## Next Steps

1. **Integrate with Posts**: Add `category_id` to posts table
2. **Add Category Permissions**: Implement role-based access
3. **Category Statistics**: Dashboard showing activity per category
4. **Category Icons**: Use icon library integration
5. **Bulk Operations**: Import/export categories

## Support

- Check `/CATEGORY_SETUP.md` for detailed documentation
- Review test files for usage examples
- Check API response errors for details

## Files Created

Backend:
- `/backend/app/models/category.py` - Model definition
- `/backend/app/schemas/category.py` - Request/response schemas
- `/backend/app/services/category.py` - Business logic
- `/backend/app/api/v1/endpoints/categories.py` - API routes
- `/backend/alembic/versions/002_create_categories_table.py` - Database migration

Frontend:
- `/frontend/src/types/category.ts` - TypeScript types
- `/frontend/src/lib/api/categories.ts` - API client
- `/frontend/src/components/categories/CategoryManager.tsx` - Main component
- `/frontend/src/components/categories/CategoryTree.tsx` - Tree view
- `/frontend/src/components/categories/CategoryForm.tsx` - Form component

Documentation:
- `/CATEGORY_SETUP.md` - Full setup guide
- `/CATEGORY_QUICKSTART.md` - This file

## Success Checklist

- [x] Models created
- [x] Schemas created
- [x] Service layer implemented
- [x] API endpoints created
- [x] Migration created
- [x] Frontend types created
- [x] API client created
- [x] Components created
- [x] Documentation created
- [ ] Database migration applied (run: `alembic upgrade head`)
- [ ] Test with actual data
- [ ] Integrate with posts system
- [ ] Deploy to production
