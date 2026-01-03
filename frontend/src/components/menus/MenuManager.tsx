'use client'

/**
 * Menu Manager Component
 * 메뉴 관리 메인 컴포넌트
 *
 * Security First: XSS 방지, 안전한 렌더링
 * Error Handling First: 모든 API 호출에 에러 처리
 */

import React, { useState, useEffect, useCallback } from 'react'
import {
  getAllMenus,
  createMenu,
  updateMenu,
  deleteMenu,
  moveMenu,
} from '@/lib/api/menus'
import type {
  Menu,
  MenuTree,
  MenuFormData,
  MenuType,
} from '@/types/menu'
import MenuTreeComponent from './MenuTree'
import MenuForm from './MenuForm'

interface MenuManagerProps {
  menuType: MenuType
  title?: string
}

type FormMode = 'view' | 'create' | 'edit'

// 트리 → flat list 변환 헬퍼
const flattenMenuTree = (menuList: Menu[]): Menu[] => {
  const result: Menu[] = []
  const flatten = (items: Menu[]) => {
    items.forEach((item) => {
      result.push(item)
      if (item.children?.length) {
        flatten(item.children)
      }
    })
  }
  flatten(menuList)
  return result
}

// flat list → 트리 변환 헬퍼
const buildMenuTree = (flatMenus: Menu[]): MenuTree[] => {
  const menuMap = new Map<number, MenuTree>()
  const rootMenus: MenuTree[] = []

  // 먼저 모든 메뉴를 Map에 저장
  flatMenus.forEach((menu) => {
    menuMap.set(menu.id, { ...menu, children: [] })
  })

  // 부모-자식 관계 설정
  flatMenus.forEach((menu) => {
    const menuNode = menuMap.get(menu.id)!
    if (menu.parent_id === null) {
      rootMenus.push(menuNode)
    } else {
      const parent = menuMap.get(menu.parent_id)
      if (parent) {
        parent.children = parent.children || []
        parent.children.push(menuNode)
      }
    }
  })

  // 정렬
  const sortMenus = (menus: MenuTree[]) => {
    menus.sort((a, b) => a.sort_order - b.sort_order)
    menus.forEach((menu) => {
      if (menu.children?.length) sortMenus(menu.children)
    })
  }

  sortMenus(rootMenus)
  return rootMenus
}

