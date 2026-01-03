# 메뉴 관리 Frontend 가이드

메뉴 관리 시스템의 Frontend 컴포넌트 문서입니다.

## 목차

- [개요](#개요)
- [설치된 컴포넌트](#설치된-컴포넌트)
- [보안 원칙](#보안-원칙)
- [사용법](#사용법)
- [컴포넌트 API](#컴포넌트-api)
- [커스터마이징](#커스터마이징)

---

## 개요

### 기술 스택

- **React 19** + **Next.js 16** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **TanStack Query** (API 상태 관리)

### 핵심 원칙

1. **Security First**: XSS 방지, 안전한 URL 검증
2. **Error Handling First**: 모든 API 호출에 에러 처리
3. **반응형 디자인**: Desktop/Mobile 지원

---

## 설치된 컴포넌트

### 파일 구조

```
frontend/src/
├── types/
│   └── menu.ts                          # 메뉴 타입 정의
├── lib/
│   └── api/
│       └── menus.ts                     # 메뉴 API 클라이언트
├── components/
│   └── menus/
│       ├── MenuManager.tsx              # 관리자 메뉴 관리
│       ├── MenuTree.tsx                 # 트리 컴포넌트 (드래그&드롭)
│       ├── MenuForm.tsx                 # 메뉴 생성/수정 폼
│       ├── Navigation.tsx               # 사용자 네비게이션
│       ├── MobileDrawer.tsx             # 모바일 드로어 메뉴
│       └── index.ts                     # Export
└── app/
    ├── admin/
    │   └── menus/
    │       └── page.tsx                 # 관리자 메뉴 관리 페이지
    └── mypage/
        ├── layout.tsx                   # 마이페이지 레이아웃
        └── page.tsx                     # 마이페이지 홈
```

---

## 보안 원칙

### 1. XSS 방지

```typescript
// ❌ 절대 금지
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// ✅ React 기본 이스케이프 사용
<div>{userInput}</div>
```

### 2. URL 안전성 검증

```typescript
import { isSafeUrl } from '@/lib/api/menus'

// 사용 예시
if (!isSafeUrl(url)) {
  console.warn('Blocked unsafe URL:', url)
  return
}
```

### 3. 입력 검증

```typescript
import { validateMenuInput } from '@/lib/api/menus'

const errors = validateMenuInput(formData)
if (errors.length > 0) {
  setValidationErrors(errors)
  return
}
```

---

## 사용법

### 1. 관리자 메뉴 관리

```tsx
import { MenuManager } from '@/components/menus'

export default function AdminMenusPage() {
  return (
    <MenuManager
      menuType="user"
      title="사용자 메뉴 관리"
    />
  )
}
```

**기능:**
- 메뉴 트리 표시
- 드래그&드롭으로 순서/계층 변경
- 메뉴 생성/수정/삭제
- 실시간 미리보기

**접근:**
- URL: `/admin/menus`
- 권한: 관리자만

---

### 2. 데스크톱 네비게이션

```tsx
import { Navigation } from '@/components/menus'

export default function Sidebar() {
  return (
    <Navigation
      menuType="user"
      className="bg-white p-4 rounded-lg"
    />
  )
}
```

**특징:**
- 계층형 메뉴 구조
- 활성 메뉴 강조
- 배지/강조 표시 지원

---

### 3. 모바일 드로어 메뉴

```tsx
'use client'

import { useState } from 'react'
import { MobileDrawer } from '@/components/menus'

export default function MobileLayout() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button onClick={() => setIsOpen(true)}>
        메뉴 열기
      </button>

      <MobileDrawer
        menuType="user"
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </>
  )
}
```

**특징:**
- 좌측에서 슬라이드
- 백드롭 클릭/ESC로 닫기
- body 스크롤 잠금

---

### 4. 반응형 레이아웃 (통합 예시)

```tsx
'use client'

import { useState } from 'react'
import { Navigation, MobileDrawer } from '@/components/menus'

export default function MyPageLayout({ children }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <div>
      {/* 헤더 */}
      <header>
        <button
          onClick={() => setIsMobileMenuOpen(true)}
          className="lg:hidden"
        >
          메뉴
        </button>
      </header>

      <div className="flex gap-6">
        {/* 데스크톱 네비게이션 */}
        <aside className="hidden lg:block w-64">
          <Navigation menuType="user" />
        </aside>

        {/* 메인 컨텐츠 */}
        <main className="flex-1">
          {children}
        </main>
      </div>

      {/* 모바일 드로어 */}
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

## 컴포넌트 API

### MenuManager

관리자 메뉴 관리 컴포넌트

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| menuType | MenuType | ✅ | 메뉴 타입 ('user', 'admin', 'site' 등) |
| title | string | ❌ | 페이지 제목 (기본: '메뉴 관리') |

**MenuType:**
```typescript
type MenuType = 'site' | 'user' | 'admin' | 'header_utility' | 'footer_utility' | 'quick_menu'
```

---

### Navigation

데스크톱 네비게이션 컴포넌트

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| menuType | MenuType | ✅ | 메뉴 타입 |
| className | string | ❌ | 추가 CSS 클래스 |

**특징:**
- 자동으로 활성 메뉴만 표시 (is_active, is_visible, is_enabled)
- 권한 체크 자동 적용
- 로딩/에러 상태 처리

---

### MobileDrawer

모바일 드로어 메뉴 컴포넌트

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| menuType | MenuType | ✅ | 메뉴 타입 |
| isOpen | boolean | ✅ | 드로어 열림 상태 |
| onClose | () => void | ✅ | 닫기 콜백 |

**자동 기능:**
- ESC 키로 닫기
- 백드롭 클릭 시 닫기
- body 스크롤 잠금

---

## 커스터마이징

### 1. 메뉴 아이콘

```typescript
// 메뉴 생성 시
{
  icon: '🏠',           // 이모지
  // 또는
  icon: 'fa-home',     // Font Awesome 클래스
}
```

### 2. 배지 표시

```typescript
{
  badge_type: 'count',
  badge_value: '3',
  badge_color: '#3b82f6',
}
```

### 3. 강조 표시

```typescript
{
  highlight: true,
  highlight_text: 'NEW',
  highlight_color: '#ef4444',
}
```

### 4. CSS 커스터마이징

```typescript
{
  css_class: 'font-bold text-blue-600',
}
```

---

## API 엔드포인트

### 관리자 API

```
GET    /api/v1/admin/menus              # 메뉴 목록 (관리자)
GET    /api/v1/admin/menus/:id          # 메뉴 상세
POST   /api/v1/admin/menus              # 메뉴 생성
PUT    /api/v1/admin/menus/:id          # 메뉴 수정
DELETE /api/v1/admin/menus/:id          # 메뉴 삭제
PUT    /api/v1/admin/menus/:id/move     # 메뉴 이동
PUT    /api/v1/admin/menus/reorder      # 순서 변경
```

### 공개 API

```
GET    /api/v1/menus                    # 공개 메뉴 목록 (권한별 필터링)
```

---

## 드래그&드롭 기능

MenuTree 컴포넌트는 HTML5 드래그&드롭 API를 사용합니다.

**사용법:**
1. 메뉴 항목을 드래그
2. 다른 메뉴 위에 드롭
3. 자동으로 부모-자식 관계 변경 및 순서 저장

**제약사항:**
- 자기 자신에게 드롭 불가
- 순환 참조 방지 (백엔드에서 검증)

---

## 에러 처리

### 1. API 에러

모든 API 호출은 try-catch로 감싸져 있습니다.

```typescript
try {
  await createMenu(data)
  setSuccessMessage('메뉴가 추가되었습니다.')
} catch (err: any) {
  setError(err.message || '저장 중 오류가 발생했습니다.')
}
```

### 2. 폼 검증 에러

```typescript
const errors = validateMenuInput(formData)
if (errors.length > 0) {
  setValidationErrors(errors)
  return
}
```

### 3. 네트워크 에러

```typescript
if (error.code === 'ERR_NETWORK') {
  throw new Error('네트워크 연결을 확인해주세요.')
}
```

---

## 접근성 (Accessibility)

### 1. 키보드 네비게이션

- ESC: 드로어 닫기
- Enter/Space: 메뉴 선택

### 2. ARIA 속성

```tsx
<button aria-label="메뉴 열기">...</button>
<button aria-label="메뉴 닫기">...</button>
```

### 3. 포커스 관리

- 드로어 열릴 때 포커스 트랩
- 닫힐 때 이전 포커스 복원

---

## 성능 최적화

### 1. 메모이제이션

```typescript
const handleSelectMenu = useCallback((id: number) => {
  setSelectedId(id)
}, [])
```

### 2. 조건부 렌더링

```typescript
{isExpanded && hasChildren && (
  <ChildMenus />
)}
```

### 3. 로딩 상태

```tsx
{loading && <LoadingSkeleton />}
```

---

## 트러블슈팅

### 1. 메뉴가 표시되지 않음

**확인사항:**
- `is_active = true`
- `is_visible = true`
- `is_enabled = true`
- 권한 설정 확인

### 2. 드래그&드롭이 작동하지 않음

**확인사항:**
- HTML5 드래그 API 지원 브라우저
- 이벤트 핸들러 정상 등록 확인

### 3. 모바일 드로어가 열리지 않음

**확인사항:**
- `isOpen` state 관리 확인
- z-index 충돌 확인

---

## 다음 단계

1. **Backend API 연동**
   - FastAPI 메뉴 엔드포인트 구현
   - 권한 체크 미들웨어 추가

2. **고급 기능**
   - 메뉴 검색 기능
   - 일괄 편집
   - 메뉴 복제

3. **배포**
   - 환경변수 설정
   - 빌드 최적화

---

## 문의

이슈가 있거나 개선 사항이 있으면 GitHub Issue로 등록해주세요.
