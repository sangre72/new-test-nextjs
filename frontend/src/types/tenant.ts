/**
 * Tenant Type Definitions
 * Types for tenant management system
 */

/**
 * Tenant settings configuration
 */
export interface TenantSettings {
  theme?: 'default' | 'light' | 'dark'
  language?: 'ko' | 'en' | 'ja' | 'zh'
  timezone?: string
  primaryColor?: string
  companyName?: string
  logo?: string
  favicon?: string
  contactEmail?: string
  contactPhone?: string
  [key: string]: any
}

/**
 * Tenant status enumeration
 */
export enum TenantStatus {
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  INACTIVE = 'inactive',
}

/**
 * Tenant base properties
 */
export interface TenantBase {
  tenant_code: string
  tenant_name: string
  description?: string
  domain?: string
  subdomain?: string
  settings?: TenantSettings
  admin_email?: string
  admin_name?: string
  status?: TenantStatus | string
}

/**
 * Tenant request for creation
 */
export interface CreateTenantRequest extends TenantBase {}

/**
 * Tenant request for updates
 */
export interface UpdateTenantRequest {
  tenant_name?: string
  description?: string
  domain?: string
  subdomain?: string
  settings?: TenantSettings
  admin_email?: string
  admin_name?: string
  status?: TenantStatus | string
}

/**
 * Tenant response
 */
export interface Tenant extends TenantBase {
  id: number
  created_at: string
  created_by?: string
  updated_at: string
  updated_by?: string
  is_active: boolean
  is_deleted: boolean
}

/**
 * Tenant detail response with relationships
 */
export interface TenantDetail extends Tenant {
  users?: any[]
  user_groups?: any[]
}

/**
 * Tenant statistics
 */
export interface TenantStats {
  tenant_id: number
  total_users: number
  total_groups: number
  total_menus: number
  total_boards: number
}

/**
 * List response metadata
 */
export interface ListMeta {
  skip: number
  limit: number
  total: number
  hasMore: boolean
}

/**
 * Paginated list response
 */
export interface PaginatedResponse<T> {
  data: T[]
  meta: ListMeta
}
