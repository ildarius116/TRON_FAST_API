import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session, init_db, drop_db
from src.models.history import HistoryModel


@pytest_asyncio.fixture(scope="module")
async def test_db():
    """
    Функция-фикстура инициализации и очистка тестовой БД
    """
    await init_db()
    yield
    await drop_db()


@pytest_asyncio.fixture
async def db_session(test_db) -> AsyncSession:
    """
    Функция-фикстура асинхронной сессии
    """
    async with async_session() as session:
        yield session
        await session.close()


@pytest_asyncio.fixture
async def clean_db(db_session: AsyncSession):
    """
    Функция-фикстура очистки БД перед тестом
    """
    await db_session.execute(delete(HistoryModel))
    await db_session.commit()
    yield
