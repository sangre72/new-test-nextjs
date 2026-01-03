# Category Integration with Posts System

## Overview

This guide explains how to integrate the category management system with a posts/articles system.

## Database Schema

### Posts Table (With Category)

```sql
CREATE TABLE posts (
  id BIGINT PRIMARY KEY,
  tenant_id BIGINT NOT NULL (FK: tenants.id),
  board_id BIGINT NOT NULL (FK: boards.id),
  category_id BIGINT (FK: categories.id),  -- New field

  -- Post content
  title VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  slug VARCHAR(255),
  excerpt VARCHAR(500),

  -- Post metadata
  author_id BIGINT NOT NULL (FK: users.id),
  view_count INT DEFAULT 0,
  comment_count INT DEFAULT 0,

  -- Post settings
  is_pinned BOOLEAN DEFAULT FALSE,
  is_locked BOOLEAN DEFAULT FALSE,

  -- Audit fields
  created_at TIMESTAMP,
  created_by VARCHAR(100),
  updated_at TIMESTAMP,
  updated_by VARCHAR(100),
  is_active BOOLEAN DEFAULT TRUE,
  is_deleted BOOLEAN DEFAULT FALSE,

  FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
  UNIQUE(board_id, slug),
  INDEX idx_category_id (category_id),
  INDEX idx_board_category (board_id, category_id),
  INDEX idx_created_at (created_at)
);
```

## Alembic Migration

### Add Category to Posts

**File**: `/backend/alembic/versions/003_add_category_to_posts.py`

```python
"""Add category_id to posts table

Revision ID: 003_add_category_to_posts
Revises: 002_create_categories_table
Create Date: 2024-01-03 08:45:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '003_add_category_to_posts'
down_revision = '002_create_categories_table'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add category_id column to posts"""
    op.add_column('posts', sa.Column(
        'category_id',
        sa.BigInteger(),
        nullable=True,
        comment="Category this post belongs to"
    ))

    op.create_foreign_key(
        'fk_posts_category_id',
        'posts', 'categories',
        ['category_id'], ['id'],
        ondelete='SET NULL'
    )

    op.create_index('idx_category_id', 'posts', ['category_id'])
    op.create_index('idx_board_category', 'posts', ['board_id', 'category_id'])

def downgrade() -> None:
    """Remove category_id column from posts"""
    op.drop_index('idx_board_category', 'posts')
    op.drop_index('idx_category_id', 'posts')
    op.drop_constraint('fk_posts_category_id', 'posts', type_='foreignkey')
    op.drop_column('posts', 'category_id')
```

## Backend Implementation

### Update Post Model

```python
# In app/models/post.py

from app.models.category import Category

class Post(Base, AuditMixin):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # Foreign Keys
    tenant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False
    )
    board_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        comment="Category this post belongs to"
    )
    author_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=True)
    excerpt: Mapped[str] = mapped_column(String(500), nullable=True)

    # Metadata
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)

    # Settings
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    category = relationship("Category", backref="posts")
    author = relationship("User", backref="posts")

    # Indexes
    __table_args__ = (
        UniqueConstraint("board_id", "slug", name="uk_board_slug"),
        Index("idx_category_id", "category_id"),
        Index("idx_board_category", "board_id", "category_id"),
        Index("idx_created_at", "created_at"),
    )
```

### Update Category Model

Add post count relationship:

```python
# In app/models/category.py

from sqlalchemy import func
from app.models.post import Post

class Category(Base):
    __tablename__ = "categories"

    # ... existing fields ...

    # Relationship
    posts = relationship("Post", backref="category")

    # Method to update post count
    def update_post_count(self, session):
        """Update cached post count"""
        count = session.query(func.count(Post.id)).filter(
            and_(
                Post.category_id == self.id,
                Post.is_deleted == False
            )
        ).scalar()
        self.post_count = count or 0
```

### Post Schema with Category

```python
# In app/schemas/post.py

from typing import Optional
from app.schemas.category import CategoryResponse

class PostCreate(BaseModel):
    title: str
    content: str
    category_id: Optional[int] = None  # Optional category
    board_id: int
    tenant_id: int

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    category_id: Optional[int] = None
    category: Optional[CategoryResponse] = None  # Nested category
    author_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### Post Service

```python
# In app/services/post.py

