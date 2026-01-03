'use client'

/**
 * Menu Form Component
 * 메뉴 생성/수정 폼
 *
 * Security First: 입력 검증, XSS 방지
 * Error Handling First: 폼 검증 및 에러 표시
 */

import React, { useState, useEffect } from 'react'
import type {
  Menu,
  MenuFormData,
  LinkType,
  PermissionType,
  ShowCondition,
  BadgeType,
} from '@/types/menu'
import { validateMenuInput } from '@/lib/api/menus'

interface MenuFormProps {
  isEdit: boolean
  menu: Menu | null
  parentMenus: Menu[]
  parentIdForCreate?: number | null
  onSubmit: (data: MenuFormData) => Promise<void>
  onCancel: () => void
  loading: boolean
  error: string
}

const LINK_TYPES: { value: LinkType; label: string }[] = [
  { value: 'url', label: '내부 URL' },
  { value: 'external', label: '외부 URL' },
  { value: 'new_window', label: '새 창' },
  { value: 'modal', label: '모달' },
  { value: 'none', label: '링크 없음' },
]

const PERMISSION_TYPES: { value: PermissionType; label: string }[] = [
  { value: 'public', label: '전체 공개' },
  { value: 'member', label: '회원만' },
  { value: 'groups', label: '그룹별' },
  { value: 'users', label: '사용자별' },
  { value: 'roles', label: '역할별' },
  { value: 'admin', label: '관리자만' },
]

const SHOW_CONDITIONS: { value: ShowCondition; label: string }[] = [
  { value: 'always', label: '항상 표시' },
  { value: 'logged_in', label: '로그인 시' },
  { value: 'logged_out', label: '로그아웃 시' },
  { value: 'custom', label: '커스텀 조건' },
]

const BADGE_TYPES: { value: BadgeType; label: string }[] = [
  { value: 'none', label: '없음' },
  { value: 'count', label: '카운트' },
  { value: 'dot', label: '점' },
  { value: 'text', label: '텍스트' },
  { value: 'api', label: 'API' },
]

