from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL_SQL = "sqlite+aiosqlite:///./coupon.db"

DATABSE_URL_POSTGRE = "postgre+asyncpg://user:password@localhost/coupon"

engine = create_async_engine(DATABASE_URL_SQL, echo=False)

AsycnLocalSession = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass
