from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from apis.practise_api.app.database import Base, get_db
from apis.practise_api.app.main import app
from apis.practise_api.app.config import get_settings
from apis.practise_api.app.ratelimiter import check_rate_limit
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

settings=get_settings()

async def override_rate_limit():
    pass

app.dependency_overrides[check_rate_limit]=override_rate_limit

TEST_DATABASE_URL="sqlite+aiosqlite:///./trading_test.db"

test_engine=create_async_engine(TEST_DATABASE_URL)

TestLocalSession=async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def override_get_db():
    async with TestLocalSession() as session:
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
        headers={'X-API-Key':settings.api_key}
    ) as ac:
        yield ac
