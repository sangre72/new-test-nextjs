/**
 * 테넌트 관련 타입 정의
 *
 * 포함:
 * - Tenant: 테넌트 정보
 * - TenantSettings: 테넌트 설정
 * - TenantCreate: 테넌트 생성 요청
 * - TenantUpdate: 테넌트 수정 요청
 */

/**
 * 테넌트 설정
 */
export interface TenantSettings {
  theme?: string;
  logo?: string;
  favicon?: string;
  language?: 'ko' | 'en' | 'ja' | 'zh';
  timezone?: string;
  primary_color?: string;
  company_name?: string;
  contact_email?: string;
  contact_phone?: string;
  [key: string]: any;
}

/**
 * 테넌트 정보
 */
export interface Tenant {
  id: number;
  tenant_code: string;
  tenant_name: string;
  description?: string;
  domain?: string;
  subdomain?: string;
  settings?: TenantSettings;
  admin_email?: string;
  admin_name?: string;
  created_at: string;
  created_by?: string;
  updated_at: string;
  updated_by?: string;
  is_active: boolean;
  is_deleted: boolean;
}

/**
 * 테넌트 생성 요청
 */
export interface TenantCreateRequest {
  tenant_code: string;
  tenant_name: string;
  description?: string;
  domain?: string;
  subdomain?: string;
  admin_email?: string;
  admin_name?: string;
  settings?: TenantSettings;
}

/**
 * 테넌트 수정 요청
 */
export interface TenantUpdateRequest {
  tenant_name?: string;
  description?: string;
  domain?: string;
  subdomain?: string;
  admin_email?: string;
  admin_name?: string;
  settings?: TenantSettings;
  is_active?: boolean;
}

/**
 * 테넌트 목록 응답
 */
export interface TenantListResponse {
  success: boolean;
  data: Tenant[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * 테넌트 상세 응답
 */
export interface TenantDetailResponse {
  success: boolean;
  data: Tenant;
  message?: string;
}

/**
 * 테넌트 설정 응답
 */
export interface TenantSettingsResponse {
  success: boolean;
  data: TenantSettings;
  message?: string;
}

/**
 * 공통 성공 응답
 */
export interface SuccessResponse<T = any> {
  success: true;
  data?: T;
  message?: string;
}

/**
 * 공통 실패 응답
 */
export interface ErrorResponse {
  success: false;
  error_code: string;
  message: string;
}

/**
 * API 응답 타입 (성공 or 실패)
 */
export type ApiResponse<T> = SuccessResponse<T> | ErrorResponse;
