from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from apis.order_management_api.app.database import get_db, Base
from apis.order_management_api.app.main import app
from apis.order_management_api.app.ratelimiter import check_rate_limit
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from apis.order_management_api.app.config import get_settings

settings=get_settings()

DATABASE_URL="sqlite+aiosqlite:///./tes_orders.db"

def override_rate_limiter():
    pass 

app.dependency_overrides[check_rate_limit]=override_rate_limiter

test_engine=create_async_engine(DATABASE_URL)

AsyncTestSession=async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit= False
)

async def override_get_db():
    async with AsyncTestSession() as session:
        try:
            yield session 
        finally:
            await session.close()

app.dependency_overrides[get_db]=override_get_db

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key":settings.api_key}
        ) as ac:
        yield ac