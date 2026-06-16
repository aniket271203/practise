from sqlalchemy.ext.asyncio import AsyncSession,create_async_engine,async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL_SQL='sqlite+aiosqlite:///./warhouse.db'
DATABASE_URL_POSTGRE='postgresql+aysncpg://user:password@localhost/warhouse'

engine=create_async_engine(DATABASE_URL_SQL,echo=False)

AsyncLocalSession=async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass
