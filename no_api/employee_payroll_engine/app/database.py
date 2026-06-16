from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL='sqlite+aiosqlite:///./employee_payroll.db'

engine=create_async_engine(DATABASE_URL,echo=False)

AsyncLocalSession=async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass