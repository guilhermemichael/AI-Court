from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.settings import get_settings

settings = get_settings()
engine_kwargs: dict[str, object] = {"pool_pre_ping": not settings.is_sqlite}
if settings.is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine: AsyncEngine = create_async_engine(settings.database_url, **engine_kwargs)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
