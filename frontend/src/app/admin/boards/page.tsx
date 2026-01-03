'use client'

/**
 * Admin Board Management Page
 * Manage boards (CRUD)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { boardApi, boardCategoryApi } from '@/lib/api/boards'
import type { Board, BoardCreate, BoardUpdate } from '@/types/board'

export default function AdminBoardsPage() {
  const queryClient = useQueryClient()
  const tenantId = 1 // TODO: Get from auth context

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [editingBoard, setEditingBoard] = useState<Board | null>(null)
  const [formData, setFormData] = useState<Partial<BoardCreate>>({
    tenant_id: tenantId,
    board_name: '',
    board_code: '',
    description: '',
    board_type: 'free',
    read_permission: 'public',
    write_permission: 'member',
    comment_permission: 'member',
    enable_categories: true,
    enable_secret_post: false,
    enable_attachments: true,
    enable_likes: true,
    enable_comments: true,
    display_order: 0,
  })

  // Fetch boards
  const { data: boards, isLoading } = useQuery({
    queryKey: ['boards', tenantId],
    queryFn: () => boardApi.getBoards(tenantId, true),
  })

  // Create board mutation
  const createMutation = useMutation({
    mutationFn: (data: BoardCreate) => boardApi.createBoard(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boards', tenantId] })
      setIsCreateModalOpen(false)
      resetForm()
    },
  })

  // Update board mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: BoardUpdate }) =>
      boardApi.updateBoard(id, tenantId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boards', tenantId] })
      setEditingBoard(null)
      resetForm()
    },
  })

  // Delete board mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => boardApi.deleteBoard(id, tenantId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boards', tenantId] })
    },
  })

  // Handlers
  const resetForm = () => {
    setFormData({
      tenant_id: tenantId,
      board_name: '',
      board_code: '',
      description: '',
      board_type: 'free',
      read_permission: 'public',
      write_permission: 'member',
      comment_permission: 'member',
      enable_categories: true,
      enable_secret_post: false,
      enable_attachments: true,
      enable_likes: true,
      enable_comments: true,
      display_order: 0,
    })
  }

  const handleCreate = () => {
    setIsCreateModalOpen(true)
    resetForm()
  }

  const handleEdit = (board: Board) => {
    setEditingBoard(board)
    setFormData({
      board_name: board.board_name,
      board_code: board.board_code,
      description: board.description,
      board_type: board.board_type,
      read_permission: board.read_permission,
      write_permission: board.write_permission,
      comment_permission: board.comment_permission,
      enable_categories: board.enable_categories,
      enable_secret_post: board.enable_secret_post,
      enable_attachments: board.enable_attachments,
      enable_likes: board.enable_likes,
      enable_comments: board.enable_comments,
      display_order: board.display_order,
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.board_name || !formData.board_code) {
      alert('필수 항목을 입력하세요.')
      return
    }

    if (editingBoard) {
      updateMutation.mutate({
        id: editingBoard.id,
        data: formData as BoardUpdate,
      })
    } else {
      createMutation.mutate(formData as BoardCreate)
    }
  }

  const handleDelete = (board: Board) => {
    if (confirm(`'${board.board_name}' 게시판을 삭제하시겠습니까?`)) {
      deleteMutation.mutate(board.id)
    }
  }

  const handleCancel = () => {
    setIsCreateModalOpen(false)
    setEditingBoard(null)
    resetForm()
  }

  const showModal = isCreateModalOpen || editingBoard !== null

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">게시판 관리</h1>
            <p className="mt-2 text-gray-600">게시판을 생성하고 관리합니다</p>
          </div>
          <button
            onClick={handleCreate}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            게시판 추가
          </button>
        </div>

        {/* Boards list */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="text-gray-600">로딩 중...</div>
          </div>
        ) : boards && boards.length > 0 ? (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    이름
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    코드
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    타입
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    게시글
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    댓글
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    상태
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    작업
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {boards.map((board) => (
                  <tr key={board.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{board.board_name}</div>
                      <div className="text-sm text-gray-500">{board.description}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {board.board_code}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                        {board.board_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {board.total_posts}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {board.total_comments}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span
                        className={`px-2 py-1 rounded ${
                          board.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {board.is_active ? '활성' : '비활성'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => handleEdit(board)}
                        className="text-blue-600 hover:text-blue-700 mr-3"
                      >
                        수정
                      </button>
                      <button
                        onClick={() => handleDelete(board)}
                        className="text-red-600 hover:text-red-700"
                      >
                        삭제
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-500">등록된 게시판이 없습니다.</p>
          </div>
        )}

        {/* Create/Edit Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  {editingBoard ? '게시판 수정' : '게시판 추가'}
                </h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Basic Info */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        게시판 이름 <span className="text-red-600">*</span>
                      </label>
                      <input
                        type="text"
                        value={formData.board_name}
                        onChange={(e) => setFormData({ ...formData, board_name: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        게시판 코드 <span className="text-red-600">*</span>
                      </label>
                      <input
                        type="text"
                        value={formData.board_code}
                        onChange={(e) => setFormData({ ...formData, board_code: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        required
                        disabled={!!editingBoard}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">설명</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      rows={2}
                    />
                  </div>

                  {/* Board Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      게시판 타입
                    </label>
                    <select
                      value={formData.board_type}
                      onChange={(e) =>
                        setFormData({ ...formData, board_type: e.target.value as any })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="notice">공지사항</option>
                      <option value="free">자유게시판</option>
                      <option value="qna">Q&A</option>
                      <option value="faq">FAQ</option>
                      <option value="gallery">갤러리</option>
                      <option value="review">후기게시판</option>
                    </select>
                  </div>

                  {/* Permissions */}
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        읽기 권한
                      </label>
                      <select
                        value={formData.read_permission}
                        onChange={(e) =>
                          setFormData({ ...formData, read_permission: e.target.value as any })
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="public">전체 공개</option>
                        <option value="member">회원</option>
                        <option value="admin">관리자</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        쓰기 권한
                      </label>
                      <select
                        value={formData.write_permission}
                        onChange={(e) =>
                          setFormData({ ...formData, write_permission: e.target.value as any })
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="public">전체 공개</option>
                        <option value="member">회원</option>
                        <option value="admin">관리자</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        댓글 권한
                      </label>
                      <select
                        value={formData.comment_permission}
                        onChange={(e) =>
                          setFormData({ ...formData, comment_permission: e.target.value as any })
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="public">전체 공개</option>
                        <option value="member">회원</option>
                        <option value="admin">관리자</option>
                        <option value="disabled">비활성</option>
                      </select>
                    </div>
                  </div>

                  {/* Features */}
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700">기능 설정</label>
                    <div className="grid grid-cols-2 gap-2">
                      {[
                        { key: 'enable_categories', label: '카테고리' },
                        { key: 'enable_secret_post', label: '비밀글' },
                        { key: 'enable_attachments', label: '첨부파일' },
                        { key: 'enable_likes', label: '좋아요' },
                        { key: 'enable_comments', label: '댓글' },
                      ].map((feature) => (
                        <label key={feature.key} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={formData[feature.key as keyof typeof formData] as boolean}
                            onChange={(e) =>
                              setFormData({ ...formData, [feature.key]: e.target.checked })
                            }
                            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <span className="ml-2 text-sm text-gray-700">{feature.label}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Buttons */}
                  <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                    <button
                      type="button"
                      onClick={handleCancel}
                      className="px-6 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-100"
                    >
                      취소
                    </button>
                    <button
                      type="submit"
                      disabled={createMutation.isPending || updateMutation.isPending}
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                      {createMutation.isPending || updateMutation.isPending
                        ? '처리 중...'
                        : editingBoard
                        ? '수정'
                        : '추가'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
