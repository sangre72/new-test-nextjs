'use client'

/**
 * Tenant Manager Component
 * Admin panel for managing tenants (CRUD operations)
 */

import React, { useState, useCallback } from 'react'
import {
  fetchTenants,
  createTenant,
  updateTenant,
  deleteTenant,
  fetchTenant,
} from '@/lib/api/tenants'
import type {
  Tenant,
  CreateTenantRequest,
  UpdateTenantRequest,
  TenantSettings,
} from '@/types/tenant'

interface TenantFormData extends CreateTenantRequest {}

/**
 * Tenant List Section
 */
function TenantList({
  tenants,
  selectedId,
  onSelect,
  onAddNew,
  isLoading,
}: {
  tenants: Tenant[]
  selectedId: number | null
  onSelect: (id: number) => void
  onAddNew: () => void
  isLoading: boolean
}) {
  const [searchTerm, setSearchTerm] = useState('')

  const filtered = tenants.filter(
    (t) =>
      t.tenant_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.tenant_code.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="w-80 border-r border-gray-200 flex flex-col h-screen">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Tenants</h2>
          <button
            onClick={onAddNew}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
          >
            Add New
          </button>
        </div>

        <input
          type="text"
          placeholder="Search tenants..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
        />
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-gray-500">Loading...</div>
        ) : filtered.length === 0 ? (
          <div className="p-4 text-center text-gray-500">No tenants found</div>
        ) : (
          <ul>
            {filtered.map((tenant) => (
              <li key={tenant.id}>
                <button
                  onClick={() => onSelect(tenant.id)}
                  className={`w-full p-4 border-b border-gray-100 text-left hover:bg-gray-50 transition ${
                    selectedId === tenant.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                  }`}
                >
                  <div className="font-medium text-sm">{tenant.tenant_name}</div>
                  <div className="text-xs text-gray-500">{tenant.tenant_code}</div>
                  <div className="flex gap-2 mt-2">
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        tenant.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {tenant.is_active ? 'Active' : 'Inactive'}
                    </span>
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        tenant.status === 'active'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {tenant.status}
                    </span>
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

/**
 * Tenant Form Section
 */
function TenantForm({
  tenant,
  isNew,
  onSave,
  onDelete,
  onCancel,
  isSaving,
}: {
  tenant: Tenant | null
  isNew: boolean
  onSave: (data: CreateTenantRequest | UpdateTenantRequest) => Promise<void>
  onDelete: (id: number) => Promise<void>
  onCancel: () => void
  isSaving: boolean
}) {
  const [formData, setFormData] = useState<TenantFormData>({
    tenant_code: tenant?.tenant_code || '',
    tenant_name: tenant?.tenant_name || '',
    description: tenant?.description || '',
    domain: tenant?.domain || '',
    subdomain: tenant?.subdomain || '',
    admin_email: tenant?.admin_email || '',
    admin_name: tenant?.admin_name || '',
    status: tenant?.status || 'active',
    settings: tenant?.settings || {
      theme: 'default',
      language: 'ko',
      timezone: 'Asia/Seoul',
      primaryColor: '#1976d2',
    },
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [activeTab, setActiveTab] = useState<'basic' | 'domain' | 'settings'>(
    'basic'
  )

  const handleChange = (field: keyof TenantFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev }
        delete next[field]
        return next
      })
    }
  }

  const handleSettingChange = (key: keyof TenantSettings, value: any) => {
    setFormData((prev) => ({
      ...prev,
      settings: {
        ...prev.settings,
        [key]: value,
      },
    }))
  }

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.tenant_code?.trim()) {
      newErrors.tenant_code = 'Tenant code is required'
    } else if (!/^[a-z0-9_]+$/.test(formData.tenant_code)) {
      newErrors.tenant_code =
        'Tenant code must contain only lowercase letters, numbers, and underscores'
    }

    if (!formData.tenant_name?.trim()) {
      newErrors.tenant_name = 'Tenant name is required'
    }

    if (
      formData.admin_email &&
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.admin_email)
    ) {
      newErrors.admin_email = 'Invalid email format'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validate()) return

    try {
      await onSave(formData)
    } catch (err) {
      console.error('Save failed:', err)
    }
  }

  const handleDeleteClick = async () => {
    if (!tenant) return
    if (tenant.tenant_code === 'default') {
      alert('Cannot delete the default tenant')
      return
    }

    try {
      await onDelete(tenant.id)
      setShowDeleteConfirm(false)
      onCancel()
    } catch (err) {
      console.error('Delete failed:', err)
    }
  }

  if (!tenant && !isNew) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center text-gray-500">
          <p className="text-lg">Select a tenant to manage</p>
          <p className="text-sm">or create a new one</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 bg-white">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-sm text-gray-500 mb-1">
              {isNew ? 'Create New Tenant' : `Edit Tenant: ${tenant?.tenant_name}`}
            </p>
            <h1 className="text-2xl font-bold">
              {formData.tenant_name || 'Untitled'}
            </h1>
          </div>

          <div className="flex gap-2">
            <button
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={isSaving}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
            >
              {isSaving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 bg-white">
        <div className="flex">
          {(['basic', 'domain', 'settings'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 font-medium text-sm border-b-2 transition ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab === 'basic'
                ? 'Basic Info'
                : tab === 'domain'
                  ? 'Domain Settings'
                  : 'Theme Settings'}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <form onSubmit={handleSubmit} className="max-w-2xl">
          {/* Basic Info Tab */}
          {activeTab === 'basic' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tenant Code *
                </label>
                <input
                  type="text"
                  value={formData.tenant_code}
                  onChange={(e) =>
                    handleChange('tenant_code', e.target.value.toLowerCase())
                  }
                  disabled={!isNew}
                  placeholder="e.g., shop-a"
                  className={`w-full px-3 py-2 border rounded focus:outline-none focus:border-blue-500 disabled:bg-gray-100 ${
                    errors.tenant_code ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.tenant_code && (
                  <p className="text-sm text-red-500 mt-1">
                    {errors.tenant_code}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tenant Name *
                </label>
                <input
                  type="text"
                  value={formData.tenant_name}
                  onChange={(e) => handleChange('tenant_name', e.target.value)}
                  placeholder="e.g., Shop A"
                  className={`w-full px-3 py-2 border rounded focus:outline-none focus:border-blue-500 ${
                    errors.tenant_name ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.tenant_name && (
                  <p className="text-sm text-red-500 mt-1">
                    {errors.tenant_name}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleChange('description', e.target.value)}
                  placeholder="Tenant description"
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="border-t pt-6">
                <h3 className="font-medium text-gray-900 mb-4">
                  Administrator Information
                </h3>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Admin Name
                  </label>
                  <input
                    type="text"
                    value={formData.admin_name}
                    onChange={(e) => handleChange('admin_name', e.target.value)}
                    placeholder="Administrator name"
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Admin Email
                  </label>
                  <input
                    type="email"
                    value={formData.admin_email}
                    onChange={(e) => handleChange('admin_email', e.target.value)}
                    placeholder="admin@example.com"
                    className={`w-full px-3 py-2 border rounded focus:outline-none focus:border-blue-500 ${
                      errors.admin_email ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.admin_email && (
                    <p className="text-sm text-red-500 mt-1">
                      {errors.admin_email}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Domain Settings Tab */}
          {activeTab === 'domain' && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-6">
                <p className="text-sm text-blue-800">
                  Configure how users access this tenant. Use either a subdomain
                  or a custom domain.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Subdomain
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={formData.subdomain}
                    onChange={(e) =>
                      handleChange('subdomain', e.target.value)
                    }
                    placeholder="e.g., shop-a"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                  />
                  <span className="text-gray-600">.example.com</span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Users will access at: subdomain.example.com
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Custom Domain
                </label>
                <input
                  type="text"
                  value={formData.domain}
                  onChange={(e) => handleChange('domain', e.target.value)}
                  placeholder="e.g., www.shop-a.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                />
                <p className="text-xs text-gray-500 mt-2">
                  Users will access at: custom domain
                </p>
              </div>
            </div>
          )}

          {/* Theme Settings Tab */}
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Name
                </label>
                <input
                  type="text"
                  value={formData.settings?.companyName || ''}
                  onChange={(e) =>
                    handleSettingChange('companyName', e.target.value)
                  }
                  placeholder="Company name"
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Theme
                </label>
                <select
                  value={formData.settings?.theme || 'default'}
                  onChange={(e) =>
                    handleSettingChange(
                      'theme',
                      e.target.value as 'default' | 'light' | 'dark'
                    )
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                >
                  <option value="default">Default</option>
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Language
                </label>
                <select
                  value={formData.settings?.language || 'ko'}
                  onChange={(e) =>
                    handleSettingChange(
                      'language',
                      e.target.value as 'ko' | 'en' | 'ja' | 'zh'
                    )
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                >
                  <option value="ko">Korean</option>
                  <option value="en">English</option>
                  <option value="ja">Japanese</option>
                  <option value="zh">Chinese</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Timezone
                </label>
                <input
                  type="text"
                  value={formData.settings?.timezone || 'Asia/Seoul'}
                  onChange={(e) =>
                    handleSettingChange('timezone', e.target.value)
                  }
                  placeholder="e.g., Asia/Seoul"
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Primary Color
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={formData.settings?.primaryColor || '#1976d2'}
                    onChange={(e) =>
                      handleSettingChange('primaryColor', e.target.value)
                    }
                    className="w-12 h-10 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={formData.settings?.primaryColor || '#1976d2'}
                    onChange={(e) =>
                      handleSettingChange('primaryColor', e.target.value)
                    }
                    placeholder="#000000"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500 font-mono text-sm"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Delete Section (for existing tenants) */}
          {!isNew && tenant && tenant.tenant_code !== 'default' && (
            <div className="mt-12 pt-6 border-t border-gray-200">
              <h3 className="font-medium text-red-600 mb-4">Danger Zone</h3>

              {!showDeleteConfirm ? (
                <button
                  type="button"
                  onClick={() => setShowDeleteConfirm(true)}
                  className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                >
                  Delete Tenant
                </button>
              ) : (
                <div className="bg-red-50 border border-red-200 rounded p-4">
                  <p className="text-sm text-red-900 mb-4">
                    Are you sure you want to delete this tenant? This action
                    cannot be undone.
                  </p>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => setShowDeleteConfirm(false)}
                      className="px-3 py-2 border border-gray-300 rounded hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      onClick={handleDeleteClick}
                      className="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </form>
      </div>
    </div>
  )
}

/**
 * Main Tenant Manager Component
 */
export default function TenantManager() {
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [selectedTenant, setSelectedTenant] = useState<Tenant | null>(null)
  const [isAddingNew, setIsAddingNew] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  // Load tenants on mount
  React.useEffect(() => {
    loadTenants()
  }, [])

  const loadTenants = async () => {
    try {
      setIsLoading(true)
      const data = await fetchTenants(0, 1000)
      setTenants(data)
    } catch (error) {
      console.error('Failed to load tenants:', error)
      alert('Failed to load tenants')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectTenant = useCallback((id: number) => {
    const tenant = tenants.find((t) => t.id === id)
    if (tenant) {
      setSelectedId(id)
      setSelectedTenant(tenant)
      setIsAddingNew(false)
    }
  }, [tenants])

  const handleAddNew = useCallback(() => {
    setSelectedId(null)
    setSelectedTenant(null)
    setIsAddingNew(true)
  }, [])

  const handleCancel = useCallback(() => {
    setSelectedId(null)
    setSelectedTenant(null)
    setIsAddingNew(false)
  }, [])

  const handleSave = async (
    data: CreateTenantRequest | UpdateTenantRequest
  ) => {
    try {
      setIsSaving(true)

      if (isAddingNew) {
        const created = await createTenant(data as CreateTenantRequest)
        setTenants((prev) => [created, ...prev])
        setSelectedId(created.id)
        setSelectedTenant(created)
        setIsAddingNew(false)
      } else if (selectedId) {
        const updated = await updateTenant(
          selectedId,
          data as UpdateTenantRequest
        )
        setTenants((prev) =>
          prev.map((t) => (t.id === selectedId ? updated : t))
        )
        setSelectedTenant(updated)
      }

      alert('Saved successfully!')
    } catch (error) {
      console.error('Save failed:', error)
      alert('Failed to save tenant')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    try {
      setIsSaving(true)
      await deleteTenant(id)
      setTenants((prev) => prev.filter((t) => t.id !== id))
      setSelectedId(null)
      setSelectedTenant(null)
      setIsAddingNew(false)
      alert('Tenant deleted successfully!')
    } catch (error) {
      console.error('Delete failed:', error)
      alert('Failed to delete tenant')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="flex h-screen bg-white">
      <TenantList
        tenants={tenants}
        selectedId={selectedId}
        onSelect={handleSelectTenant}
        onAddNew={handleAddNew}
        isLoading={isLoading}
      />

      <TenantForm
        tenant={selectedTenant}
        isNew={isAddingNew}
        onSave={handleSave}
        onDelete={handleDelete}
        onCancel={handleCancel}
        isSaving={isSaving}
      />
    </div>
  )
}