class PostService:

    @staticmethod
    def create_post(
        post_data: PostCreate,
        author_id: int,
        session: Session
    ) -> PostResponse:
        """Create a new post"""

        # Validate category if provided
        if post_data.category_id:
            category = session.query(Category).filter(
                and_(
                    Category.id == post_data.category_id,
                    Category.board_id == post_data.board_id,
                    Category.is_deleted == False
                )
            ).first()

            if not category:
                raise ValueError("Category not found or deleted")

            # Check write permission
            if category.write_permission == "admin":
                # Implement user role check
                pass

        # Create post
        post = Post(
            title=post_data.title,
            content=post_data.content,
            category_id=post_data.category_id,
            board_id=post_data.board_id,
            tenant_id=post_data.tenant_id,
            author_id=author_id
        )

        session.add(post)
        session.flush()

        # Update category post count
        if post_data.category_id:
            category = session.query(Category).filter(
                Category.id == post_data.category_id
            ).first()
            category.post_count += 1

        session.commit()
        return PostResponse.model_validate(post)

    @staticmethod
    def move_post_to_category(
        post_id: int,
        new_category_id: int,
        session: Session
    ) -> PostResponse:
        """Move post to different category"""

        post = session.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise ValueError("Post not found")

        # Update counts
        if post.category_id:
            old_category = session.query(Category).filter(
                Category.id == post.category_id
            ).first()
            if old_category:
                old_category.post_count = max(0, old_category.post_count - 1)

        if new_category_id:
            new_category = session.query(Category).filter(
                Category.id == new_category_id
            ).first()
            if new_category:
                new_category.post_count += 1

        post.category_id = new_category_id
        session.commit()

        return PostResponse.model_validate(post)

    @staticmethod
    def get_posts_by_category(
        category_id: int,
        board_id: int,
        session: Session
    ) -> List[PostResponse]:
        """Get all posts in a category"""

        posts = session.query(Post).filter(
            and_(
                Post.category_id == category_id,
                Post.board_id == board_id,
                Post.is_deleted == False
            )
        ).order_by(Post.created_at.desc()).all()

        return [PostResponse.model_validate(p) for p in posts]
```

### Post API Endpoints

```python
# In app/api/v1/endpoints/posts.py

@router.get("/board/{board_id}/category/{category_id}")
def get_posts_by_category(
    board_id: int,
    category_id: int,
    tenant_id: int = Query(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all posts in a specific category"""

    posts = PostService.get_posts_by_category(
        category_id=category_id,
        board_id=board_id,
        session=db
    )

    return posts

@router.post("/{post_id}/move-category/{category_id}")
def move_post_to_category(
    post_id: int,
    category_id: int,
    tenant_id: int = Query(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Move post to different category"""

    post = PostService.move_post_to_category(
        post_id=post_id,
        new_category_id=category_id,
        session=db
    )

    return post
```

## Frontend Implementation

### Update Post Types

```typescript
// In frontend/src/types/post.ts

import type { Category } from './category'

export interface Post {
  id: number
  title: string
  content: string
  category_id?: number | null
  category?: Category  // Nested category
  author_id: number
  author?: User
  view_count: number
  comment_count: number
  is_pinned: boolean
  is_locked: boolean
  created_at: string
  updated_at: string
}

export interface PostCreateRequest {
  title: string
  content: string
  category_id?: number | null
  board_id: number
  tenant_id: number
}

export interface PostUpdateRequest {
  title?: string
  content?: string
  category_id?: number | null
}
```

### Update Post API Client

```typescript
// In frontend/src/lib/api/posts.ts

import type { Post, PostCreateRequest, PostUpdateRequest } from '@/types/post'

export async function getPostsByCategory(
  boardId: number,
  categoryId: number,
  tenantId: number
): Promise<Post[]> {
  const response = await api.get<Post[]>(
    `/posts/board/${boardId}/category/${categoryId}`,
    { params: { tenant_id: tenantId } }
  )
  return response.data
}

export async function movePostToCategory(
  postId: number,
  categoryId: number,
  tenantId: number
): Promise<Post> {
  const response = await api.post<Post>(
    `/posts/${postId}/move-category/${categoryId}`,
    {},
    { params: { tenant_id: tenantId } }
  )
  return response.data
}
```

### Create Post Form with Category

```tsx
// In frontend/src/components/posts/PostForm.tsx

import { getCategoriesFlat } from '@/lib/api/categories'
import type { Category } from '@/types/category'

export function PostForm({ boardId, tenantId }: PostFormProps) {
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null)

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const cats = await getCategoriesFlat(boardId, tenantId)
        setCategories(cats)
      } catch (error) {
        console.error('Error loading categories:', error)
      }
    }

    loadCategories()
  }, [boardId, tenantId])

  return (
    <form className="space-y-4">
      {/* Title input */}
      <div>
        <label>Title</label>
        <input type="text" placeholder="Post title" />
      </div>

      {/* Content editor */}
      <div>
        <label>Content</label>
        <textarea placeholder="Post content" rows={10} />
      </div>

      {/* Category selector - NEW */}
      <div>
        <label>Category</label>
        <select
          value={selectedCategory || ''}
          onChange={(e) => setSelectedCategory(e.target.value ? parseInt(e.target.value) : null)}
        >
          <option value="">Select a category (optional)</option>
          {categories.map(cat => (
            <option key={cat.id} value={cat.id}>
              {'  '.repeat(cat.depth)}{cat.category_name}
            </option>
          ))}
        </select>
      </div>

      <button type="submit">Post</button>
    </form>
  )
}
```

### Display Posts by Category

```tsx
// In frontend/src/pages/board/[boardId]/category/[categoryId].tsx

