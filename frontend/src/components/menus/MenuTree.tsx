'use client'

/**
 * Menu Tree Component
 * 트리 형태 메뉴 표시 컴포넌트 (드래그&드롭 지원)
 *
 * Security First: XSS 방지, 안전한 렌더링
 * Error Handling First: 에러 처리 및 사용자 피드백
 */

import React, { useState } from 'react'
import type { MenuTree } from '@/types/menu'
import { cn } from '@/lib/utils'

interface MenuTreeProps {
  menus: MenuTree[]
  selectedId: number | null
  onSelect: (id: number) => void
  onEdit: (id: number) => void
  onDelete: (id: number) => void
  onCreateChild: (parentId: number) => void
  onMove: (menuId: number, newParentId: number | null, newIndex: number) => void
  expandedIds: Set<number>
  onToggleExpand: (id: number) => void
}

interface MenuItemProps {
  menu: MenuTree
  level: number
  selectedId: number | null
  onSelect: (id: number) => void
  onEdit: (id: number) => void
  onDelete: (id: number) => void
  onCreateChild: (parentId: number) => void
  onMove: (menuId: number, newParentId: number | null, newIndex: number) => void
  isExpanded: boolean
  onToggleExpand: (id: number) => void
  expandedIds: Set<number>
}

function MenuItem({
  menu,
  level,
  selectedId,
  onSelect,
  onEdit,
  onDelete,
  onCreateChild,
  onMove,
  isExpanded,
  onToggleExpand,
  expandedIds,
}: MenuItemProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isDragOver, setIsDragOver] = useState(false)
  const [showActions, setShowActions] = useState(false)

  const hasChildren = menu.children && menu.children.length > 0
  const isSelected = menu.id === selectedId

  // 드래그 시작
  const handleDragStart = (e: React.DragEvent) => {
    e.stopPropagation()
    setIsDragging(true)
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('menuId', menu.id.toString())
  }

  // 드래그 종료
  const handleDragEnd = (e: React.DragEvent) => {
    e.stopPropagation()
    setIsDragging(false)
  }

  // 드래그 오버
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
    e.dataTransfer.dropEffect = 'move'
  }

  // 드래그 떠남
  const handleDragLeave = (e: React.DragEvent) => {
    e.stopPropagation()
    setIsDragOver(false)
  }

  // 드롭
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)

    const draggedMenuId = parseInt(e.dataTransfer.getData('menuId'))
    if (draggedMenuId && draggedMenuId !== menu.id) {
      // 자기 자신에게 드롭하지 않음
      onMove(draggedMenuId, menu.id, 0)
    }
  }

  return (
    <div className="select-none">
      <div
        draggable
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onMouseEnter={() => setShowActions(true)}
        onMouseLeave={() => setShowActions(false)}
        className={cn(
          'group flex items-center gap-1 py-1.5 px-2 rounded-md cursor-pointer transition-colors',
          isSelected && 'bg-blue-100 text-blue-900',
          !isSelected && 'hover:bg-gray-100',
          isDragging && 'opacity-50',
          isDragOver && 'bg-blue-50 border-2 border-blue-400 border-dashed'
        )}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
      >
        {/* 확장/축소 버튼 */}
        {hasChildren ? (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onToggleExpand(menu.id)
            }}
            className="flex-shrink-0 w-5 h-5 flex items-center justify-center text-gray-500 hover:text-gray-700"
          >
            {isExpanded ? (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            )}
          </button>
        ) : (
          <span className="flex-shrink-0 w-5 h-5" />
        )}

        {/* 아이콘 */}
        {menu.icon && (
          <span className="flex-shrink-0 text-lg">{menu.icon}</span>
        )}

        {/* 메뉴 이름 */}
        <div
          onClick={() => onSelect(menu.id)}
          className="flex-1 min-w-0"
        >
          <div className="flex items-center gap-2">
            <span className={cn(
              'font-medium truncate',
              !menu.is_visible && 'text-gray-400 line-through',
              !menu.is_enabled && 'text-gray-500 italic'
            )}>
              {menu.menu_name}
            </span>
            {menu.highlight && (
              <span className="flex-shrink-0 px-1.5 py-0.5 text-xs font-semibold rounded"
                style={{
                  backgroundColor: menu.highlight_color || '#ef4444',
                  color: 'white',
                }}>
                {menu.highlight_text || 'NEW'}
              </span>
            )}
            {menu.badge_type !== 'none' && menu.badge_value && (
              <span className="flex-shrink-0 px-1.5 py-0.5 text-xs rounded-full"
                style={{
                  backgroundColor: menu.badge_color || '#3b82f6',
                  color: 'white',
                }}>
                {menu.badge_value}
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500 truncate">{menu.menu_code}</p>
        </div>

        {/* 액션 버튼 (호버 시 표시) */}
        {showActions && (
          <div className="flex-shrink-0 flex items-center gap-1">
            <button
              onClick={(e) => {
                e.stopPropagation()
                onCreateChild(menu.id)
              }}
              className="p-1 rounded hover:bg-blue-100 text-blue-600"
              title="하위 메뉴 추가"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation()
                onEdit(menu.id)
              }}
              className="p-1 rounded hover:bg-yellow-100 text-yellow-600"
              title="수정"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation()
                onDelete(menu.id)
              }}
              className="p-1 rounded hover:bg-red-100 text-red-600"
              title="삭제"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        )}

        {/* 드래그 핸들 */}
        <div className="flex-shrink-0 w-4 text-gray-400 opacity-0 group-hover:opacity-100">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
          </svg>
        </div>
      </div>

      {/* 하위 메뉴 */}
      {hasChildren && isExpanded && (
        <div>
          {menu.children!.map((child) => (
            <MenuItem
              key={child.id}
              menu={child}
              level={level + 1}
              selectedId={selectedId}
              onSelect={onSelect}
              onEdit={onEdit}
              onDelete={onDelete}
              onCreateChild={onCreateChild}
              onMove={onMove}
              isExpanded={expandedIds.has(child.id)}
              onToggleExpand={onToggleExpand}
              expandedIds={expandedIds}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export function MenuTree({
  menus,
  selectedId,
  onSelect,
  onEdit,
  onDelete,
  onCreateChild,
  onMove,
  expandedIds,
  onToggleExpand,
}: MenuTreeProps) {
  return (
    <div className="space-y-0.5">
      {menus.map((menu) => (
        <MenuItem
          key={menu.id}
          menu={menu}
          level={0}
          selectedId={selectedId}
          onSelect={onSelect}
          onEdit={onEdit}
          onDelete={onDelete}
          onCreateChild={onCreateChild}
          onMove={onMove}
          isExpanded={expandedIds.has(menu.id)}
          onToggleExpand={onToggleExpand}
          expandedIds={expandedIds}
        />
      ))}
    </div>
  )
}

export default MenuTree
