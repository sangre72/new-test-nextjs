export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          New Test Project
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          FastAPI + Next.js 15 + TypeScript + Tailwind CSS
        </p>
        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            프로젝트 초기화가 완료되었습니다.
          </p>
          <div className="text-sm text-gray-500">
            <p>다음 단계:</p>
            <ul className="mt-2 space-y-1">
              <li>1. Use shared-schema --init</li>
              <li>2. Use auth-backend --init --type=phone</li>
              <li>3. Use auth-frontend --init</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
