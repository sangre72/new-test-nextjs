'use client'

/**
 * Mobile Drawer Component
 * 모바일 메뉴 드로어
 *
 * Security First: XSS 방지
 * Error Handling First: 에러 처리
 */

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import type { Menu, MenuType } from '@/types/menu'
import { getPublicMenus, isSafeUrl } from '@/lib/api/menus'
import { cn } from '@/lib/utils'

interface MobileDrawerProps {
  menuType: MenuType
  isOpen: boolean
  onClose: () => void
}

interface DrawerMenuItemProps {
  menu: Menu
  isActive: boolean
  onNavigate: () => void
  level?: number
}

function DrawerMenuItem({ menu, isActive, onNavigate, level = 0 }: DrawerMenuItemProps) {
  const [isExpanded, setIsExpanded] = useState(menu.default_expanded)

  const hasChildren = menu.children && menu.children.length > 0
  const hasLink = menu.link_type !== 'none' && menu.link_url

  const handleClick = (e: React.MouseEvent) => {
    // 하위 메뉴가 있으면 토글
    if (hasChildren && menu.is_expandable) {
      e.preventDefault()
      setIsExpanded(!isExpanded)
      return
    }

    // 외부 링크 안전성 검증
    if (menu.link_type === 'external' && menu.external_url) {
      if (!isSafeUrl(menu.external_url)) {
        e.preventDefault()
        console.warn('Blocked unsafe URL:', menu.external_url)
        return
      }
    }

    // 링크 클릭 시 드로어 닫기
    onNavigate()
  }

  const menuContent = (
    <>
      {menu.icon && <span className="text-xl">{menu.icon}</span>}
      <span className="flex-1 font-medium">{menu.menu_name}</span>
      {menu.badge_type !== 'none' && menu.badge_value && (
        <span
          className="px-2 py-1 text-xs rounded-full"
          style={{
            backgroundColor: menu.badge_color || '#3b82f6',
            color: 'white',
          }}
        >
          {menu.badge_value}
        </span>
      )}
      {menu.highlight && menu.highlight_text && (
        <span
          className="px-2 py-1 text-xs font-semibold rounded"
          style={{
            backgroundColor: menu.highlight_color || '#ef4444',
            color: 'white',
          }}
        >
          {menu.highlight_text}
        </span>
      )}
      {hasChildren && menu.is_expandable && (
        <svg
          className={cn(
            'w-5 h-5 transition-transform',
            isExpanded && 'rotate-180'
          )}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      )}
    </>
  )

  const linkClasses = cn(
    'flex items-center gap-3 px-4 py-3 transition-colors',
    isActive && 'bg-blue-600 text-white',
    !isActive && 'text-gray-800 active:bg-gray-100',
    menu.css_class
  )

  return (
    <div style={{ paddingLeft: `${level * 16}px` }}>
      {hasLink && menu.link_type === 'url' ? (
        <Link href={menu.link_url || '#'} className={linkClasses} onClick={handleClick}>
          {menuContent}
        </Link>
      ) : hasLink && menu.link_type === 'external' && menu.external_url ? (
        <a
          href={menu.external_url}
          target="_blank"
          rel="noopener noreferrer"
          className={linkClasses}
          onClick={handleClick}
        >
          {menuContent}
        </a>
      ) : (
        <button className={cn(linkClasses, 'w-full text-left')} onClick={handleClick}>
          {menuContent}
        </button>
      )}

      {/* 하위 메뉴 */}
      {hasChildren && isExpanded && (
        <div className="bg-gray-50">
          {menu.children!.map((child) => (
            <DrawerMenuItem
              key={child.id}
              menu={child}
              isActive={false}
              onNavigate={onNavigate}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export function MobileDrawer({ menuType, isOpen, onClose }: MobileDrawerProps) {
  const pathname = usePathname()
  const [menus, setMenus] = useState<Menu[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      const loadMenus = async () => {
        try {
          setLoading(true)
          setError('')
          const data = await getPublicMenus(menuType)

          // 활성화되고 표시 가능한 메뉴만 필터링
          const visibleMenus = data.filter(
            (menu) => menu.is_active && menu.is_visible && menu.is_enabled
          )

          setMenus(visibleMenus)
        } catch (err: any) {
          setError(err.message || '메뉴를 불러오는데 실패했습니다.')
          console.error('Error loading menus:', err)
        } finally {
          setLoading(false)
        }
      }

      loadMenus()
    }
  }, [menuType, isOpen])

  // 백드롭 클릭 시 닫기
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  // ESC 키로 닫기
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  // body 스크롤 잠금
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }

    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  const isMenuActive = (menu: Menu): boolean => {
    return pathname === menu.link_url
  }

  return (
    <>
      {/* 백드롭 */}
      <div
        className={cn(
          'fixed inset-0 bg-black/50 z-40 transition-opacity',
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        )}
        onClick={handleBackdropClick}
      />

      {/* 드로어 */}
      <div
        className={cn(
          'fixed top-0 left-0 bottom-0 w-80 max-w-[85vw] bg-white z-50 shadow-xl transition-transform transform',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* 헤더 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">메뉴</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
            aria-label="메뉴 닫기"
          >
            <svg
              className="w-6 h-6 text-gray-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* 메뉴 컨텐츠 */}
        <div className="overflow-y-auto h-[calc(100vh-65px)]">
          {loading ? (
            <div className="p-4 space-y-3">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="animate-pulse h-12 bg-gray-200 rounded"></div>
              ))}
            </div>
          ) : error ? (
            <div className="p-4">
              <div className="p-4 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                {error}
              </div>
            </div>
          ) : menus.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              메뉴가 없습니다
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {menus.map((menu) => (
                <DrawerMenuItem
                  key={menu.id}
                  menu={menu}
                  isActive={isMenuActive(menu)}
                  onNavigate={onClose}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  )
}

export default MobileDrawer
