/**
 * Board-related TypeScript Types
 */

// Enums
export type BoardType = 'notice' | 'free' | 'qna' | 'faq' | 'gallery' | 'review'
export type PermissionLevel = 'public' | 'member' | 'admin' | 'disabled'
export type PostStatus = 'draft' | 'published' | 'hidden' | 'deleted'
export type CommentStatus = 'published' | 'hidden' | 'deleted'

// Board
export interface Board {
  id: number
  tenant_id: number
  board_name: string
  board_code: string
  description?: string
  board_type: BoardType
  read_permission: PermissionLevel
  write_permission: PermissionLevel
  comment_permission: PermissionLevel
  enable_categories: boolean
  enable_secret_post: boolean
  enable_attachments: boolean
  enable_likes: boolean
  enable_comments: boolean
  settings?: Record<string, any>
  display_order: number
  total_posts: number
  total_comments: number
  created_at: string
  created_by?: string
  updated_at: string
  updated_by?: string
  is_active: boolean
  is_deleted: boolean
}

export interface BoardCreate {
  tenant_id: number
  board_name: string
  board_code: string
  description?: string
  board_type: BoardType
  read_permission?: PermissionLevel
  write_permission?: PermissionLevel
  comment_permission?: PermissionLevel
  enable_categories?: boolean
  enable_secret_post?: boolean
  enable_attachments?: boolean
  enable_likes?: boolean
  enable_comments?: boolean
  settings?: Record<string, any>
  display_order?: number
}

export interface BoardUpdate {
  board_name?: string
  description?: string
  board_type?: BoardType
  read_permission?: PermissionLevel
  write_permission?: PermissionLevel
  comment_permission?: PermissionLevel
  enable_categories?: boolean
  enable_secret_post?: boolean
  enable_attachments?: boolean
  enable_likes?: boolean
  enable_comments?: boolean
  settings?: Record<string, any>
  display_order?: number
  is_active?: boolean
}

// Board Category
export interface BoardCategory {
  id: number
  board_id: number
  tenant_id: number
  category_name: string
  category_code: string
  description?: string
  color?: string
  display_order: number
  created_at: string
  is_active: boolean
}

export interface BoardCategoryCreate {
  board_id: number
  tenant_id: number
  category_name: string
  category_code: string
  description?: string
  color?: string
  display_order?: number
}

// Board Post
export interface BoardPost {
  id: number
  board_id: number
  tenant_id: number
  category_id?: number
  author_id: number
  title: string
  content: string
  status: PostStatus
  is_secret: boolean
  is_pinned: boolean
  is_notice: boolean
  is_answered: boolean
  accepted_answer_id?: number
  rating?: number
  view_count: number
  like_count: number
  comment_count: number
  metadata?: Record<string, any>
  published_at?: string
  created_at: string
  created_by?: string
  updated_at: string
  updated_by?: string
  is_active: boolean
}

export interface BoardPostListItem {
  id: number
  board_id: number
  category_id?: number
  category_name?: string
  author_id: number
  author_name: string
  title: string
  status: PostStatus
  is_secret: boolean
  is_pinned: boolean
  is_notice: boolean
  is_answered: boolean
  rating?: number
  view_count: number
  like_count: number
  comment_count: number
  created_at: string
  updated_at: string
}

export interface BoardPostDetail {
  id: number
  board_id: number
  tenant_id: number
  category_id?: number
  category_name?: string
  author_id: number
  author_name: string
  author_email?: string
  title: string
  content: string
  status: PostStatus
  is_secret: boolean
  is_pinned: boolean
  is_notice: boolean
  is_answered: boolean
  accepted_answer_id?: number
  rating?: number
  view_count: number
  like_count: number
  comment_count: number
  metadata?: Record<string, any>
  published_at?: string
  created_at: string
  created_by?: string
  updated_at: string
  updated_by?: string
  is_active: boolean
  can_edit: boolean
  can_delete: boolean
  has_liked: boolean
}

export interface BoardPostCreate {
  board_id: number
  tenant_id: number
  title: string
  content: string
  category_id?: number
  is_secret?: boolean
  is_pinned?: boolean
  is_notice?: boolean
  rating?: number
  metadata?: Record<string, any>
}

export interface BoardPostUpdate {
  title?: string
  content?: string
  category_id?: number
  is_secret?: boolean
  is_pinned?: boolean
  is_notice?: boolean
  status?: PostStatus
  rating?: number
  metadata?: Record<string, any>
}

export interface BoardPostListRequest {
  page?: number
  page_size?: number
  category_id?: number
  search?: string
  status?: PostStatus
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface BoardPostListPaginated {
  items: BoardPostListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// Board Comment
export interface BoardComment {
  id: number
  post_id: number
  tenant_id: number
  author_id: number
  author_name: string
  parent_id?: number
  content: string
  status: CommentStatus
  is_secret: boolean
  is_answer: boolean
  like_count: number
  created_at: string
  updated_at: string
  is_active: boolean
  can_edit: boolean
  can_delete: boolean
  replies: BoardComment[]
}

export interface BoardCommentCreate {
  post_id: number
  tenant_id: number
  content: string
  parent_id?: number
  is_secret?: boolean
  is_answer?: boolean
}

export interface BoardCommentUpdate {
  content?: string
  is_secret?: boolean
  status?: CommentStatus
}

// Board Attachment
export interface BoardAttachment {
  id: number
  post_id: number
  original_filename: string
  file_size: number
  mime_type?: string
  is_image: boolean
  width?: number
  height?: number
  download_count: number
  display_order: number
  created_at: string
  download_url?: string
  thumbnail_url?: string
}

export interface BoardAttachmentCreate {
  post_id: number
  tenant_id: number
  original_filename: string
  stored_filename: string
  file_path: string
  file_size: number
  mime_type?: string
  is_image?: boolean
  thumbnail_path?: string
  width?: number
  height?: number
  display_order?: number
}

// Board Like
export interface BoardLike {
  post_id: number
  user_id: number
  created_at: string
}

export interface BoardLikeResponse {
  is_liked: boolean
  like_count: number
}

// Statistics
export interface BoardStatistics {
  total_posts: number
  total_comments: number
  total_views: number
  total_likes: number
  recent_posts: number
}

export interface PostStatistics {
  view_count: number
  like_count: number
  comment_count: number
  is_liked_by_user: boolean
}
