import pytest_asyncio
from sqlalchemy import delete, NullPool
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker

from src.models.history import HistoryModel
from src.models.history import Base

engine: AsyncEngine = create_async_engine(
    url="sqlite+aiosqlite:///./tron_test.db",
    poolclass=NullPool,
    echo=True
)

async_session = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)


@pytest_asyncio.fixture(scope="module")
async def test_db():
    """
    Функция-фикстура инициализации и очистка тестовой БД
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_db_session(test_db) -> AsyncSession:
    """
    Функция-фикстура асинхронной сессии
    """
    async with async_session() as session:
        yield session
        await session.close()


@pytest_asyncio.fixture
async def clean_db(test_db_session: AsyncSession):
    """
    Функция-фикстура очистки БД перед тестом
    """
    await test_db_session.execute(delete(HistoryModel))
    await test_db_session.commit()
    yield
