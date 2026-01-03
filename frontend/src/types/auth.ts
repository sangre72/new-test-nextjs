/**
 * Auth Types
 * 인증 관련 타입 정의
 */

// 사용자 정보
export interface User {
  id: number
  email: string
  name: string
  role?: 'user' | 'admin' | 'super_admin'
  avatarUrl?: string
  isEmailVerified?: boolean
  createdAt?: string
  updatedAt?: string
}

// 로그인 요청
export interface LoginRequest {
  email: string
  password: string
}

// 로그인 응답
export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

// 회원가입 요청
export interface RegisterRequest {
  email: string
  password: string
  passwordConfirm: string
  name: string
  phone?: string
}

// 회원가입 응답
export interface RegisterResponse {
  id: number
  email: string
  name: string
  message: string
}

// 비밀번호 변경 요청
export interface ChangePasswordRequest {
  currentPassword: string
  newPassword: string
  newPasswordConfirm: string
}

// 인증 Context
export interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  changePassword: (data: ChangePasswordRequest) => Promise<void>
  refreshUser: () => Promise<void>
}

// API 응답
export interface ApiResponse<T> {
  success?: boolean
  data?: T
  error_code?: string
  message?: string
  detail?: string
}

// 에러 응답
export interface ApiError {
  message: string
  error_code?: string
  detail?: string
}
