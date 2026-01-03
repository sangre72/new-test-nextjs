'use client'

/**
 * Board Post Edit Page
 * Edit an existing post
 */

import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import { boardApi, boardPostApi, boardCategoryApi } from '@/lib/api/boards'
import type { BoardPostUpdate } from '@/types/board'

export default function BoardPostEditPage() {
  const params = useParams()
  const router = useRouter()

  const boardCode = params.boardCode as string
  const postId = parseInt(params.postId as string)
  const tenantId = 1 // TODO: Get from auth context

  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category_id: undefined as number | undefined,
    is_secret: false,
    rating: undefined as number | undefined,
  })

  // Fetch board info
  const { data: board } = useQuery({
    queryKey: ['board', boardCode, tenantId],
    queryFn: () => boardApi.getBoard(boardCode, tenantId),
  })

  // Fetch post
  const { data: post, isLoading: postLoading } = useQuery({
    queryKey: ['boardPost', boardCode, postId, tenantId],
    queryFn: () => boardPostApi.getPost(boardCode, postId, tenantId),
  })

  // Fetch categories
  const { data: categories } = useQuery({
    queryKey: ['boardCategories', board?.id, tenantId],
    queryFn: () => boardCategoryApi.getCategories(board!.id, tenantId),
    enabled: !!board && board.enable_categories,
  })

  // Initialize form data from post
  useEffect(() => {
    if (post) {
      setFormData({
        title: post.title,
        content: post.content,
        category_id: post.category_id,
        is_secret: post.is_secret,
        rating: post.rating,
      })
    }
  }, [post])

  // Update post mutation
  const updateMutation = useMutation({
    mutationFn: (data: BoardPostUpdate) => boardPostApi.updatePost(boardCode, postId, tenantId, data),
    onSuccess: () => {
      router.push(`/boards/${boardCode}/${postId}`)
    },
  })

  // Handlers
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.title.trim()) {
      alert('제목을 입력하세요.')
      return
    }

    if (!formData.content.trim()) {
      alert('내용을 입력하세요.')
      return
    }

    if (board?.board_type === 'review' && board.settings?.rating_required && !formData.rating) {
      alert('별점을 선택하세요.')
      return
    }

    const updateData: BoardPostUpdate = {
      title: formData.title,
      content: formData.content,
      category_id: formData.category_id,
      is_secret: formData.is_secret,
      rating: formData.rating,
    }

    updateMutation.mutate(updateData)
  }

  const handleCancel = () => {
    if (confirm('수정을 취소하시겠습니까?')) {
      router.push(`/boards/${boardCode}/${postId}`)
    }
  }

  if (postLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">로딩 중...</div>
      </div>
    )
  }

  if (!post || !board) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-red-600">게시글을 찾을 수 없습니다.</div>
      </div>
    )
  }

  if (!post.can_edit) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-red-600">수정 권한이 없습니다.</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">글수정</h1>
          <p className="mt-2 text-gray-600">{board.board_name}</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
          {/* Category */}
          {board.enable_categories && categories && categories.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">분류</label>
              <select
                value={formData.category_id || ''}
                onChange={(e) =>
                  setFormData({ ...formData, category_id: e.target.value ? parseInt(e.target.value) : undefined })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">선택하세요</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.category_name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Rating (for review board) */}
          {board.board_type === 'review' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                별점 {board.settings?.rating_required && <span className="text-red-600">*</span>}
              </label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setFormData({ ...formData, rating: star })}
                    className="text-3xl focus:outline-none"
                  >
                    {formData.rating && star <= formData.rating ? (
                      <span className="text-yellow-500">★</span>
                    ) : (
                      <span className="text-gray-300">☆</span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              제목 <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="제목을 입력하세요"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          {/* Content */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              내용 <span className="text-red-600">*</span>
            </label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              placeholder="내용을 입력하세요"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              rows={15}
              required
            />
          </div>

          {/* Secret post */}
          {board.enable_secret_post && (
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_secret"
                checked={formData.is_secret}
                onChange={(e) => setFormData({ ...formData, is_secret: e.target.checked })}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="is_secret" className="ml-2 text-sm text-gray-700">
                비밀글로 작성
              </label>
            </div>
          )}

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
              disabled={updateMutation.isPending}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {updateMutation.isPending ? '수정 중...' : '수정'}
            </button>
          </div>

          {/* Error message */}
          {updateMutation.isError && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600">
                게시글 수정에 실패했습니다. 다시 시도해주세요.
              </p>
            </div>
          )}
        </form>
      </div>
    </div>
  )
}
