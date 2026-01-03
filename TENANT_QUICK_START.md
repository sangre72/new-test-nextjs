# 테넌트 관리 시스템 빠른 시작 가이드

## 5분 안에 시작하기

### 1. 기본 테넌트 생성

```bash
# API 호출
curl -X POST http://localhost:8000/api/v1/admin/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_code": "acme",
    "tenant_name": "ACME Corporation",
    "admin_email": "admin@acme.com"
  }'
```

응답:
```json
{
  "id": 2,
  "tenant_code": "acme",
  "tenant_name": "ACME Corporation",
  "is_active": true,
  "status": "active"
}
```

### 2. 테넌트 목록 조회

```bash
curl http://localhost:8000/api/v1/admin/tenants
```

### 3. 현재 테넌트 정보 조회

```bash
# 헤더로 테넌트 지정
curl -H "X-Tenant-Code: acme" \
  http://localhost:8000/api/v1/tenants/current/info
```

응답:
```json
{
  "tenant_id": 2,
  "tenant_code": "acme",
  "tenant_name": "ACME Corporation",
  "settings": {}
}
```

### 4. 테넌트 설정 수정

```bash
curl -X PATCH http://localhost:8000/api/v1/admin/tenants/2/settings \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "dark",
    "language": "en",
    "primaryColor": "#1976d2",
    "companyName": "ACME Corp"
  }'
```

---

## 도메인 설정

### 서브도메인 접근

```bash
# 테넌트 생성 시 서브도메인 지정
curl -X POST http://localhost:8000/api/v1/admin/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_code": "acme",
    "tenant_name": "ACME Corporation",
    "subdomain": "acme"
  }'

# 이제 http://acme.localhost:8000 으로 접근 가능
# (localhost 테스트용, 실제 환경에서는 acme.example.com)
```

### 커스텀 도메인 접근

```bash
# 테넌트 생성 시 도메인 지정
curl -X POST http://localhost:8000/api/v1/admin/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_code": "acme",
    "tenant_name": "ACME Corporation",
    "domain": "acme.com"
  }'

# 이제 http://acme.com 으로 접근 가능
```

---

## Frontend 사용

### 1. 관리자 페이지 라우트 추가

```typescript
// app/admin/tenants/page.tsx
import TenantManager from '@/components/admin/TenantManager'

export default function TenantsPage() {
  return <TenantManager />
}
```

### 2. 현재 테넌트 정보 표시

```typescript
import { fetchCurrentTenant } from '@/lib/api/tenants'

export default function Header() {
  const [tenant, setTenant] = useState(null)

  useEffect(() => {
    fetchCurrentTenant().then(setTenant)
  }, [])

  return (
    <header>
      <h1>{tenant?.tenant_name || 'Loading...'}</h1>
      <span>{tenant?.tenant_code}</span>
    </header>
  )
}
```

### 3. 테넌트별 메뉴 표시

```typescript
import api from '@/lib/api'

export default function Menu() {
  const [menus, setMenus] = useState([])

  useEffect(() => {
    // 현재 테넌트의 메뉴만 조회됨
    api.get('/menus').then(res => setMenus(res.data))
  }, [])

  return (
    <nav>
      {menus.map(menu => (
        <a key={menu.id} href={menu.menu_url}>{menu.menu_name}</a>
      ))}
    </nav>
  )
}
```

---

## API 요청 헤더

### 테넌트 지정 방법

1. **X-Tenant-Code 헤더** (API 호출)
```bash
curl -H "X-Tenant-Code: acme" http://localhost:8000/api/v1/menus
```

2. **서브도메인** (웹 접근)
```
http://acme.localhost:8000
```

3. **커스텀 도메인** (프로덕션)
```
http://acme.com
```

4. **기본값** (헤더/도메인 미지정)
```
기본 테넌트 사용 (tenant_code = 'default')
```

---

## 데이터베이스 쿼리

### 테넌트 조회

```sql
-- 활성 테넌트만 조회
SELECT * FROM tenants WHERE is_active = TRUE AND is_deleted = FALSE;

-- 특정 테넌트
SELECT * FROM tenants WHERE tenant_code = 'acme';

-- 도메인으로 조회
SELECT * FROM tenants WHERE domain = 'acme.com';

-- 서브도메인으로 조회
SELECT * FROM tenants WHERE subdomain = 'acme';
```

### 테넌트별 사용자 조회

```sql
-- ACME 테넌트의 모든 사용자
SELECT u.* FROM users u
JOIN tenants t ON u.tenant_id = t.id
WHERE t.tenant_code = 'acme';

-- 테넌트별 사용자 수
SELECT t.tenant_code, COUNT(u.id) as user_count
FROM tenants t
LEFT JOIN users u ON t.id = u.tenant_id
GROUP BY t.id, t.tenant_code;
```

---

## 일반적인 작업

### 테넌트 비활성화

```bash
curl -X PATCH http://localhost:8000/api/v1/admin/tenants/2 \
  -H "Content-Type: application/json" \
  -d '{"status": "inactive"}'
```

### 테넌트 일시 중지

