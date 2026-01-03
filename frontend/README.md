# Frontend - Next.js

Next.js 16 기반 프론트엔드 애플리케이션

## 빠른 시작

### 1. 의존성 설치

```bash
npm install
# 또는
yarn install
# 또는
pnpm install
```

### 2. 환경 변수 설정

```bash
# .env.local 파일 생성
cp .env.local.example .env.local

# .env.local 파일 편집
nano .env.local
```

### 3. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 http://localhost:3000 접속

## 프로젝트 구조

```
frontend/
├── src/
│   ├── app/              # App Router (Next.js 13+)
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx      # Home page
│   │   ├── providers.tsx # React Query provider
│   │   └── globals.css   # Global styles
│   ├── components/       # React components
│   ├── lib/             # Utilities
│   │   ├── api.ts       # Axios instance
│   │   └── utils.ts     # Helper functions
│   └── types/           # TypeScript types
├── public/              # Static files
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## 기술 스택

- **React**: 19.2.3
- **Next.js**: 16.1.1 (App Router)
- **TypeScript**: 5.7.3
- **TanStack Query**: 5.90.16 (React Query v5)
- **Tailwind CSS**: 3.4.17
- **Axios**: 1.7.9

## 개발 가이드

### 새 페이지 추가

App Router 사용 (Next.js 13+):

```tsx
// src/app/about/page.tsx
export default function AboutPage() {
  return (
    <div>
      <h1>About Page</h1>
    </div>
  )
}
```

### API 호출 (React Query)

```tsx
'use client'

import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '@/lib/api'

export default function ItemsPage() {
  // GET request
  const { data, isLoading, error } = useQuery({
    queryKey: ['items'],
    queryFn: async () => {
      const response = await api.get('/items')
      return response.data
    },
  })

  // POST request
  const createMutation = useMutation({
    mutationFn: async (newItem: any) => {
      const response = await api.post('/items', newItem)
      return response.data
    },
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['items'] })
    },
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <div>
      {data?.map((item: any) => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  )
}
```

### 컴포넌트 생성

```tsx
// src/components/Button.tsx
import { cn } from '@/lib/utils'

interface ButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary'
  onClick?: () => void
}

export function Button({ children, variant = 'primary', onClick }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'px-4 py-2 rounded-lg font-medium transition-colors',
        variant === 'primary' && 'bg-blue-500 hover:bg-blue-600 text-white',
        variant === 'secondary' && 'bg-gray-200 hover:bg-gray-300 text-gray-800'
      )}
    >
      {children}
    </button>
  )
}
```

### TypeScript 타입 정의

```typescript
// src/types/item.ts
export interface Item {
  id: number
  name: string
  description: string
  createdAt: string
}

export interface ItemCreate {
  name: string
  description: string
}
```

### API 클라이언트 사용

```typescript
// src/lib/api/items.ts
import { api } from '@/lib/api'
import type { Item, ItemCreate } from '@/types/item'

export const itemsApi = {
  getAll: async (): Promise<Item[]> => {
    const response = await api.get('/items')
    return response.data
  },

  getById: async (id: number): Promise<Item> => {
    const response = await api.get(`/items/${id}`)
    return response.data
  },

  create: async (data: ItemCreate): Promise<Item> => {
    const response = await api.post('/items', data)
    return response.data
  },

  update: async (id: number, data: Partial<ItemCreate>): Promise<Item> => {
    const response = await api.put(`/items/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/items/${id}`)
  },
}
```

## 스크립트

```bash
# 개발 서버
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 서버
npm run start

# 린트 검사
npm run lint

# 타입 체크
npm run type-check
```

## 환경 변수

`.env.local` 파일에 필요한 환경 변수:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_AUTH_STORAGE_KEY=auth_token
```

환경 변수 이름은 `NEXT_PUBLIC_` 접두사로 시작해야 브라우저에서 접근 가능합니다.

## Tailwind CSS

### 커스텀 색상 사용

```tsx
<div className="bg-primary-500 text-white">
  Primary color
</div>
```

### 반응형 디자인

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {/* Responsive grid */}
</div>
```

## 트러블슈팅

### API 호출 실패

1. Backend 서버가 실행 중인지 확인
2. `.env.local`에서 `NEXT_PUBLIC_API_URL` 확인
3. CORS 설정 확인 (backend/.env의 `BACKEND_CORS_ORIGINS`)

### 빌드 에러

```bash
# 캐시 삭제
rm -rf .next node_modules

# 재설치
npm install

# 빌드
npm run build
```

### 타입 에러

```bash
# 타입 체크
npm run type-check

# TypeScript 서버 재시작 (VSCode)
Cmd+Shift+P -> "TypeScript: Restart TS Server"
```

## 다음 단계

1. 인증 UI 추가: `Use auth-frontend --init`
2. 메뉴 컴포넌트 추가: `Use menu-frontend --init`
3. 게시판 UI 추가: `Use board-generator --template notice`

## 참고 자료

- [Next.js 문서](https://nextjs.org/docs)
- [TanStack Query 문서](https://tanstack.com/query/latest)
- [Tailwind CSS 문서](https://tailwindcss.com/docs)
