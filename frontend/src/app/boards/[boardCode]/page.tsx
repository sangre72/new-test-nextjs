'use client'

/**
 * Board Post List Page
 * Displays paginated list of posts for a board
 */

import { useParams, useSearchParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import Link from 'next/link'
import { boardApi, boardPostApi, boardCategoryApi } from '@/lib/api/boards'
import type { BoardPostListRequest } from '@/types/board'

export default function BoardPostListPage() {
  const params = useParams()
  const searchParams = useSearchParams()
  const router = useRouter()

  const boardCode = params.boardCode as string
  const tenantId = 1 // TODO: Get from auth context

  // Query parameters
  const page = parseInt(searchParams.get('page') || '1')
  const categoryId = searchParams.get('category_id') ? parseInt(searchParams.get('category_id')!) : undefined
  const search = searchParams.get('search') || undefined

  const [searchInput, setSearchInput] = useState(search || '')

  // Fetch board info
  const { data: board, isLoading: boardLoading } = useQuery({
    queryKey: ['board', boardCode, tenantId],
    queryFn: () => boardApi.getBoard(boardCode, tenantId),
  })

  // Fetch categories
  const { data: categories } = useQuery({
    queryKey: ['boardCategories', board?.id, tenantId],
    queryFn: () => boardCategoryApi.getCategories(board!.id, tenantId),
    enabled: !!board && board.enable_categories,
  })

  // Fetch posts
  const requestParams: BoardPostListRequest = {
    page,
    page_size: 20,
    category_id: categoryId,
    search,
    sort_by: 'created_at',
    sort_order: 'desc',
  }

  const { data: postsData, isLoading: postsLoading } = useQuery({
    queryKey: ['boardPosts', boardCode, tenantId, requestParams],
    queryFn: () => boardPostApi.getPosts(boardCode, tenantId, requestParams),
  })

  // Handlers
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const params = new URLSearchParams(searchParams.toString())
    if (searchInput) {
      params.set('search', searchInput)
    } else {
      params.delete('search')
    }
    params.set('page', '1')
    router.push(`/boards/${boardCode}?${params.toString()}`)
  }

  const handleCategoryFilter = (catId?: number) => {
    const params = new URLSearchParams(searchParams.toString())
    if (catId) {
      params.set('category_id', catId.toString())
    } else {
      params.delete('category_id')
    }
    params.set('page', '1')
    router.push(`/boards/${boardCode}?${params.toString()}`)
  }

  const handlePageChange = (newPage: number) => {
    const params = new URLSearchParams(searchParams.toString())
    params.set('page', newPage.toString())
    router.push(`/boards/${boardCode}?${params.toString()}`)
  }

  // Permission check
  const canWrite = board && board.write_permission === 'public' // TODO: Implement proper permission check

  if (boardLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">로딩 중...</div>
      </div>
    )
  }

  if (!board) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-red-600">게시판을 찾을 수 없습니다.</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">{board.board_name}</h1>
          {board.description && (
            <p className="mt-2 text-gray-600">{board.description}</p>
          )}
          <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
            <span>전체 {board.total_posts}개</span>
            <span>댓글 {board.total_comments}개</span>
          </div>
        </div>

        {/* Categories */}
        {board.enable_categories && categories && categories.length > 0 && (
          <div className="mb-6 flex flex-wrap gap-2">
            <button
              onClick={() => handleCategoryFilter()}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                !categoryId
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
              }`}
            >
              전체
            </button>
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => handleCategoryFilter(category.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  categoryId === category.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                }`}
                style={
                  categoryId === category.id && category.color
                    ? { backgroundColor: category.color, borderColor: category.color }
                    : {}
                }
              >
                {category.category_name}
              </button>
            ))}
          </div>
        )}

        {/* Search & Write */}
        <div className="mb-6 flex items-center justify-between gap-4">
          <form onSubmit={handleSearch} className="flex-1 max-w-md">
            <div className="flex gap-2">
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="검색어를 입력하세요"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                검색
              </button>
            </div>
          </form>

          {canWrite && (
            <Link
              href={`/boards/${boardCode}/write`}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors whitespace-nowrap"
            >
              글쓰기
            </Link>
          )}
        </div>

        {/* Post List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  번호
                </th>
                {board.enable_categories && (
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    분류
                  </th>
                )}
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  제목
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  작성자
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  날짜
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  조회
                </th>
                {board.enable_likes && (
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    추천
                  </th>
                )}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {postsLoading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                    로딩 중...
                  </td>
                </tr>
              ) : postsData && postsData.items.length > 0 ? (
                postsData.items.map((post, index) => {
                  const postNumber = postsData.total - (page - 1) * 20 - index
                  return (
                    <tr key={post.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {post.is_pinned ? (
                          <span className="text-red-600 font-bold">공지</span>
                        ) : (
                          postNumber
                        )}
                      </td>
                      {board.enable_categories && (
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          {post.category_name && (
                            <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                              {post.category_name}
                            </span>
                          )}
                        </td>
                      )}
                      <td className="px-6 py-4 text-sm text-gray-900">
                        <Link
                          href={`/boards/${boardCode}/${post.id}`}
                          className="hover:text-blue-600 font-medium"
                        >
                          {post.is_notice && (
                            <span className="text-red-600 font-bold mr-2">[공지]</span>
                          )}
                          {post.title}
                          {post.comment_count > 0 && (
                            <span className="ml-2 text-blue-600">[{post.comment_count}]</span>
                          )}
                          {board.board_type === 'qna' && post.is_answered && (
                            <span className="ml-2 text-green-600">[답변완료]</span>
                          )}
                          {board.board_type === 'review' && post.rating && (
                            <span className="ml-2 text-yellow-600">
                              {'★'.repeat(post.rating)}
                            </span>
                          )}
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {post.author_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(post.created_at).toLocaleDateString('ko-KR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {post.view_count}
                      </td>
                      {board.enable_likes && (
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {post.like_count}
                        </td>
                      )}
                    </tr>
                  )
                })
              ) : (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                    게시글이 없습니다.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {postsData && postsData.total_pages > 1 && (
          <div className="mt-6 flex justify-center gap-2">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
              className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
            >
              이전
            </button>

            {Array.from({ length: postsData.total_pages }, (_, i) => i + 1)
              .filter((p) => {
                return p === 1 || p === postsData.total_pages || Math.abs(p - page) <= 2
              })
              .map((p, index, array) => {
                if (index > 0 && p - array[index - 1] > 1) {
                  return (
                    <span key={`ellipsis-${p}`} className="px-2 py-2">
                      ...
                    </span>
                  )
                }
                return (
                  <button
                    key={p}
                    onClick={() => handlePageChange(p)}
                    className={`px-4 py-2 border rounded-lg ${
                      p === page
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'border-gray-300 hover:bg-gray-100'
                    }`}
                  >
                    {p}
                  </button>
                )
              })}

            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={page === postsData.total_pages}
              className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
            >
              다음
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
