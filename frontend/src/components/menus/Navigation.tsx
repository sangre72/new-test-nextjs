'use client'

/**
 * Navigation Component
 * 반응형 네비게이션 (Desktop/Mobile)
 *
 * Security First: XSS 방지, 안전한 URL 처리
 * Error Handling First: 에러 처리 및 폴백
 */

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import type { Menu, MenuType } from '@/types/menu'
import { getPublicMenus, isSafeUrl } from '@/lib/api/menus'
import { cn } from '@/lib/utils'

interface NavigationProps {
  menuType: MenuType
  className?: string
}

interface NavigationItemProps {
  menu: Menu
  isActive: boolean
  isMobile?: boolean
  onNavigate?: () => void
}

function NavigationItem({ menu, isActive, isMobile, onNavigate }: NavigationItemProps) {
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

    // 모바일에서는 클릭 시 메뉴 닫기
    if (isMobile && onNavigate) {
      onNavigate()
    }
  }

  const menuContent = (
    <>
      {menu.icon && <span className="text-lg">{menu.icon}</span>}
      <span className="flex-1">{menu.menu_name}</span>
      {menu.badge_type !== 'none' && menu.badge_value && (
        <span
          className="px-2 py-0.5 text-xs rounded-full"
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
          className="px-2 py-0.5 text-xs font-semibold rounded"
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
            'w-4 h-4 transition-transform',
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
    'flex items-center gap-2 px-4 py-2 rounded-md transition-colors',
    isActive && 'bg-blue-100 text-blue-900 font-semibold',
    !isActive && 'text-gray-700 hover:bg-gray-100',
    menu.css_class
  )

  return (
    <li>
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
        <button className={linkClasses} onClick={handleClick}>
          {menuContent}
        </button>
      )}

      {/* 하위 메뉴 */}
      {hasChildren && isExpanded && (
        <ul className="ml-4 mt-1 space-y-1">
          {menu.children!.map((child) => (
            <NavigationItem
              key={child.id}
              menu={child}
              isActive={false}
              isMobile={isMobile}
              onNavigate={onNavigate}
            />
          ))}
        </ul>
      )}
    </li>
  )
}

export function Navigation({ menuType, className }: NavigationProps) {
  const pathname = usePathname()
  const [menus, setMenus] = useState<Menu[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
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
  }, [menuType])

  const isMenuActive = (menu: Menu): boolean => {
    return pathname === menu.link_url
  }

  if (loading) {
    return (
      <nav className={className}>
        <div className="animate-pulse space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-10 bg-gray-200 rounded"></div>
          ))}
        </div>
      </nav>
    )
  }

  if (error) {
    return (
      <nav className={className}>
        <div className="p-4 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {error}
        </div>
      </nav>
    )
  }

  if (menus.length === 0) {
    return null
  }

  return (
    <nav className={className}>
      <ul className="space-y-1">
        {menus.map((menu) => (
          <NavigationItem
            key={menu.id}
            menu={menu}
            isActive={isMenuActive(menu)}
          />
        ))}
      </ul>
    </nav>
  )
}

export default Navigation
