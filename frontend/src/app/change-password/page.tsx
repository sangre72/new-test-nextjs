'use client'

/**
 * Change Password Page
 * 비밀번호 변경 페이지
 * Security First: 현재 비밀번호 확인, 안전한 변경
 */

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'

function ChangePasswordContent() {
  const router = useRouter()
  const { changePassword, isLoading } = useAuth()

  // 폼 상태
  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
    newPasswordConfirm: '',
  })
  const [showPassword, setShowPassword] = useState(false)

  // 에러/성공 상태
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

  // 필드 변경
  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [field]: e.target.value })
    // 에러 초기화
    if (fieldErrors[field]) {
      setFieldErrors({ ...fieldErrors, [field]: '' })
    }
    setError(null)
    setSuccess(null)
  }

  // 검증
  const validate = (): boolean => {
    const errors: Record<string, string> = {}

    // 현재 비밀번호
    if (!formData.currentPassword) {
      errors.currentPassword = '현재 비밀번호를 입력해주세요.'
    }

    // 새 비밀번호
    if (!formData.newPassword) {
      errors.newPassword = '새 비밀번호를 입력해주세요.'
    } else if (formData.newPassword.length < 8) {
      errors.newPassword = '비밀번호는 8자 이상이어야 합니다.'
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.newPassword)) {
      errors.newPassword = '비밀번호는 대문자, 소문자, 숫자를 포함해야 합니다.'
    } else if (formData.newPassword === formData.currentPassword) {
      errors.newPassword = '현재 비밀번호와 다른 비밀번호를 입력해주세요.'
    }

    // 새 비밀번호 확인
    if (!formData.newPasswordConfirm) {
      errors.newPasswordConfirm = '새 비밀번호 확인을 입력해주세요.'
    } else if (formData.newPassword !== formData.newPasswordConfirm) {
      errors.newPasswordConfirm = '비밀번호가 일치하지 않습니다.'
    }

    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  // 폼 제출
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)

    if (!validate()) {
      return
    }

    try {
      await changePassword(formData)
      setSuccess('비밀번호가 성공적으로 변경되었습니다.')
      // 폼 초기화
      setFormData({
        currentPassword: '',
        newPassword: '',
        newPasswordConfirm: '',
      })
      // 3초 후 홈으로 이동
      setTimeout(() => {
        router.push('/')
      }, 3000)
    } catch (err: any) {
      setError(err.message || '비밀번호 변경에 실패했습니다.')
      // 보안을 위해 모든 비밀번호 필드 초기화
      setFormData({
        currentPassword: '',
        newPassword: '',
        newPasswordConfirm: '',
      })
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* 헤더 */}
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            비밀번호 변경
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            새로운 비밀번호로 변경하세요
          </p>
        </div>

        {/* 성공 메시지 */}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-800 rounded-md p-4">
            <div className="flex items-center">
              <svg
                className="h-5 w-5 text-green-400 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <span className="text-sm">{success}</span>
            </div>
          </div>
        )}

        {/* 에러 메시지 */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 rounded-md p-4">
            <div className="flex items-center">
              <svg
                className="h-5 w-5 text-red-400 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <span className="text-sm">{error}</span>
            </div>
          </div>
        )}

        {/* 폼 */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-4">
            {/* 현재 비밀번호 */}
            <div>
              <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700 mb-1">
                현재 비밀번호 <span className="text-red-500">*</span>
              </label>
              <input
                id="currentPassword"
                name="currentPassword"
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                required
                value={formData.currentPassword}
                onChange={handleChange('currentPassword')}
                className={`appearance-none relative block w-full px-3 py-2 border ${
                  fieldErrors.currentPassword ? 'border-red-300' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm`}
                placeholder="현재 비밀번호를 입력하세요"
              />
              {fieldErrors.currentPassword && (
                <p className="mt-1 text-sm text-red-600">{fieldErrors.currentPassword}</p>
              )}
            </div>

            {/* 새 비밀번호 */}
            <div>
              <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 mb-1">
                새 비밀번호 <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                  id="newPassword"
                  name="newPassword"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  required
                  value={formData.newPassword}
                  onChange={handleChange('newPassword')}
                  className={`appearance-none relative block w-full px-3 py-2 border ${
                    fieldErrors.newPassword ? 'border-red-300' : 'border-gray-300'
                  } placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm`}
                  placeholder="8자 이상, 대소문자, 숫자 포함"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? (
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
              {fieldErrors.newPassword && (
                <p className="mt-1 text-sm text-red-600">{fieldErrors.newPassword}</p>
              )}
            </div>

            {/* 새 비밀번호 확인 */}
            <div>
              <label htmlFor="newPasswordConfirm" className="block text-sm font-medium text-gray-700 mb-1">
                새 비밀번호 확인 <span className="text-red-500">*</span>
              </label>
              <input
                id="newPasswordConfirm"
                name="newPasswordConfirm"
                type={showPassword ? 'text' : 'password'}
                autoComplete="new-password"
                required
                value={formData.newPasswordConfirm}
                onChange={handleChange('newPasswordConfirm')}
                className={`appearance-none relative block w-full px-3 py-2 border ${
                  fieldErrors.newPasswordConfirm ? 'border-red-300' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm`}
                placeholder="새 비밀번호를 다시 입력하세요"
              />
              {fieldErrors.newPasswordConfirm && (
                <p className="mt-1 text-sm text-red-600">{fieldErrors.newPasswordConfirm}</p>
              )}
            </div>
          </div>

          {/* 버튼 그룹 */}
          <div className="flex space-x-4">
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  변경 중...
                </span>
              ) : (
                '비밀번호 변경'
              )}
            </button>
            <Link
              href="/"
              className="flex-1 flex justify-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              취소
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function ChangePasswordPage() {
  return (
    <ProtectedRoute>
      <ChangePasswordContent />
    </ProtectedRoute>
  )
}
