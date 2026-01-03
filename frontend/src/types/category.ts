/**
 * Category Management Types
 */

export interface Category {
  id: number
  tenant_id: number
  board_id: number
  parent_id: number | null
  depth: number
  path: string | null
  category_name: string
  category_code: string
  description?: string
  sort_order: number
  icon?: string
  color?: string
  read_permission: 'all' | 'members' | 'admin'
  write_permission: 'all' | 'members' | 'admin'
  post_count: number
  created_at: string
  created_by?: string
  updated_at: string
  updated_by?: string
  is_active: boolean
}

export interface CategoryTree extends Category {
  children?: CategoryTree[]
}

export interface CategoryCreateRequest {
  tenant_id: number
  board_id: number
  category_name: string
  category_code: string
  description?: string
  parent_id?: number | null
  sort_order?: number
  icon?: string
  color?: string
  read_permission?: 'all' | 'members' | 'admin'
  write_permission?: 'all' | 'members' | 'admin'
}

export interface CategoryUpdateRequest {
  category_name?: string
  description?: string
  parent_id?: number | null
  sort_order?: number
  icon?: string
  color?: string
  read_permission?: 'all' | 'members' | 'admin'
  write_permission?: 'all' | 'members' | 'admin'
  is_active?: boolean
}

export interface CategoryReorderRequest {
  category_id: number
  new_parent_id: number | null
  new_sort_order: number
}

export interface CategoryBreadcrumb {
  id: number
  name: string
  code: string
}
