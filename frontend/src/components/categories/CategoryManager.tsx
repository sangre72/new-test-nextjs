'use client'

import React, { useState, useEffect, useCallback } from 'react'
import {
  getCategoriesTree,
  getCategoriesFlat,
  getCategory,
  createCategory,
  updateCategory,
  deleteCategory,
  reorderCategory,
} from '@/lib/api/categories'
import type {
  Category,
  CategoryTree,
  CategoryCreateRequest,
  CategoryUpdateRequest,
  CategoryReorderRequest,
} from '@/types/category'
import CategoryTreeComponent from './CategoryTree'
import CategoryForm from './CategoryForm'

interface CategoryManagerProps {
  boardId: number
  tenantId: number
  boardName?: string
}

type FormMode = 'view' | 'create' | 'edit'

export function CategoryManager({
  boardId,
  tenantId,
  boardName,
}: CategoryManagerProps) {
  const [categories, setCategories] = useState<CategoryTree[]>([])
  const [categoriesFlat, setCategoriesFlat] = useState<Category[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null)
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set())
  const [formMode, setFormMode] = useState<FormMode>('view')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formError, setFormError] = useState('')

  // Fetch categories
  const fetchCategories = useCallback(async () => {
    try {
      setLoading(true)
      setError('')
      const [tree, flat] = await Promise.all([
        getCategoriesTree(boardId, tenantId),
        getCategoriesFlat(boardId, tenantId),
      ])
      setCategories(tree)
      setCategoriesFlat(flat)
    } catch (err) {
      setError('Failed to fetch categories')
      console.error('Error fetching categories:', err)
    } finally {
      setLoading(false)
    }
  }, [boardId, tenantId])

  // Initial load
  useEffect(() => {
    fetchCategories()
  }, [fetchCategories])

  // Load selected category details
  useEffect(() => {
    const loadCategory = async () => {
      if (selectedId && formMode !== 'create') {
        try {
          const category = await getCategory(selectedId, tenantId)
          setSelectedCategory(category)
        } catch (err) {
          console.error('Error loading category:', err)
        }
      } else if (formMode === 'create') {
        setSelectedCategory(null)
      }
    }
    loadCategory()
  }, [selectedId, formMode, tenantId])

  const handleSelectCategory = useCallback((id: number) => {
    setSelectedId(id)
    setFormMode('view')
  }, [])

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

  const handleCreateNew = () => {
    setSelectedId(null)
    setSelectedCategory(null)
    setFormMode('create')
    setFormError('')
  }

  const handleEdit = (id: number) => {
    setSelectedId(id)
    setFormMode('edit')
    setFormError('')
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this category?')) {
      return
    }

    try {
      setLoading(true)
      await deleteCategory(id, tenantId)
      await fetchCategories()
      setSelectedId(null)
      setFormMode('view')
    } catch (err: any) {
      setFormError(err.response?.data?.detail || 'Failed to delete category')
      console.error('Error deleting category:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitForm = async (data: CategoryCreateRequest | CategoryUpdateRequest) => {
    try {
      setLoading(true)
      setFormError('')

      if (formMode === 'create') {
        const createData = data as CategoryCreateRequest
        await createCategory({
          ...createData,
          tenant_id: tenantId,
          board_id: boardId,
        })
      } else if (formMode === 'edit' && selectedId) {
        await updateCategory(selectedId, tenantId, data as CategoryUpdateRequest)
      }

      await fetchCategories()
      setFormMode('view')
    } catch (err: any) {
      setFormError(err.response?.data?.detail || 'Failed to save category')
      console.error('Error saving category:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setFormMode('view')
    setFormError('')
  }

  const parentCategories = categoriesFlat.filter(
    (c) => !selectedCategory || c.id !== selectedCategory.id
  )

  return (
    <div className="flex gap-6 h-screen bg-gray-50">
      {/* Left Panel - Category Tree */}
      <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto p-4">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-1">
            Categories
          </h2>
          {boardName && (
            <p className="text-sm text-gray-600">{boardName}</p>
          )}
        </div>

        <button
          onClick={handleCreateNew}
          className="w-full mb-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 font-medium"
        >
          + New Category
        </button>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
            {error}
          </div>
        )}

        {loading && !categories.length ? (
          <div className="text-center text-gray-500">Loading...</div>
        ) : categories.length === 0 ? (
          <div className="text-center text-gray-500">
            No categories yet
          </div>
        ) : (
          <CategoryTreeComponent
            categories={categories}
            selectedId={selectedId}
            onSelect={handleSelectCategory}
            onEdit={handleEdit}
            onDelete={handleDelete}
            expandedIds={expandedIds}
            onToggleExpand={handleToggleExpand}
          />
        )}
      </div>

      {/* Right Panel - Form/Detail */}
      <div className="flex-1 overflow-y-auto p-6">
        {formMode === 'view' && !selectedId ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <p>Select a category or create a new one</p>
          </div>
        ) : formMode === 'view' && selectedCategory ? (
          <div className="max-w-2xl">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              {selectedCategory.category_name}
            </h2>

            <div className="bg-white rounded-lg shadow p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Code</p>
                  <p className="font-medium">{selectedCategory.category_code}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Status</p>
                  <p className="font-medium">
                    {selectedCategory.is_active ? 'Active' : 'Inactive'}
                  </p>
                </div>
              </div>

              {selectedCategory.description && (
                <div>
                  <p className="text-sm text-gray-600">Description</p>
                  <p>{selectedCategory.description}</p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Read Permission</p>
                  <p className="font-medium capitalize">{selectedCategory.read_permission}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Write Permission</p>
                  <p className="font-medium capitalize">{selectedCategory.write_permission}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Depth</p>
                  <p className="font-medium">{selectedCategory.depth}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Posts</p>
                  <p className="font-medium">{selectedCategory.post_count}</p>
                </div>
              </div>

              <div className="pt-4 flex gap-2">
                <button
                  onClick={() => handleEdit(selectedId!)}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(selectedId!)}
                  className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-2xl">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              {formMode === 'create' ? 'Create New Category' : 'Edit Category'}
            </h2>

            <div className="bg-white rounded-lg shadow p-6">
              <CategoryForm
                isEdit={formMode === 'edit'}
                category={selectedCategory}
                parentCategories={parentCategories}
                onSubmit={handleSubmitForm}
                onCancel={handleCancel}
                loading={loading}
                error={formError}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CategoryManager
