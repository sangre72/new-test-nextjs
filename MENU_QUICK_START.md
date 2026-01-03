# 메뉴 관리 Frontend 빠른 시작

메뉴 관리 시스템을 5분 안에 시작하는 가이드입니다.

## 1단계: 관리자 페이지 접속

```bash
# 개발 서버 실행 (이미 실행 중이면 생략)
cd frontend
npm run dev
```

브라우저에서 접속:
```
http://localhost:3000/admin/menus
```

---

## 2단계: 첫 메뉴 추가

### 관리자 페이지에서:

1. **"+ 최상위 메뉴 추가"** 버튼 클릭

2. **기본 정보 입력:**
   - 메뉴 이름: `마이페이지`
   - 메뉴 코드: `mypage` (영문, 숫자, 언더스코어만)
   - 설명: `사용자 마이페이지`
   - 아이콘: `🏠` (이모지 또는 CSS 클래스)

3. **링크 설정:**
   - 링크 타입: `내부 URL`
   - URL: `/mypage`

4. **권한 설정:**
   - 권한 타입: `회원만`
   - 표시 조건: `로그인 시`

5. **"추가"** 버튼 클릭

---

## 3단계: 하위 메뉴 추가

1. 방금 만든 **"마이페이지"** 메뉴에 마우스 오버

2. **"+"** (하위 메뉴 추가) 버튼 클릭

3. **정보 입력:**
   - 메뉴 이름: `내 정보`
   - 메뉴 코드: `profile`
   - URL: `/mypage/profile`

4. **"추가"** 버튼 클릭

---

## 4단계: 사용자 페이지에서 확인

### 마이페이지 레이아웃 이미 적용됨

```
http://localhost:3000/mypage
```

**데스크톱:**
- 좌측에 네비게이션 메뉴 표시
- 메뉴 클릭으로 페이지 이동

**모바일:**
- 상단 메뉴 버튼 클릭
- 드로어 메뉴 열림
- 메뉴 선택 시 자동 닫힘

---

## 5단계: 드래그&드롭으로 순서 변경

1. 관리자 페이지로 돌아가기

2. 메뉴 항목을 **드래그**

3. 다른 메뉴 위에 **드롭**

4. 자동으로 순서 저장됨

---

## 완료!

이제 다음을 할 수 있습니다:

- ✅ 메뉴 추가/수정/삭제
- ✅ 드래그&드롭으로 순서/계층 변경
- ✅ 데스크톱 네비게이션
- ✅ 모바일 드로어 메뉴

---

## 추가 기능

### 배지 추가

```typescript
// 메뉴 수정 시
{
  badge_type: 'count',
  badge_value: '5',
  badge_color: '#3b82f6',
}
```

### 강조 표시 (NEW 배지)

```typescript
{
  highlight: true,
  highlight_text: 'NEW',
  highlight_color: '#ef4444',
}
```

### 숨김/비활성화

```typescript
{
  is_visible: false,  // 메뉴 숨김
  is_enabled: false,  // 비활성화 (클릭 불가)
}
```

---

## 다른 메뉴 타입

### 관리자 메뉴

```tsx
<MenuManager menuType="admin" title="관리자 메뉴" />
```

### 헤더 유틸리티 메뉴

```tsx
<Navigation menuType="header_utility" />
```

### 푸터 메뉴

```tsx
<Navigation menuType="footer_utility" />
```

---

## 컴포넌트 사용법

### 1. 관리자 페이지

```tsx
import { MenuManager } from '@/components/menus'

export default function AdminPage() {
  return <MenuManager menuType="user" />
}
```

### 2. 데스크톱 네비게이션

```tsx
import { Navigation } from '@/components/menus'

export default function Sidebar() {
  return <Navigation menuType="user" />
}
```

### 3. 모바일 드로어

```tsx
'use client'

import { useState } from 'react'
import { MobileDrawer } from '@/components/menus'

export default function Layout() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button onClick={() => setIsOpen(true)}>메뉴</button>
      <MobileDrawer
        menuType="user"
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </>
  )
}
```

---

## 파일 위치

```
frontend/src/
├── types/menu.ts                        # 타입 정의
├── lib/api/menus.ts                     # API 클라이언트
├── components/menus/                    # 메뉴 컴포넌트
│   ├── MenuManager.tsx                  # 관리자 페이지
│   ├── Navigation.tsx                   # 데스크톱 네비게이션
│   ├── MobileDrawer.tsx                 # 모바일 드로어
│   └── index.ts
└── app/
    ├── admin/menus/page.tsx             # /admin/menus
    └── mypage/layout.tsx                # /mypage 레이아웃
```

---

## 보안 체크리스트

- ✅ XSS 방지: React 기본 이스케이프 사용
- ✅ URL 검증: `isSafeUrl()` 함수로 검증
- ✅ 입력 검증: `validateMenuInput()` 사용
- ✅ 에러 처리: 모든 API 호출에 try-catch
- ✅ 권한 체크: 백엔드에서 검증

---

## 문제 해결

### 메뉴가 안 보여요

1. 메뉴 상태 확인:
   - `is_active = true`
   - `is_visible = true`
   - `is_enabled = true`

2. 권한 확인:
   - 로그인 상태와 `show_condition` 일치
   - `permission_type` 확인

### 드래그가 안 돼요

- 브라우저 HTML5 드래그 API 지원 확인
- 최신 브라우저 사용 권장

### API 연결이 안 돼요

- Backend API 서버 실행 확인
- `.env.local` 파일에서 `NEXT_PUBLIC_API_URL` 설정 확인

---

## 다음 단계

자세한 내용은 [MENU_FRONTEND_README.md](./MENU_FRONTEND_README.md)를 참고하세요.
