'use client'

/**
 * MyPage Layout
 * 마이페이지 레이아웃 (네비게이션 포함)
 */

import React, { useState } from 'react'
import { Navigation, MobileDrawer } from '@/components/menus'

export default function MyPageLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 (모바일 메뉴 버튼 포함) */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">마이페이지</h1>

          {/* 모바일 메뉴 버튼 */}
          <button
            onClick={() => setIsMobileMenuOpen(true)}
            className="lg:hidden p-2 rounded-md hover:bg-gray-100"
            aria-label="메뉴 열기"
          >
            <svg
              className="w-6 h-6 text-gray-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="flex gap-6">
          {/* 좌측 네비게이션 (데스크톱) */}
          <aside className="hidden lg:block w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sticky top-24">
              <Navigation menuType="user" />
            </div>
          </aside>

          {/* 메인 컨텐츠 */}
          <main className="flex-1 min-w-0">
            {children}
          </main>
        </div>
      </div>

      {/* 모바일 드로어 */}
      <MobileDrawer
        menuType="user"
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />
    </div>
  )
}
