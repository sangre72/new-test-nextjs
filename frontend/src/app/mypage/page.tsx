/**
 * MyPage Home
 * 마이페이지 홈
 */

export default function MyPageHome() {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">마이페이지</h2>
      <p className="text-gray-600">
        좌측 메뉴에서 원하는 페이지를 선택하세요.
      </p>
      <p className="text-sm text-gray-500 mt-2">
        모바일에서는 상단의 메뉴 버튼을 클릭하세요.
      </p>
    </div>
  )
}
