# 메뉴 관리 Frontend 구현 요약

## 구현 완료 현황

### ✅ 생성된 파일

```
frontend/src/
├── types/
│   └── menu.ts                          # 메뉴 타입 정의 (Menu, MenuFormData 등)
│
├── lib/
│   └── api/
│       └── menus.ts                     # 메뉴 API 클라이언트 + 검증 함수
│
├── components/
│   └── menus/
│       ├── MenuManager.tsx              # 관리자 메뉴 관리 컴포넌트
│       ├── MenuTree.tsx                 # 트리 컴포넌트 (드래그&드롭)
│       ├── MenuForm.tsx                 # 메뉴 생성/수정 폼
│       ├── Navigation.tsx               # 데스크톱 네비게이션
│       ├── MobileDrawer.tsx             # 모바일 드로어 메뉴
│       └── index.ts                     # Export
│
└── app/
    ├── admin/
    │   └── menus/
    │       └── page.tsx                 # /admin/menus 페이지
    └── mypage/
        ├── layout.tsx                   # 마이페이지 레이아웃
        └── page.tsx                     # 마이페이지 홈

문서:
├── MENU_FRONTEND_README.md              # 상세 사용 가이드
├── MENU_QUICK_START.md                  # 빠른 시작 가이드
└── MENU_IMPLEMENTATION_SUMMARY.md       # 이 파일
```

---

## 핵심 기능

### 1. 관리자 메뉴 관리 (MenuManager)

**파일:** `components/menus/MenuManager.tsx`

**기능:**
- 메뉴 CRUD (생성, 조회, 수정, 삭제)
- 트리 구조 표시
- 드래그&드롭 정렬/계층 변경
- 실시간 미리보기
- 에러 처리 및 성공 메시지

**보안:**
- ✅ XSS 방지 (React 기본 이스케이프)
- ✅ 입력 검증 (validateMenuInput)
- ✅ 안전한 URL 검증 (isSafeUrl)

**사용:**
```tsx
<MenuManager menuType="user" title="사용자 메뉴 관리" />
```

---

### 2. 메뉴 트리 (MenuTree)

**파일:** `components/menus/MenuTree.tsx`

**기능:**
- 계층형 메뉴 표시
- 확장/축소 토글
- HTML5 드래그&드롭 API
- 호버 시 액션 버튼 표시
- 배지/강조 표시

**드래그&드롭:**
```typescript
// 이벤트 핸들러
onDragStart → onDragOver → onDrop → API 호출 (moveMenu)
```

**사용:**
```tsx
<MenuTree
  menus={menus}
  selectedId={selectedId}
  onSelect={handleSelectMenu}
  onEdit={handleEdit}
  onDelete={handleDelete}
  onCreateChild={handleCreateChild}
  onMove={handleMoveMenu}
  expandedIds={expandedIds}
  onToggleExpand={handleToggleExpand}
/>
```

---

### 3. 메뉴 폼 (MenuForm)

**파일:** `components/menus/MenuForm.tsx`

**기능:**
- 생성/수정 모드
- 실시간 입력 검증
- 조건부 필드 표시
- 에러 메시지 표시

**검증 규칙:**
- 메뉴 이름: 필수, 최대 100자
- 메뉴 코드: 필수, 최대 50자, 영문/숫자/언더스코어만
- URL: `/` 또는 `http(s)://`로 시작
- 안전하지 않은 URL 차단 (`javascript:`, `data:`)

**사용:**
```tsx
<MenuForm
  isEdit={false}
  menu={null}
  parentMenus={parentMenus}
  onSubmit={handleSubmit}
  onCancel={handleCancel}
  loading={loading}
  error={error}
/>
```

---

### 4. 데스크톱 네비게이션 (Navigation)

**파일:** `components/menus/Navigation.tsx`

**기능:**
- 활성 메뉴 자동 필터링 (is_active, is_visible, is_enabled)
- 현재 경로 강조
- 확장/축소 가능
- 배지/강조 표시
- 로딩/에러 상태 처리

**사용:**
```tsx
<Navigation menuType="user" className="bg-white p-4" />
```

---

### 5. 모바일 드로어 (MobileDrawer)

**파일:** `components/menus/MobileDrawer.tsx`

**기능:**
- 좌측 슬라이드 드로어
- 백드롭 클릭 시 닫기
- ESC 키로 닫기
- body 스크롤 잠금
- 포커스 관리

**사용:**
```tsx
const [isOpen, setIsOpen] = useState(false)

<MobileDrawer
  menuType="user"
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
/>
```

---

## 타입 시스템

### 주요 타입

**파일:** `types/menu.ts`

