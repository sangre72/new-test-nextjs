'use client'

/**
 * Board Post Detail Page
 * Displays a single post with comments
 */

import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import Link from 'next/link'
import { boardApi, boardPostApi, boardCommentApi } from '@/lib/api/boards'
import type { BoardCommentCreate } from '@/types/board'

export default function BoardPostDetailPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()

  const boardCode = params.boardCode as string
  const postId = parseInt(params.postId as string)
  const tenantId = 1 // TODO: Get from auth context
  const currentUserId = 1 // TODO: Get from auth context

  const [commentContent, setCommentContent] = useState('')
  const [replyTo, setReplyTo] = useState<number | null>(null)

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

  // Fetch comments
  const { data: comments } = useQuery({
    queryKey: ['boardComments', boardCode, postId, tenantId],
    queryFn: () => boardCommentApi.getComments(boardCode, postId, tenantId),
    enabled: !!board && board.enable_comments,
  })

  // Like mutation
  const likeMutation = useMutation({
    mutationFn: () => boardPostApi.toggleLike(boardCode, postId, tenantId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boardPost', boardCode, postId, tenantId] })
    },
  })

  // Comment mutation
  const commentMutation = useMutation({
    mutationFn: (data: BoardCommentCreate) => boardCommentApi.createComment(boardCode, postId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boardComments', boardCode, postId, tenantId] })
      queryClient.invalidateQueries({ queryKey: ['boardPost', boardCode, postId, tenantId] })
      setCommentContent('')
      setReplyTo(null)
    },
  })

  // Delete post mutation
  const deleteMutation = useMutation({
    mutationFn: () => boardPostApi.deletePost(boardCode, postId, tenantId),
    onSuccess: () => {
      router.push(`/boards/${boardCode}`)
    },
  })

  // Handlers
  const handleLike = () => {
    likeMutation.mutate()
  }

  const handleCommentSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!commentContent.trim()) return

    commentMutation.mutate({
      post_id: postId,
      tenant_id: tenantId,
      content: commentContent,
      parent_id: replyTo || undefined,
    })
  }

  const handleDelete = () => {
    if (confirm('정말 삭제하시겠습니까?')) {
      deleteMutation.mutate()
    }
  }

  // Render comment tree
  const renderComment = (comment: any, depth = 0) => {
    return (
      <div key={comment.id} className={`${depth > 0 ? 'ml-12 mt-4' : 'mt-4'}`}>
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <span className="font-medium text-gray-900">{comment.author_name}</span>
              <span className="text-sm text-gray-500">
                {new Date(comment.created_at).toLocaleString('ko-KR')}
              </span>
              {comment.is_answer && (
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
                  답변
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              {comment.can_edit && (
                <button className="text-sm text-blue-600 hover:text-blue-700">수정</button>
              )}
              {comment.can_delete && (
                <button className="text-sm text-red-600 hover:text-red-700">삭제</button>
              )}
              <button
                onClick={() => setReplyTo(comment.id)}
                className="text-sm text-gray-600 hover:text-gray-700"
              >
                답글
              </button>
            </div>
          </div>
          <p className="text-gray-700 whitespace-pre-wrap">{comment.content}</p>
          {comment.like_count > 0 && (
            <div className="mt-2 text-sm text-gray-500">👍 {comment.like_count}</div>
          )}
        </div>

        {/* Nested replies */}
        {comment.replies && comment.replies.length > 0 && (
          <div className="mt-2">
            {comment.replies.map((reply: any) => renderComment(reply, depth + 1))}
          </div>
        )}

        {/* Reply form */}
        {replyTo === comment.id && (
          <div className="mt-4 ml-12">
            <form onSubmit={handleCommentSubmit} className="bg-gray-50 rounded-lg p-4">
              <textarea
                value={commentContent}
                onChange={(e) => setCommentContent(e.target.value)}
                placeholder="답글을 입력하세요"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                rows={3}
              />
              <div className="mt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setReplyTo(null)
                    setCommentContent('')
                  }}
                  className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-100"
                >
                  취소
                </button>
                <button
                  type="submit"
                  disabled={commentMutation.isPending}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {commentMutation.isPending ? '등록 중...' : '답글 등록'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    )
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

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back button */}
        <div className="mb-6">
          <Link
            href={`/boards/${boardCode}`}
            className="text-blue-600 hover:text-blue-700 flex items-center gap-2"
          >
            ← 목록으로
          </Link>
        </div>

        {/* Post */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* Header */}
          <div className="border-b border-gray-200 p-6">
            <div className="mb-4">
              {post.category_name && (
                <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded mr-2">
                  {post.category_name}
                </span>
              )}
              {post.is_notice && (
                <span className="inline-block px-3 py-1 bg-red-100 text-red-800 text-sm font-medium rounded">
                  공지
                </span>
              )}
            </div>

            <h1 className="text-3xl font-bold text-gray-900 mb-4">{post.title}</h1>

            <div className="flex items-center justify-between text-sm text-gray-600">
              <div className="flex items-center gap-4">
                <span>{post.author_name}</span>
                <span>{new Date(post.created_at).toLocaleString('ko-KR')}</span>
              </div>
              <div className="flex items-center gap-4">
                <span>조회 {post.view_count}</span>
                {board.enable_likes && <span>추천 {post.like_count}</span>}
                {board.enable_comments && <span>댓글 {post.comment_count}</span>}
              </div>
            </div>

            {/* Rating (for review board) */}
            {board.board_type === 'review' && post.rating && (
              <div className="mt-4 flex items-center gap-2">
                <span className="text-yellow-500 text-2xl">{'★'.repeat(post.rating)}</span>
                <span className="text-gray-600">{'☆'.repeat(5 - post.rating)}</span>
              </div>
            )}
          </div>

          {/* Content */}
          <div className="p-6">
            <div
              className="prose max-w-none text-gray-700"
              dangerouslySetInnerHTML={{ __html: post.content }}
            />
          </div>

          {/* Actions */}
          <div className="border-t border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {board.enable_likes && (
                  <button
                    onClick={handleLike}
                    disabled={likeMutation.isPending}
                    className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                      post.has_liked
                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    👍 추천 {post.like_count}
                  </button>
                )}
              </div>

              <div className="flex items-center gap-2">
                {post.can_edit && (
                  <Link
                    href={`/boards/${boardCode}/${postId}/edit`}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    수정
                  </Link>
                )}
                {post.can_delete && (
                  <button
                    onClick={handleDelete}
                    disabled={deleteMutation.isPending}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                  >
                    삭제
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Comments */}
        {board.enable_comments && (
          <div className="mt-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              댓글 {post.comment_count}개
            </h2>

            {/* Comment form */}
            {!replyTo && (
              <form onSubmit={handleCommentSubmit} className="mb-6">
                <textarea
                  value={commentContent}
                  onChange={(e) => setCommentContent(e.target.value)}
                  placeholder="댓글을 입력하세요"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  rows={4}
                />
                <div className="mt-2 flex justify-end">
                  <button
                    type="submit"
                    disabled={commentMutation.isPending}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {commentMutation.isPending ? '등록 중...' : '댓글 등록'}
                  </button>
                </div>
              </form>
            )}

            {/* Comments list */}
            <div className="space-y-4">
              {comments && comments.length > 0 ? (
                comments.map((comment) => renderComment(comment))
              ) : (
                <p className="text-center text-gray-500 py-8">댓글이 없습니다.</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