```bash
curl -X PATCH http://localhost:8000/api/v1/admin/tenants/2 \
  -H "Content-Type: application/json" \
  -d '{"status": "suspended"}'
```

### 테넌트 삭제

```bash
curl -X DELETE http://localhost:8000/api/v1/admin/tenants/2
```

참고: 기본 테넌트(default)는 삭제할 수 없습니다.

---

## 트러블슈팅

### 테넌트를 찾을 수 없음

```bash
# 데이터베이스에서 확인
docker exec postgres psql -U postgres -d app -c "SELECT * FROM tenants;"

# 기본 테넌트 확인
docker exec postgres psql -U postgres -d app -c \
  "SELECT * FROM tenants WHERE tenant_code = 'default';"
```

### 헤더가 작동하지 않음

```bash
# 헤더를 명시적으로 전달하는지 확인
curl -v -H "X-Tenant-Code: acme" http://localhost:8000/api/v1/tenants/current/info

# 응답 헤더 확인
curl -i http://localhost:8000/api/v1/tenants/current/info
```

### 도메인 충돌

```sql
-- 중복 도메인 확인
SELECT domain, COUNT(*) FROM tenants
WHERE domain IS NOT NULL
GROUP BY domain
HAVING COUNT(*) > 1;
```

---

## 다음 단계

1. **사용자 관리**: `/api/v1/users` 엔드포인트로 사용자 생성
2. **권한 관리**: 역할 및 권한 설정
3. **메뉴 관리**: 테넌트별 메뉴 구성
4. **게시판 생성**: 테넌트별 게시판 설정

---

## 실용적인 예제

### 전체 플로우

```bash
# 1. 새로운 고객(테넌트) 생성
TENANT_ID=$(curl -X POST http://localhost:8000/api/v1/admin/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_code": "customer1",
    "tenant_name": "Customer One",
    "domain": "customer1.com",
    "admin_email": "admin@customer1.com",
    "admin_name": "Admin User",
    "settings": {
      "theme": "light",
      "language": "ko",
      "companyName": "Customer One Inc.",
      "primaryColor": "#007bff"
    }
  }' | jq '.id')

echo "Created tenant: $TENANT_ID"

# 2. 테넌트 관리자 추가
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d "{
    \"tenant_id\": $TENANT_ID,
    \"username\": \"admin\",
    \"email\": \"admin@customer1.com\",
    \"password\": \"securepassword123\",
    \"full_name\": \"Admin User\",
    \"is_superuser\": true
  }"

# 3. 테넌트 설정 커스터마이징
curl -X PATCH http://localhost:8000/api/v1/admin/tenants/$TENANT_ID/settings \
  -H "Content-Type: application/json" \
  -d '{
    "logo": "https://customer1.com/logo.png",
    "favicon": "https://customer1.com/favicon.ico"
  }'

# 4. 현재 테넌트로 접근
curl -H "X-Tenant-Code: customer1" \
  http://localhost:8000/api/v1/tenants/current/info
```

### Python 클라이언트 예제

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

class TenantClient:
    def __init__(self, tenant_code: str):
        self.tenant_code = tenant_code
        self.headers = {"X-Tenant-Code": tenant_code}

    def get_info(self):
        """현재 테넌트 정보 조회"""
        r = requests.get(f"{BASE_URL}/tenants/current/info", headers=self.headers)
        return r.json()

    def get_menus(self):
        """테넌트의 메뉴 조회"""
        r = requests.get(f"{BASE_URL}/menus", headers=self.headers)
        return r.json()

    def get_users(self):
        """테넌트의 사용자 조회"""
        r = requests.get(f"{BASE_URL}/users", headers=self.headers)
        return r.json()

# 사용
client = TenantClient("acme")
print(client.get_info())
print(client.get_menus())
```

### JavaScript/TypeScript 예제

```typescript
import { fetchCurrentTenant, fetchTenants } from '@/lib/api/tenants'
import api from '@/lib/api'

// 현재 테넌트 정보
const currentTenant = await fetchCurrentTenant()
console.log(currentTenant)

// 모든 테넌트 조회 (관리자)
const allTenants = await fetchTenants(0, 100)
console.log(allTenants)

// 헤더로 테넌트 지정
api.defaults.headers.common['X-Tenant-Code'] = 'acme'
const menus = await api.get('/menus')
console.log(menus.data)
```

---

## 성능 최적화

### 캐싱

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_tenant_settings(tenant_code: str):
    """테넌트 설정 캐싱"""
    return service.get_by_code(tenant_code).settings
```

### 데이터베이스 인덱스

이미 생성됨:
- `idx_tenant_code`
- `idx_domain`
- `idx_subdomain`
- `idx_status`

---

## 체크리스트

- [ ] 기본 테넌트 생성 확인
- [ ] API 엔드포인트 테스트
- [ ] 헤더로 테넌트 지정 테스트
- [ ] 서브도메인 접근 테스트
- [ ] 관리자 UI 페이지 추가
- [ ] 현재 테넌트 정보 표시
- [ ] 권한 설정
- [ ] 프로덕션 배포

---

문의사항이 있으시면 설명서를 참고하세요: `TENANT_MANAGER_SETUP.md`
