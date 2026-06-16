import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from apis.trading_api.app.main import app
from apis.trading_api.app.database import Base, get_db
from apis.trading_api.app.config import get_settings
from apis.trading_api.app.ratelimiter import check_rate_limit

# disable rate limiting in tests
async def override_rate_limit():
    pass    # do nothing — always allow

app.dependency_overrides[check_rate_limit] = override_rate_limit

settings = get_settings()

# separate test database — never touch production data
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_trading.db"

test_engine = create_async_engine(TEST_DATABASE_URL)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# replace real DB with test DB
app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    # create tables before each test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # drop tables after each test — clean slate
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": settings.api_key}
    ) as ac:
        yield ac