"""
Application Configuration (Pydantic Settings v2)

환경 변수를 통해 설정을 관리합니다.
.env 파일에서 자동으로 로드됩니다.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application Settings

    환경 변수 우선순위:
    1. .env 파일
    2. 시스템 환경 변수
    3. 기본값
    """

    # ========== 애플리케이션 ==========
    APP_NAME: str = "New Test API"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # ========== 데이터베이스 ==========
    DATABASE_URL: str
    SQL_ECHO: bool = False  # SQL 쿼리 로깅 (개발 환경에서만 True)

    # ========== Redis ==========
    REDIS_URL: Optional[str] = None

    # ========== JWT ==========
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_IN: int = 3600  # 1시간 (초)
    JWT_REFRESH_EXPIRES_IN: int = 604800  # 7일 (초)

    # ========== SMS (프로덕션 전용) ==========
    SMS_API_KEY: Optional[str] = None
    SMS_SENDER_NUMBER: Optional[str] = None

    # ========== 소셜 로그인 ==========
    KAKAO_CLIENT_ID: Optional[str] = None
    KAKAO_CLIENT_SECRET: Optional[str] = None
    NAVER_CLIENT_ID: Optional[str] = None
    NAVER_CLIENT_SECRET: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # ========== 개발 모드 ==========
    DEV_MODE: bool = True
    DEV_VERIFICATION_CODE: str = "000000"

    # ========== CORS ==========
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS Origins를 리스트로 변환"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


# 글로벌 설정 인스턴스
settings = Settings()
