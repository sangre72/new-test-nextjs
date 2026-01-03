/**
 * Admin Menu Management Page
 * 관리자 메뉴 관리 페이지
 */

import { MenuManager } from '@/components/menus'

export default function AdminMenusPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-6">
        <MenuManager
          menuType="user"
          title="사용자 메뉴 관리"
        />
      </div>
    </div>
  )
}