export function MenuForm({
  isEdit,
  menu,
  parentMenus,
  parentIdForCreate,
  onSubmit,
  onCancel,
  loading,
  error,
}: MenuFormProps) {
  const [formData, setFormData] = useState<MenuFormData>({
    menu_type: 'user',
    menu_name: '',
    menu_code: '',
    description: '',
    icon: '',
    link_type: 'url',
    link_url: '',
    external_url: '',
    permission_type: 'public',
    show_condition: 'always',
    sort_order: 0,
    is_visible: true,
    is_enabled: true,
    is_expandable: false,
    default_expanded: false,
    css_class: '',
    highlight: false,
    highlight_text: '',
    highlight_color: '#ef4444',
    badge_type: 'none',
    badge_value: '',
    badge_color: '#3b82f6',
  })

  const [validationErrors, setValidationErrors] = useState<string[]>([])

  // 수정 모드일 때 기존 데이터 로드
  useEffect(() => {
    if (isEdit && menu) {
      setFormData({
        menu_type: menu.menu_type,
        menu_name: menu.menu_name,
        menu_code: menu.menu_code,
        description: menu.description || '',
        icon: menu.icon || '',
        link_type: menu.link_type,
        link_url: menu.link_url || '',
        external_url: menu.external_url || '',
        permission_type: menu.permission_type,
        show_condition: menu.show_condition,
        sort_order: menu.sort_order,
        is_visible: menu.is_visible,
        is_enabled: menu.is_enabled,
        is_expandable: menu.is_expandable,
        default_expanded: menu.default_expanded,
        css_class: menu.css_class || '',
        highlight: menu.highlight,
        highlight_text: menu.highlight_text || '',
        highlight_color: menu.highlight_color || '#ef4444',
        badge_type: menu.badge_type || 'none',
        badge_value: menu.badge_value || '',
        badge_color: menu.badge_color || '#3b82f6',
      })
    } else if (!isEdit) {
      // 생성 모드일 때 부모 ID 설정
      setFormData((prev) => ({
        ...prev,
        parent_id: parentIdForCreate,
      }))
    }
  }, [isEdit, menu, parentIdForCreate])

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked
      setFormData((prev) => ({ ...prev, [name]: checked }))
    } else if (type === 'number') {
      setFormData((prev) => ({ ...prev, [name]: parseInt(value) || 0 }))
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // 클라이언트 검증
    const errors = validateMenuInput(formData)
    if (errors.length > 0) {
      setValidationErrors(errors)
      return
    }

    setValidationErrors([])
    await onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* 에러 메시지 */}
      {(error || validationErrors.length > 0) && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm font-semibold text-red-800 mb-2">입력 오류</p>
          {error && <p className="text-sm text-red-700">{error}</p>}
          {validationErrors.map((err, idx) => (
            <p key={idx} className="text-sm text-red-700">
              • {err}
            </p>
          ))}
        </div>
      )}

      {/* 기본 정보 */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">기본 정보</h3>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="menu_name" className="block text-sm font-medium text-gray-700 mb-1">
              메뉴 이름 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="menu_name"
              name="menu_name"
              value={formData.menu_name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="예: 회원 정보"
            />
          </div>

          <div>
            <label htmlFor="menu_code" className="block text-sm font-medium text-gray-700 mb-1">
              메뉴 코드 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="menu_code"
              name="menu_code"
              value={formData.menu_code}
              onChange={handleChange}
              required
              disabled={isEdit}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              placeholder="예: member_info"
            />
            <p className="mt-1 text-xs text-gray-500">영문, 숫자, 언더스코어만 가능</p>
          </div>
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            설명
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="메뉴 설명을 입력하세요"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="icon" className="block text-sm font-medium text-gray-700 mb-1">
              아이콘
            </label>
            <input
              type="text"
              id="icon"
              name="icon"
              value={formData.icon}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="예: 🏠"
            />
            <p className="mt-1 text-xs text-gray-500">이모지 또는 아이콘 클래스</p>
          </div>

          <div>
            <label htmlFor="sort_order" className="block text-sm font-medium text-gray-700 mb-1">
              정렬 순서
            </label>
            <input
              type="number"
              id="sort_order"
              name="sort_order"
              value={formData.sort_order}
              onChange={handleChange}
              min="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* 링크 설정 */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">링크 설정</h3>

        <div>
          <label htmlFor="link_type" className="block text-sm font-medium text-gray-700 mb-1">
            링크 타입
          </label>
          <select
            id="link_type"
            name="link_type"
            value={formData.link_type}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {LINK_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {formData.link_type === 'url' && (
          <div>
            <label htmlFor="link_url" className="block text-sm font-medium text-gray-700 mb-1">
              URL
            </label>
            <input
              type="text"
              id="link_url"
              name="link_url"
              value={formData.link_url}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="/mypage/profile"
            />
          </div>
        )}

        {formData.link_type === 'external' && (
          <div>
            <label htmlFor="external_url" className="block text-sm font-medium text-gray-700 mb-1">
              외부 URL
            </label>
            <input
              type="url"
              id="external_url"
              name="external_url"
              value={formData.external_url}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://example.com"
            />
          </div>
        )}
      </div>

      {/* 권한 설정 */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">권한 설정</h3>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="permission_type" className="block text-sm font-medium text-gray-700 mb-1">
              권한 타입
            </label>
            <select
              id="permission_type"
              name="permission_type"
              value={formData.permission_type}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {PERMISSION_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="show_condition" className="block text-sm font-medium text-gray-700 mb-1">
              표시 조건
            </label>
            <select
              id="show_condition"
              name="show_condition"
              value={formData.show_condition}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {SHOW_CONDITIONS.map((condition) => (
                <option key={condition.value} value={condition.value}>
                  {condition.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 표시 옵션 */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">표시 옵션</h3>

        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_visible"
              name="is_visible"
              checked={formData.is_visible}
              onChange={handleChange}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="is_visible" className="ml-2 text-sm text-gray-700">
              메뉴 표시
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_enabled"
              name="is_enabled"
              checked={formData.is_enabled}
              onChange={handleChange}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="is_enabled" className="ml-2 text-sm text-gray-700">
              활성화
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_expandable"
              name="is_expandable"
              checked={formData.is_expandable}
              onChange={handleChange}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="is_expandable" className="ml-2 text-sm text-gray-700">
              확장 가능
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="default_expanded"
              name="default_expanded"
              checked={formData.default_expanded}
              onChange={handleChange}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="default_expanded" className="ml-2 text-sm text-gray-700">
              기본 펼침
            </label>
          </div>
        </div>
      </div>

      {/* 강조 표시 */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">강조 표시</h3>

        <div className="flex items-center mb-2">
          <input
            type="checkbox"
            id="highlight"
            name="highlight"
            checked={formData.highlight}
            onChange={handleChange}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <label htmlFor="highlight" className="ml-2 text-sm text-gray-700">
            강조 표시 사용
          </label>
        </div>

        {formData.highlight && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="highlight_text" className="block text-sm font-medium text-gray-700 mb-1">
                강조 텍스트
              </label>
              <input
                type="text"
                id="highlight_text"
                name="highlight_text"
                value={formData.highlight_text}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="NEW"
              />
            </div>

            <div>
              <label htmlFor="highlight_color" className="block text-sm font-medium text-gray-700 mb-1">
                강조 색상
              </label>
              <input
                type="color"
                id="highlight_color"
                name="highlight_color"
                value={formData.highlight_color}
                onChange={handleChange}
                className="w-full h-10 px-1 py-1 border border-gray-300 rounded-md"
              />
            </div>
          </div>
        )}
      </div>

      {/* 배지 */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">배지</h3>

        <div>
          <label htmlFor="badge_type" className="block text-sm font-medium text-gray-700 mb-1">
            배지 타입
          </label>
          <select
            id="badge_type"
            name="badge_type"
            value={formData.badge_type}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {BADGE_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {formData.badge_type !== 'none' && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="badge_value" className="block text-sm font-medium text-gray-700 mb-1">
                배지 값
              </label>
              <input
                type="text"
                id="badge_value"
                name="badge_value"
                value={formData.badge_value}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="3"
              />
            </div>

            <div>
              <label htmlFor="badge_color" className="block text-sm font-medium text-gray-700 mb-1">
                배지 색상
              </label>
              <input
                type="color"
                id="badge_color"
                name="badge_color"
                value={formData.badge_color}
                onChange={handleChange}
                className="w-full h-10 px-1 py-1 border border-gray-300 rounded-md"
              />
            </div>
          </div>
        )}
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-3 pt-4 border-t border-gray-200">
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? '저장 중...' : isEdit ? '수정' : '추가'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
        >
          취소
        </button>
      </div>
    </form>
  )
}

export default MenuForm
