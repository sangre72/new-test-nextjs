'use client'

/**
 * Auth Context
 * 전역 인증 상태 관리
 * Security First: 토큰 안전 저장, 에러 처리
 */

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import * as authApi from '@/lib/api/auth'
import { User, RegisterRequest, ChangePasswordRequest, AuthContextType } from '@/types/auth'

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // 초기 로드 - 저장된 토큰으로 사용자 정보 조회
  useEffect(() => {
    const initAuth = async () => {
      const savedToken = authApi.getAuthToken()
      if (savedToken) {
        try {
          authApi.setAuthToken(savedToken)
          const userData = await authApi.getCurrentUser()
          setUser(userData)
        } catch (err) {
          // 토큰이 유효하지 않으면 삭제
          authApi.setAuthToken(null)
          console.error('Token validation failed:', err)
        }
      }
      setIsLoading(false)
    }

    initAuth()
  }, [])

  // 로그인
  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const response = await authApi.login({ email, password })
      setUser(response.user)
    } finally {
      setIsLoading(false)
    }
  }, [])

  // 로그아웃
  const logout = useCallback(async () => {
    try {
      await authApi.logout()
    } finally {
      setUser(null)
    }
  }, [])

  // 회원가입
  const register = useCallback(async (data: RegisterRequest) => {
    setIsLoading(true)
    try {
      await authApi.register(data)
      // 회원가입 후 자동 로그인
      await login(data.email, data.password)
    } finally {
      setIsLoading(false)
    }
  }, [login])

  // 비밀번호 변경
  const changePassword = useCallback(async (data: ChangePasswordRequest) => {
    setIsLoading(true)
    try {
      await authApi.changePassword(data)
    } finally {
      setIsLoading(false)
    }
  }, [])

  // 사용자 정보 새로고침
  const refreshUser = useCallback(async () => {
    const token = authApi.getAuthToken()
    if (!token) {
      setUser(null)
      return
    }

    try {
      const userData = await authApi.getCurrentUser()
      setUser(userData)
    } catch (err) {
      // 토큰 만료 시 로그아웃
      await logout()
    }
  }, [logout])

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
    register,
    changePassword,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * Custom hook - useAuth
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