export function MenuManager({ menuType, title }: MenuManagerProps) {
  const [menus, setMenus] = useState<MenuTree[]>([])
  const [flatMenus, setFlatMenus] = useState<Menu[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [selectedMenu, setSelectedMenu] = useState<Menu | null>(null)
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set())
  const [formMode, setFormMode] = useState<FormMode>('view')
  const [parentIdForCreate, setParentIdForCreate] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formError, setFormError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  // 메뉴 로드
  const fetchMenus = useCallback(async () => {
    try {
      setLoading(true)
      setError('')

      const data = await getAllMenus(menuType)
      const treeData = buildMenuTree(data)
      setMenus(treeData)
      setFlatMenus(flattenMenuTree(treeData))
    } catch (err: any) {
      setError(err.message || '메뉴 목록을 불러오는데 실패했습니다.')
      console.error('Error fetching menus:', err)
    } finally {
      setLoading(false)
    }
  }, [menuType])

  // 초기 로드
  useEffect(() => {
    fetchMenus()
  }, [fetchMenus])

  // 선택된 메뉴 상세 로드
  useEffect(() => {
    if (selectedId && formMode !== 'create') {
      const menu = flatMenus.find((m) => m.id === selectedId)
      setSelectedMenu(menu || null)
    } else if (formMode === 'create') {
      setSelectedMenu(null)
    }
  }, [selectedId, formMode, flatMenus])

  // 메뉴 선택
  const handleSelectMenu = useCallback((id: number) => {
    setSelectedId(id)
    setFormMode('view')
    setFormError('')
  }, [])

  // 확장/축소 토글
  const handleToggleExpand = useCallback((id: number) => {
    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }, [])

  // 새 메뉴 추가 (루트 또는 하위)
  const handleCreateNew = (parentId: number | null = null) => {
    setSelectedId(null)
    setSelectedMenu(null)
    setParentIdForCreate(parentId)
    setFormMode('create')
    setFormError('')
  }

  // 편집 모드
  const handleEdit = (id: number) => {
    setSelectedId(id)
    setFormMode('edit')
    setFormError('')
  }

  // 삭제
  const handleDelete = async (id: number) => {
    if (!window.confirm('선택한 메뉴를 삭제하시겠습니까?\n하위 메뉴도 함께 삭제됩니다.')) {
      return
    }

    try {
      setLoading(true)
      await deleteMenu(id)
      setSuccessMessage('메뉴가 삭제되었습니다.')
      await fetchMenus()
      setSelectedId(null)
      setFormMode('view')

      // 성공 메시지 3초 후 제거
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (err: any) {
      setFormError(err.message || '메뉴 삭제에 실패했습니다.')
      console.error('Error deleting menu:', err)
    } finally {
      setLoading(false)
    }
  }

  // 메뉴 이동 (드래그&드롭)
  const handleMoveMenu = async (menuId: number, newParentId: number | null, newIndex: number) => {
    try {
      await moveMenu(menuId, newParentId, newIndex)
      setSuccessMessage('메뉴가 이동되었습니다.')
      await fetchMenus()

      // 성공 메시지 3초 후 제거
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (err: any) {
      setError(err.message || '메뉴 이동에 실패했습니다.')
      console.error('Error moving menu:', err)
    }
  }

  // 폼 제출
  const handleSubmitForm = async (data: MenuFormData) => {
    try {
      setLoading(true)
      setFormError('')

      if (formMode === 'create') {
        await createMenu({
          ...data,
          menu_type: menuType,
          parent_id: parentIdForCreate,
        })
        setSuccessMessage('메뉴가 추가되었습니다.')
      } else if (formMode === 'edit' && selectedId) {
        await updateMenu(selectedId, data)
        setSuccessMessage('메뉴가 수정되었습니다.')
      }

      await fetchMenus()
      setFormMode('view')
      setParentIdForCreate(null)

      // 성공 메시지 3초 후 제거
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (err: any) {
      setFormError(err.message || '저장 중 오류가 발생했습니다.')
      console.error('Error saving menu:', err)
    } finally {
      setLoading(false)
    }
  }

  // 취소
  const handleCancel = () => {
    setFormMode('view')
    setFormError('')
    setParentIdForCreate(null)
  }

  // 부모 메뉴 목록 (자기 자신 제외)
  const parentMenus = flatMenus.filter(
    (m) => !selectedMenu || m.id !== selectedMenu.id
  )

  return (
    <div className="flex gap-0 h-[calc(100vh-180px)] bg-gray-50">
      {/* Left Panel - Menu Tree */}
      <div className="w-96 bg-white border-r border-gray-200 overflow-y-auto">
        <div className="p-4 border-b border-gray-200 sticky top-0 bg-white z-10">
          <h2 className="text-lg font-semibold text-gray-900 mb-1">
            {title || '메뉴 관리'}
          </h2>
          <p className="text-sm text-gray-600">
            메뉴 구조를 관리합니다
          </p>

          <button
            onClick={() => handleCreateNew(null)}
            className="w-full mt-3 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium transition-colors"
          >
            + 최상위 메뉴 추가
          </button>
        </div>

        <div className="p-4">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded text-sm">
              {error}
            </div>
          )}

          {successMessage && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded text-sm">
              {successMessage}
            </div>
          )}

          {loading && !menus.length ? (
            <div className="text-center text-gray-500 py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2">로딩 중...</p>
            </div>
          ) : menus.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <p>등록된 메뉴가 없습니다</p>
              <p className="text-sm mt-1">상단 버튼으로 메뉴를 추가하세요</p>
            </div>
          ) : (
            <MenuTreeComponent
              menus={menus}
              selectedId={selectedId}
              onSelect={handleSelectMenu}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onCreateChild={handleCreateNew}
              onMove={handleMoveMenu}
              expandedIds={expandedIds}
              onToggleExpand={handleToggleExpand}
            />
          )}
        </div>
      </div>

      {/* Right Panel - Form/Detail */}
      <div className="flex-1 overflow-y-auto bg-white">
        {formMode === 'view' && !selectedId ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
              <p className="mt-2">메뉴를 선택하거나 새로 생성하세요</p>
            </div>
          </div>
        ) : formMode === 'view' && selectedMenu ? (
          <div className="p-6">
            <div className="max-w-3xl mx-auto">
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  {selectedMenu.icon && (
                    <span className="text-3xl">{selectedMenu.icon}</span>
                  )}
                  {selectedMenu.menu_name}
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  코드: {selectedMenu.menu_code}
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-6 space-y-6">
                {/* 기본 정보 */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">기본 정보</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">메뉴 타입</p>
                      <p className="font-medium">{selectedMenu.menu_type}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">상태</p>
                      <p className="font-medium">
                        {selectedMenu.is_active ? (
                          <span className="text-green-600">활성</span>
                        ) : (
                          <span className="text-red-600">비활성</span>
                        )}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">표시 여부</p>
                      <p className="font-medium">
                        {selectedMenu.is_visible ? '표시' : '숨김'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">활성화</p>
                      <p className="font-medium">
                        {selectedMenu.is_enabled ? '활성' : '비활성'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* 설명 */}
                {selectedMenu.description && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">설명</h3>
                    <p className="text-gray-900">{selectedMenu.description}</p>
                  </div>
                )}

                {/* 링크 정보 */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">링크 정보</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">링크 타입</p>
                      <p className="font-medium">{selectedMenu.link_type}</p>
                    </div>
                    {selectedMenu.link_url && (
                      <div>
                        <p className="text-sm text-gray-600">URL</p>
                        <p className="font-medium text-blue-600 break-all">
                          {selectedMenu.link_url}
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* 권한 정보 */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">권한 정보</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">권한 타입</p>
                      <p className="font-medium">{selectedMenu.permission_type}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">표시 조건</p>
                      <p className="font-medium">{selectedMenu.show_condition}</p>
                    </div>
                  </div>
                </div>

                {/* 계층 정보 */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">계층 정보</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">깊이</p>
                      <p className="font-medium">{selectedMenu.depth}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">정렬 순서</p>
                      <p className="font-medium">{selectedMenu.sort_order}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">경로</p>
                      <p className="font-medium text-sm break-all">{selectedMenu.path}</p>
                    </div>
                  </div>
                </div>

                {/* 액션 버튼 */}
                <div className="pt-4 flex gap-2">
                  <button
                    onClick={() => handleEdit(selectedId!)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                  >
                    수정
                  </button>
                  <button
                    onClick={() => handleDelete(selectedId!)}
                    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                  >
                    삭제
                  </button>
                  <button
                    onClick={() => handleCreateNew(selectedId)}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                  >
                    하위 메뉴 추가
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-6">
            <div className="max-w-3xl mx-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                {formMode === 'create' ? '새 메뉴 추가' : '메뉴 수정'}
              </h2>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <MenuForm
                  isEdit={formMode === 'edit'}
                  menu={selectedMenu}
                  parentMenus={parentMenus}
                  parentIdForCreate={parentIdForCreate}
                  onSubmit={handleSubmitForm}
                  onCancel={handleCancel}
                  loading={loading}
                  error={formError}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default MenuManager
