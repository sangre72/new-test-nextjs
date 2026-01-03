'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { UserMenu } from '@/components/auth'

export default function Home() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await api.get('/health')
      return response.data
    },
  })

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-gray-900">MyApp</h1>
            <UserMenu />
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-900 mb-4">
              Welcome to MyApp
            </h1>
            <p className="text-xl text-gray-600">
              FastAPI + Next.js + PostgreSQL
            </p>
          </div>

          {/* API Status Card */}
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              API Status
            </h2>

            {isLoading && (
              <div className="flex items-center text-gray-600">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-900 mr-3"></div>
                Connecting to API...
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 font-medium">Failed to connect to API</p>
                <p className="text-red-600 text-sm mt-1">
                  Make sure the backend server is running on http://localhost:8000
                </p>
              </div>
            )}

            {data && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="bg-green-500 rounded-full h-3 w-3 mr-3"></div>
                  <p className="text-green-800 font-medium">API is healthy</p>
                </div>
                <pre className="mt-3 text-sm text-gray-700 bg-gray-50 p-3 rounded">
                  {JSON.stringify(data, null, 2)}
                </pre>
              </div>
            )}
          </div>

          {/* Quick Links */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="block bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                API Docs (Swagger)
              </h3>
              <p className="text-gray-600 text-sm">
                Interactive API documentation
              </p>
            </a>

            <a
              href="http://localhost:8000/redoc"
              target="_blank"
              rel="noopener noreferrer"
              className="block bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                ReDoc
              </h3>
              <p className="text-gray-600 text-sm">
                Alternative API documentation
              </p>
            </a>

            <a
              href="/CLAUDE.md"
              className="block bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Documentation
              </h3>
              <p className="text-gray-600 text-sm">
                Project setup and guides
              </p>
            </a>
          </div>

          {/* Next Steps */}
          <div className="mt-12 bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Next Steps
            </h2>
            <ol className="space-y-3 text-gray-700">
              <li className="flex items-start">
                <span className="bg-primary-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
                  1
                </span>
                <span>Set up environment variables (.env files)</span>
              </li>
              <li className="flex items-start">
                <span className="bg-primary-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
                  2
                </span>
                <span>Run database migrations: <code className="bg-gray-100 px-2 py-1 rounded text-sm">alembic upgrade head</code></span>
              </li>
              <li className="flex items-start">
                <span className="bg-primary-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
                  3
                </span>
                <span>Add features using Claude agents (see CLAUDE.md)</span>
              </li>
              <li className="flex items-start">
                <span className="bg-primary-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
                  4
                </span>
                <span>Start building your application!</span>
              </li>
            </ol>
          </div>
        </div>
      </div>
    </main>
  )
}