import { getPostsByCategory } from '@/lib/api/posts'
import { getCategory } from '@/lib/api/categories'
import type { Post } from '@/types/post'

export default function CategoryPage({ params }: { params: { boardId: string; categoryId: string } }) {
  const [posts, setPosts] = useState<Post[]>([])
  const [category, setCategory] = useState(null)

  useEffect(() => {
    const load = async () => {
      const [postsData, categoryData] = await Promise.all([
        getPostsByCategory(parseInt(params.boardId), parseInt(params.categoryId), tenantId),
        getCategory(parseInt(params.categoryId), tenantId)
      ])
      setPosts(postsData)
      setCategory(categoryData)
    }
    load()
  }, [params.boardId, params.categoryId, tenantId])

  return (
    <div>
      <h1>{category?.category_name}</h1>
      <p>{category?.description}</p>

      <div className="posts">
        {posts.map(post => (
          <article key={post.id}>
            <h2>{post.title}</h2>
            <p>{post.excerpt}</p>
            <time>{new Date(post.created_at).toLocaleDateString()}</time>
          </article>
        ))}
      </div>
    </div>
  )
}
```

## Features Enabled by Integration

1. **Category Navigation**: Browse posts by category
2. **Auto Post Count**: Category post count auto-updates
3. **Post Organization**: Users can assign posts to categories
4. **Bulk Move**: Move multiple posts between categories
5. **Category Statistics**: Track activity per category
6. **Breadcrumb Navigation**: Show category path in post view
7. **Category-based Permissions**: Control who can see/post in category

## Migration Strategy

### Step 1: Add Category Column
```bash
alembic upgrade head
```

### Step 2: Set Default Categories
```python
# Assign all existing posts to "uncategorized" category
session.query(Post).update({Post.category_id: default_category_id})
session.commit()
```

### Step 3: Deploy Updates
- Update backend with new models/services
- Update frontend with new components
- Test thoroughly

### Step 4: Cleanup (Optional)
- Remove uncategorized category after migration
- Archive old post data

## Validation Rules

### When Creating Posts

```python
# Category must exist and not be deleted
if category_id:
    category = session.query(Category).filter(
        Category.id == category_id,
        Category.is_deleted == False
    ).first()

    if not category:
        raise ValueError("Category not found")

# Check write permission
if category.write_permission == "admin":
    if not user_is_admin:
        raise PermissionError("Not authorized to post in this category")

elif category.write_permission == "members":
    if not user_is_member:
        raise PermissionError("Must be member to post in this category")
```

### When Deleting Categories

```python
# Check for posts before deleting
post_count = session.query(Post).filter(
    Post.category_id == category_id,
    Post.is_deleted == False
).count()

if post_count > 0:
    raise ValueError(
        f"Cannot delete category with {post_count} posts. "
        "Move or delete posts first."
    )
```

## Performance Tips

1. **Eager Load Categories**: Use `selectinload()` when fetching posts
2. **Index Queries**: `idx_board_category` index speeds up category queries
3. **Cache Post Counts**: Update only on create/delete/move
4. **Pagination**: Always paginate post lists
5. **Select Fields**: Don't fetch entire content for lists

## Testing

### Test Cases

1. Create post with category
2. Create post without category
3. Move post to different category
4. Verify post count updates
5. Delete category without posts
6. Try to delete category with posts (should fail)
7. Check permission-based post visibility

## Next Integration Steps

1. **Comments**: Add category to comment notifications
2. **Search**: Filter search results by category
3. **Tags**: Combine with tag system
4. **Moderation**: Category-based moderation queues
5. **Notifications**: Category subscriptions

## Troubleshooting

### Post Count Not Updating
- Manually update: `category.update_post_count(session)`
- Check `is_deleted` flags

### Category Still Shows Deleted Posts
- Filter `is_deleted = False` in queries
- Soft delete doesn't remove immediately

### Migration Fails
- Check for existing `category_id` column
- Verify `categories` table exists
- Check foreign key constraints

## File References

Files to modify/create:
- `/backend/app/models/post.py` - Add category relationship
- `/backend/app/schemas/post.py` - Add category fields
- `/backend/app/services/post.py` - Update methods
- `/backend/app/api/v1/endpoints/posts.py` - Add category endpoints
- `/frontend/src/types/post.ts` - Add category type
- `/frontend/src/lib/api/posts.ts` - Add category methods
- `/frontend/src/components/posts/PostForm.tsx` - Add category selector

## Summary

The category system is now integrated with posts enabling:
- Organization of posts by category
- Hierarchical browsing
- Permission-based access
- Auto-updated post counts
- Future extensibility for filters, searches, and analytics
