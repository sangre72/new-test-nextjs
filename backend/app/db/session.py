"""
Database Session Management (SQLAlchemy 2.0 + AsyncIO)

AsyncSession을 사용하여 비동기 데이터베이스 작업을 지원합니다.
PostgreSQL + asyncpg를 사용합니다.

사용법:
    from app.db.session import AsyncSessionLocal, engine

    # 비동기 세션 사용
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings
from typing import AsyncGenerator

# 비동기 엔진 생성
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=0,
    poolclass=NullPool if settings.ENVIRONMENT == "test" else None,
)

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    의존성 주입용 세션 제공자

    Usage:
        @app.get("/users")
        async def list_users(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