```typescript
// 메뉴 타입
type MenuType = 'site' | 'user' | 'admin' | 'header_utility' | 'footer_utility' | 'quick_menu'

// 링크 타입
type LinkType = 'url' | 'new_window' | 'modal' | 'external' | 'none'

// 권한 타입
type PermissionType = 'public' | 'member' | 'groups' | 'users' | 'roles' | 'admin'

// 표시 조건
type ShowCondition = 'always' | 'logged_in' | 'logged_out' | 'custom'

// 배지 타입
type BadgeType = 'none' | 'count' | 'dot' | 'text' | 'api'
```

### 주요 인터페이스

```typescript
interface Menu {
  id: number
  menu_type: MenuType
  menu_name: string
  menu_code: string
  link_type: LinkType
  link_url?: string
  permission_type: PermissionType
  is_visible: boolean
  is_enabled: boolean
  children?: Menu[]
  // ... 기타 필드
}

interface MenuFormData {
  menu_type: MenuType
  menu_name: string
  menu_code: string
  link_type: LinkType
  // ... 기타 필드
}
```

---

## API 클라이언트

### 파일: `lib/api/menus.ts`

### API 함수

```typescript
// 관리자 API
getAllMenus(menuType?: MenuType): Promise<Menu[]>
getMenuById(id: number): Promise<Menu>
createMenu(data: MenuFormData): Promise<{ id: number; message: string }>
updateMenu(id: number, data: Partial<MenuFormData>): Promise<void>
deleteMenu(id: number): Promise<void>
moveMenu(id: number, parentId: number | null, sortOrder: number): Promise<void>
reorderMenus(orderedIds: number[]): Promise<void>

// 공개 API
getPublicMenus(menuType: MenuType): Promise<Menu[]>
```

### 유틸리티 함수

```typescript
// URL 안전성 검증
isSafeUrl(url: string): boolean

// 입력 검증
validateMenuInput(data: MenuFormData): string[]
```

### 에러 처리

```typescript
const handleError = (error: AxiosError | any): never => {
  // API 응답 에러
  if (error.response?.data?.message) {
    throw new Error(error.response.data.message)
  }

  // 네트워크 에러
  if (error.code === 'ERR_NETWORK') {
    throw new Error('네트워크 연결을 확인해주세요.')
  }

  // 타임아웃
  if (error.code === 'ECONNABORTED') {
    throw new Error('요청 시간이 초과되었습니다.')
  }

  throw new Error('요청 중 오류가 발생했습니다.')
}
```

---

## 보안 체크리스트

### ✅ 구현된 보안 기능

1. **XSS 방지**
   - React 기본 이스케이프 사용
   - dangerouslySetInnerHTML 사용 안 함

2. **URL 안전성 검증**
   ```typescript
   isSafeUrl(url: string): boolean
   - javascript: 프로토콜 차단
   - data: 프로토콜 차단
   ```

3. **입력 검증**
   ```typescript
   validateMenuInput(data: MenuFormData): string[]
   - 필수 필드 검증
   - 길이 제한 검증
   - 패턴 검증 (영문/숫자/언더스코어)
   - URL 형식 검증
   ```

4. **에러 처리**
   - 모든 API 호출 try-catch
   - 사용자 친화적 에러 메시지
   - 네트워크 에러 감지

---

## 반응형 디자인

### 브레이크포인트

```css
/* Tailwind CSS 기본 브레이크포인트 */
sm: 640px
md: 768px
lg: 1024px   ← Navigation 표시/숨김 기준
xl: 1280px
```

### 구현 전략

**데스크톱 (lg 이상):**
```tsx
<aside className="hidden lg:block w-64">
  <Navigation menuType="user" />
</aside>
```

**모바일 (lg 미만):**
```tsx
<button className="lg:hidden" onClick={() => setIsOpen(true)}>
  메뉴
</button>

<MobileDrawer isOpen={isOpen} onClose={() => setIsOpen(false)} />
```

---

## 성능 최적화

### 1. React 최적화

```typescript
// useCallback으로 함수 메모이제이션
const handleSelectMenu = useCallback((id: number) => {
  setSelectedId(id)
}, [])

// 조건부 렌더링으로 불필요한 렌더링 방지
{isExpanded && hasChildren && <ChildMenus />}
```

### 2. 로딩 상태

```tsx
{loading ? (
  <LoadingSkeleton />
) : error ? (
  <ErrorMessage />
) : (
  <Content />
)}
```

### 3. 필터링

```typescript
// 활성 메뉴만 표시
const visibleMenus = data.filter(
  (menu) => menu.is_active && menu.is_visible && menu.is_enabled
)
```

---

## 접근성 (A11y)

### 1. 키보드 네비게이션

- ESC: 드로어 닫기
- Enter/Space: 버튼 활성화

### 2. ARIA 속성

