'use client'

import React, { useState } from 'react'
import type { CategoryTree } from '@/types/category'

interface CategoryTreeProps {
  categories: CategoryTree[]
  selectedId?: number | null
  onSelect?: (id: number) => void
  onEdit?: (id: number) => void
  onDelete?: (id: number) => void
  expandedIds?: Set<number>
  onToggleExpand?: (id: number) => void
}

export function CategoryTreeComponent({
  categories,
  selectedId = null,
  onSelect,
  onEdit,
  onDelete,
  expandedIds = new Set(),
  onToggleExpand,
}: CategoryTreeProps) {
  const renderCategories = (items: CategoryTree[], depth: number = 0) => {
    return (
      <ul
        className="list-none p-0 m-0"
        style={{ marginLeft: `${depth * 16}px` }}
      >
        {items.map((category) => {
          const isExpanded = expandedIds.has(category.id)
          const hasChildren = category.children && category.children.length > 0
          const isSelected = selectedId === category.id

          return (
            <li key={category.id} className="py-1">
              <div
                className={`flex items-center gap-2 px-3 py-2 rounded cursor-pointer transition-colors ${
                  isSelected
                    ? 'bg-blue-100 border-l-4 border-blue-500'
                    : 'hover:bg-gray-100'
                }`}
              >
                {hasChildren && (
                  <button
                    className="flex-shrink-0 w-6 h-6 flex items-center justify-center hover:bg-gray-200 rounded"
                    onClick={() => onToggleExpand?.(category.id)}
                  >
                    <span className="text-sm">
                      {isExpanded ? '▼' : '▶'}
                    </span>
                  </button>
                )}
                {!hasChildren && <div className="w-6" />}

                {category.color && (
                  <div
                    className="flex-shrink-0 w-3 h-3 rounded-full"
                    style={{ backgroundColor: category.color }}
                    title={category.color}
                  />
                )}

                <span
                  className={`flex-1 ${
                    category.is_active ? 'text-gray-900' : 'text-gray-400'
                  }`}
                  onClick={() => onSelect?.(category.id)}
                >
                  {category.category_name}
                </span>

                {category.post_count > 0 && (
                  <span className="text-xs bg-gray-200 px-2 py-1 rounded">
                    {category.post_count}
                  </span>
                )}

                <div className="flex-shrink-0 flex gap-1">
                  <button
                    className="text-xs bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
                    onClick={() => onEdit?.(category.id)}
                  >
                    Edit
                  </button>
                  <button
                    className="text-xs bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600"
                    onClick={() => onDelete?.(category.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>

              {hasChildren && isExpanded && (
                renderCategories(category.children!, depth + 1)
              )}
            </li>
          )
        })}
      </ul>
    )
  }

  return <div className="category-tree">{renderCategories(categories)}</div>
}

export default CategoryTreeComponent
