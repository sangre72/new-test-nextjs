'use client'

import React, { useState, useEffect } from 'react'
import type { Category, CategoryCreateRequest, CategoryUpdateRequest } from '@/types/category'

interface CategoryFormProps {
  isEdit?: boolean
  category?: Category | null
  parentCategories?: Category[]
  onSubmit: (data: CategoryCreateRequest | CategoryUpdateRequest) => Promise<void>
  onCancel?: () => void
  loading?: boolean
  error?: string
}

export function CategoryForm({
  isEdit = false,
  category = null,
  parentCategories = [],
  onSubmit,
  onCancel,
  loading = false,
  error = '',
}: CategoryFormProps) {
  const [formData, setFormData] = useState<any>({
    category_name: '',
    category_code: '',
    description: '',
    parent_id: null,
    sort_order: 0,
    icon: '',
    color: '#3B82F6',
    read_permission: 'all',
    write_permission: 'all',
    is_active: true,
  })

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    if (isEdit && category) {
      setFormData({
        category_name: category.category_name || '',
        category_code: category.category_code || '',
        description: category.description || '',
        parent_id: category.parent_id || null,
        sort_order: category.sort_order || 0,
        icon: category.icon || '',
        color: category.color || '#3B82F6',
        read_permission: category.read_permission || 'all',
        write_permission: category.write_permission || 'all',
        is_active: category.is_active !== false,
      })
    }
  }, [isEdit, category])

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {}

    if (!formData.category_name.trim()) {
      errors.category_name = 'Category name is required'
    }

    if (!formData.category_code.trim()) {
      errors.category_code = 'Category code is required'
    } else if (!/^[a-z0-9_]+$/.test(formData.category_code)) {
      errors.category_code = 'Only lowercase letters, numbers, and underscores allowed'
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    try {
      await onSubmit(formData)
    } catch (err) {
      console.error('Form submission error:', err)
    }
  }

  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (validationErrors[field]) {
      setValidationErrors((prev) => {
        const next = { ...prev }
        delete next[field]
        return next
      })
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Category Code *
        </label>
        <input
          type="text"
          value={formData.category_code}
          onChange={(e) => handleChange('category_code', e.target.value.toLowerCase())}
          disabled={isEdit}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            validationErrors.category_code ? 'border-red-500' : 'border-gray-300'
          } ${isEdit ? 'bg-gray-100' : ''}`}
          placeholder="lowercase_only"
        />
        {validationErrors.category_code && (
          <p className="text-red-500 text-sm mt-1">{validationErrors.category_code}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Category Name *
        </label>
        <input
          type="text"
          value={formData.category_name}
          onChange={(e) => handleChange('category_name', e.target.value)}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            validationErrors.category_name ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Enter category name"
        />
        {validationErrors.category_name && (
          <p className="text-red-500 text-sm mt-1">{validationErrors.category_name}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Parent Category
        </label>
        <select
          value={formData.parent_id || ''}
          onChange={(e) => handleChange('parent_id', e.target.value ? parseInt(e.target.value) : null)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">None (Root Level)</option>
          {parentCategories
            .filter((c) => !isEdit || c.id !== category?.id)
            .map((c) => (
              <option key={c.id} value={c.id}>
                {'  '.repeat(c.depth)}{c.category_name}
              </option>
            ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter category description"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Color
          </label>
          <input
            type="color"
            value={formData.color}
            onChange={(e) => handleChange('color', e.target.value)}
            className="w-full h-10 rounded-md border border-gray-300 cursor-pointer"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Icon
          </label>
          <input
            type="text"
            value={formData.icon}
            onChange={(e) => handleChange('icon', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., folder, star"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Read Permission
          </label>
          <select
            value={formData.read_permission}
            onChange={(e) => handleChange('read_permission', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Everyone</option>
            <option value="members">Members Only</option>
            <option value="admin">Admin Only</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Write Permission
          </label>
          <select
            value={formData.write_permission}
            onChange={(e) => handleChange('write_permission', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Everyone</option>
            <option value="members">Members Only</option>
            <option value="admin">Admin Only</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Sort Order
          </label>
          <input
            type="number"
            value={formData.sort_order}
            onChange={(e) => handleChange('sort_order', parseInt(e.target.value) || 0)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {isEdit && (
          <div className="flex items-end">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => handleChange('is_active', e.target.checked)}
                className="rounded"
              />
              <span className="text-sm font-medium text-gray-700">Active</span>
            </label>
          </div>
        )}
      </div>

      <div className="flex gap-2 justify-end pt-4">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
            disabled={loading}
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-blue-300"
          disabled={loading}
        >
          {loading ? 'Saving...' : isEdit ? 'Update' : 'Create'}
        </button>
      </div>
    </form>
  )
}

export default CategoryForm
