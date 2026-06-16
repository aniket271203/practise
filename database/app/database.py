from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL="sqlite+aiosqlite:///./test.db"
engine=create_async_engine(DATABASE_URL,echo=False)

AsyncLocalSession=async_sessionmaker(
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