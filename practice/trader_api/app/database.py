from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from apis.trader_api.app.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=settings.debug)

AsyncLocalSession = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncLocalSession() as session:
        try:
            yield session
        finally:
            await session.close()