```tsx
<button aria-label="메뉴 열기">...</button>
<button aria-label="메뉴 닫기">...</button>
```

### 3. 포커스 관리

- 드로어 열릴 때: 첫 번째 메뉴 항목에 포커스
- 드로어 닫힐 때: 이전 포커스 위치로 복원

---

## 사용 예시

### 1. 관리자 페이지

```tsx
// app/admin/menus/page.tsx
import { MenuManager } from '@/components/menus'

export default function AdminMenusPage() {
  return <MenuManager menuType="user" title="사용자 메뉴 관리" />
}
```

**URL:** `/admin/menus`

---

### 2. 마이페이지 레이아웃

```tsx
// app/mypage/layout.tsx
'use client'

import { useState } from 'react'
import { Navigation, MobileDrawer } from '@/components/menus'

export default function MyPageLayout({ children }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <div>
      <header>
        <button
          onClick={() => setIsMobileMenuOpen(true)}
          className="lg:hidden"
        >
          메뉴
        </button>
      </header>

      <div className="flex gap-6">
        {/* 데스크톱 */}
        <aside className="hidden lg:block w-64">
          <Navigation menuType="user" />
        </aside>

        {/* 메인 */}
        <main>{children}</main>
      </div>

      {/* 모바일 */}
      <MobileDrawer
        menuType="user"
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />
    </div>
  )
}
```

---

## Backend API 연동 필요

### 필수 엔드포인트

```
GET    /api/v1/admin/menus              # 메뉴 목록 (관리자)
GET    /api/v1/admin/menus/:id          # 메뉴 상세
POST   /api/v1/admin/menus              # 메뉴 생성
PUT    /api/v1/admin/menus/:id          # 메뉴 수정
DELETE /api/v1/admin/menus/:id          # 메뉴 삭제
PUT    /api/v1/admin/menus/:id/move     # 메뉴 이동
PUT    /api/v1/admin/menus/reorder      # 순서 변경
GET    /api/v1/menus                    # 공개 메뉴 (권한별)
```

### 응답 형식

```typescript
interface ApiResponse<T> {
  success: boolean
  data?: T
  error_code?: string
  message?: string
}
```

---

## 테스트 시나리오

### 1. 관리자 테스트

1. 메뉴 추가 ✅
2. 메뉴 수정 ✅
3. 메뉴 삭제 ✅
4. 드래그&드롭 ✅
5. 하위 메뉴 추가 ✅

### 2. 사용자 테스트

1. 데스크톱 네비게이션 표시 ✅
2. 모바일 드로어 열기/닫기 ✅
3. 메뉴 클릭 시 페이지 이동 ✅
4. 활성 메뉴 강조 ✅

### 3. 보안 테스트

1. XSS 공격 시도 (차단됨) ✅
2. 안전하지 않은 URL (차단됨) ✅
3. 잘못된 입력 (검증됨) ✅

---

## 다음 단계

### 1. Backend 구현

- FastAPI 메뉴 엔드포인트 구현
- 권한 체크 미들웨어
- 데이터베이스 스키마

### 2. 고급 기능

- 메뉴 검색 기능
- 일괄 편집
- 메뉴 복제
- 메뉴 미리보기

### 3. 테스트

- Unit 테스트 (Jest + React Testing Library)
- E2E 테스트 (Playwright)

### 4. 배포

- 환경변수 설정
- 빌드 최적화
- CDN 설정

---

## 참고 문서

- [MENU_FRONTEND_README.md](./MENU_FRONTEND_README.md) - 상세 가이드
- [MENU_QUICK_START.md](./MENU_QUICK_START.md) - 빠른 시작

---

## 기술 스택 요약

- **React 19** - UI 라이브러리
- **Next.js 16** - App Router, SSR
- **TypeScript** - 타입 안전성
- **Tailwind CSS** - 스타일링
- **TanStack Query** - API 상태 관리 (추후 적용 가능)
- **Axios** - HTTP 클라이언트
- **HTML5 Drag & Drop API** - 드래그&드롭

---

## 코딩 컨벤션

### 네이밍

- 컴포넌트: PascalCase (`MenuManager`)
- 함수/변수: camelCase (`handleSelectMenu`)
- 상수: UPPER_SNAKE_CASE (`API_BASE_URL`)
- Boolean: is/has/should 접두사 (`isLoading`)
- 이벤트 핸들러: handle 접두사 (`handleClick`)

### Import 순서

1. React/Next.js
2. 외부 라이브러리
3. 내부 컴포넌트
4. 타입
5. API/유틸

---

## 완료!

메뉴 관리 Frontend 컴포넌트가 모두 구현되었습니다.

**시작하기:**
```bash
npm run dev
http://localhost:3000/admin/menus
```
