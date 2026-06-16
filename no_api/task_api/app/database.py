from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

DATABASE_URL_SQL = "sqlite+aiosqlite:///./trading.db"
DATABASE_URL_POSTGRE = "postgre+asyncpg://user:password@localhost/trading"

engine = create_async_engine(DATABASE_URL_SQL, echo=False)

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
