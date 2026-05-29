"""
Infraestrutura de banco de dados — SQLAlchemy 2.0 async com psycopg3.

Expõe:
- engine: AsyncEngine (singleton)
- async_session_factory: sessionmaker configurado
- get_db_session: generator para uso como dependência FastAPI
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from cam._shared.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependência FastAPI para sessão de banco de dados.

    Uso:
        @router.get("/")
        async def endpoint(session: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with async_session_factory() as session:
        yield session
