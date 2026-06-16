from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL_sqlite="sqlite+aiosqlite:///./trading.db"
DATABASE_URL_postgre="postgresql+asyncpg://user:password@localhost/trading"

engine=create_async_engine(DATABASE_URL_sqlite,echo=False)

AsyncLocalSession=async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass