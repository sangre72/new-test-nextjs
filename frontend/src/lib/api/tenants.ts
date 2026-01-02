/**
 * 테넌트 API 클라이언트
 *
 * 엔드포인트:
 * - GET /api/v1/tenants - 테넌트 목록
 * - GET /api/v1/tenants/{id} - 테넌트 상세
 * - POST /api/v1/tenants - 테넌트 생성
 * - PUT /api/v1/tenants/{id} - 테넌트 수정
 * - DELETE /api/v1/tenants/{id} - 테넌트 삭제
 * - GET /api/v1/tenants/{id}/settings - 설정 조회
 * - PATCH /api/v1/tenants/{id}/settings - 설정 수정
 */

import { apiClient } from './client';
import type {
  Tenant,
  TenantSettings,
  TenantCreateRequest,
  TenantUpdateRequest,
  TenantListResponse,
  TenantDetailResponse,
  TenantSettingsResponse,
} from '@/types/tenant';

const BASE_URL = '/api/v1/tenants';

/**
 * 테넌트 목록 조회
 */
export async function fetchTenants(
  skip: number = 0,
  limit: number = 20,
  isActive?: boolean
): Promise<TenantListResponse> {
  const params = new URLSearchParams();
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());
  if (isActive !== undefined) {
    params.append('is_active', isActive.toString());
  }

  const response = await apiClient.get(`${BASE_URL}?${params.toString()}`);
  return response.data;
}

/**
 * 테넌트 상세 조회
 */
export async function fetchTenant(tenantId: number): Promise<TenantDetailResponse> {
  const response = await apiClient.get(`${BASE_URL}/${tenantId}`);
  return response.data;
}

/**
 * 테넌트 생성
 */
export async function createTenant(
  data: TenantCreateRequest
): Promise<TenantDetailResponse> {
  const response = await apiClient.post(BASE_URL, data);
  return response.data;
}

/**
 * 테넌트 수정
 */
export async function updateTenant(
  tenantId: number,
  data: TenantUpdateRequest
): Promise<TenantDetailResponse> {
  const response = await apiClient.put(`${BASE_URL}/${tenantId}`, data);
  return response.data;
}

/**
 * 테넌트 삭제
 */
export async function deleteTenant(tenantId: number): Promise<any> {
  const response = await apiClient.delete(`${BASE_URL}/${tenantId}`);
  return response.data;
}

/**
 * 테넌트 설정 조회
 */
export async function fetchTenantSettings(
  tenantId: number
): Promise<TenantSettingsResponse> {
  const response = await apiClient.get(`${BASE_URL}/${tenantId}/settings`);
  return response.data;
}

/**
 * 테넌트 설정 수정 (부분 업데이트)
 */
export async function updateTenantSettings(
  tenantId: number,
  settings: Partial<TenantSettings>
): Promise<TenantSettingsResponse> {
  const response = await apiClient.patch(
    `${BASE_URL}/${tenantId}/settings`,
    settings
  );
  return response.data;
}
