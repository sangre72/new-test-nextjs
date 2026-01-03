"""
Social Authentication Configuration
OAuth2 providers: Kakao, Naver, Google

NOTE: This is configuration only. Actual implementation requires:
1. Install httpx: pip install httpx
2. Register OAuth apps with each provider
3. Set environment variables in .env
4. Implement callback endpoints in auth.py
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from app.core.config import settings


@dataclass
class OAuthProvider:
    """OAuth Provider configuration"""
    name: str
    client_id: Optional[str]
    client_secret: Optional[str]
    authorization_url: str
    token_url: str
    user_info_url: str
    scope: str


class SocialAuthConfig:
    """Social authentication configuration manager"""

    # Kakao OAuth
    KAKAO = OAuthProvider(
        name="kakao",
        client_id=settings.KAKAO_CLIENT_ID,
        client_secret=settings.KAKAO_CLIENT_SECRET,
        authorization_url="https://kauth.kakao.com/oauth/authorize",
        token_url="https://kauth.kakao.com/oauth/token",
        user_info_url="https://kapi.kakao.com/v2/user/me",
        scope="profile_nickname profile_image account_email"
    )

    # Naver OAuth
    NAVER = OAuthProvider(
        name="naver",
        client_id=settings.NAVER_CLIENT_ID,
        client_secret=settings.NAVER_CLIENT_SECRET,
        authorization_url="https://nid.naver.com/oauth2.0/authorize",
        token_url="https://nid.naver.com/oauth2.0/token",
        user_info_url="https://openapi.naver.com/v1/nid/me",
        scope="name email profile_image"
    )

    # Google OAuth
    GOOGLE = OAuthProvider(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
        scope="openid email profile"
    )

    @classmethod
    def get_provider(cls, provider_name: str) -> Optional[OAuthProvider]:
        """Get OAuth provider configuration by name"""
        providers = {
            "kakao": cls.KAKAO,
            "naver": cls.NAVER,
            "google": cls.GOOGLE
        }
        return providers.get(provider_name.lower())

    @classmethod
    def is_enabled(cls, provider_name: str) -> bool:
        """Check if provider is configured"""
        provider = cls.get_provider(provider_name)
        if not provider:
            return False
        return bool(provider.client_id and provider.client_secret)


# ============================================================================
# Social Login Implementation Guide
# ============================================================================

"""
구현 가이드:

1. .env 파일에 OAuth 정보 추가:
   KAKAO_CLIENT_ID=your_kakao_client_id
   KAKAO_CLIENT_SECRET=your_kakao_client_secret
   NAVER_CLIENT_ID=your_naver_client_id
   NAVER_CLIENT_SECRET=your_naver_client_secret
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret

2. auth.py에 엔드포인트 추가:

@router.get("/oauth/{provider}")
async def oauth_login(provider: str):
    # Redirect to OAuth provider
    config = SocialAuthConfig.get_provider(provider)
    if not config or not SocialAuthConfig.is_enabled(provider):
        raise HTTPException(400, "Provider not configured")

    # Generate authorization URL with state
    redirect_uri = "http://yourdomain.com/api/v1/auth/oauth/{provider}/callback"
    state = generate_random_state()  # Implement this

    auth_url = (
        f"{config.authorization_url}?"
        f"client_id={config.client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={config.scope}&"
        f"state={state}"
    )

    return {"authorization_url": auth_url}


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    # 1. Exchange code for access token
    # 2. Get user info from provider
    # 3. Create or update user in database
    # 4. Generate JWT tokens
    # 5. Return LoginResponse
    pass


3. 필요한 헬퍼 함수:

async def exchange_code_for_token(provider: OAuthProvider, code: str, redirect_uri: str) -> Dict[str, Any]:
    # Use httpx to exchange code for token
    pass

async def get_user_info_from_provider(provider: OAuthProvider, access_token: str) -> Dict[str, Any]:
    # Use httpx to get user info
    pass

def create_or_update_social_user(db: Session, provider: str, user_info: Dict) -> User:
    # Create or update user based on social login info
    pass


4. 필요한 Database 테이블 추가 (선택):

CREATE TABLE social_accounts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(20) NOT NULL,  -- kakao, naver, google
    provider_user_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(provider, provider_user_id)
);

CREATE INDEX idx_social_user ON social_accounts(user_id);
CREATE INDEX idx_social_provider ON social_accounts(provider, provider_user_id);
"""
