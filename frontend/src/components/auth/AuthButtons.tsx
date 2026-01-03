'use client'

/**
 * Auth Buttons Component
 * 로그인/로그아웃 버튼 컴포넌트
 */

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export const AuthButtons: React.FC = () => {
  const { user, isAuthenticated, logout, isLoading } = useAuth()
  const router = useRouter()

  const handleLogout = async () => {
    try {
      await logout()
      router.push('/login')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="h-8 w-8 rounded-full bg-gray-200 animate-pulse"></div>
      </div>
    )
  }

  if (isAuthenticated && user) {
    return (
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-medium">
            {user.name.charAt(0).toUpperCase()}
          </div>
          <span className="text-sm font-medium text-gray-700">{user.name}</span>
        </div>
        <button
          onClick={handleLogout}
          className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors"
        >
          로그아웃
        </button>
      </div>
    )
  }

  return (
    <div className="flex items-center space-x-2">
      <Link
        href="/login"
        className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
      >
        로그인
      </Link>
      <Link
        href="/register"
        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
      >
        회원가입
      </Link>
    </div>
  )
}

/**
 * User Menu Dropdown Component
 * 사용자 메뉴 드롭다운 (고급 버전)
 */
export const UserMenu: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth()
  const router = useRouter()
  const [isOpen, setIsOpen] = React.useState(false)

  const handleLogout = async () => {
    try {
      await logout()
      router.push('/login')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  if (!isAuthenticated || !user) {
    return <AuthButtons />
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 focus:outline-none"
      >
        <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-medium">
          {user.name.charAt(0).toUpperCase()}
        </div>
        <span className="text-sm font-medium text-gray-700">{user.name}</span>
        <svg
          className={`h-4 w-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          {/* 백드롭 */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          ></div>

          {/* 드롭다운 메뉴 */}
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-20 border border-gray-200">
            <div className="px-4 py-2 border-b border-gray-100">
              <p className="text-sm font-medium text-gray-900">{user.name}</p>
              <p className="text-xs text-gray-500">{user.email}</p>
            </div>

            <Link
              href="/profile"
              className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              onClick={() => setIsOpen(false)}
            >
              프로필
            </Link>

            <Link
              href="/change-password"
              className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              onClick={() => setIsOpen(false)}
            >
              비밀번호 변경
            </Link>

            <div className="border-t border-gray-100"></div>

            <button
              onClick={() => {
                setIsOpen(false)
                handleLogout()
              }}
              className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
            >
              로그아웃
            </button>
          </div>
        </>
      )}
    </div>
  )
}

import React from 'react'
