import os
import pytest_asyncio
from typing import Dict, Any
from dotenv import load_dotenv
from sqlalchemy import delete, NullPool
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker

from src.models.history import HistoryModel
from src.models.history import Base

load_dotenv()
DB_NAME = os.getenv('DB_NAME', "test_tron1")
DATABASE_URL = f"sqlite+aiosqlite:///./{DB_NAME}.db"

engine: AsyncEngine = create_async_engine(
    url=DATABASE_URL,
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
        print('BEFORE CREATE !!!!!!!!!!!!!!!!!')
        await conn.run_sync(Base.metadata.create_all)
        print('AFTER CREATE !!!!!!!!!!!!!!!!!')
    yield
    async with engine.begin() as conn:
        print('BEFORE DROP !!!!!!!!!!!!!!!!!')
        await conn.run_sync(Base.metadata.drop_all)
        print('AFTER DROP !!!!!!!!!!!!!!!!!')


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


@pytest_asyncio.fixture
async def mock_account_data():
    """
    Функция-фикстура
    """
    mock_account_data: Dict[str, Any] = {
        "address": "full_fields_address",
        "balance": 1000.0,
        "bandwidth": {"available": 50.0},
        "energy": {"available": 20.0}
    }
    return mock_account_data


@pytest_asyncio.fixture
async def history_test_data():
    """
    Функция-фикстура
    """
    history_data = [HistoryModel(address="full_fields_address",
                                 bandwidth=123.45,
                                 energy=67.89,
                                 balance=987.65
                                 ),
                    HistoryModel(address="full_fields_address",
                                 bandwidth=123.45,
                                 energy=67.89,
                                 balance=987.65
                                 ),
                    ]

    history_data = HistoryModel(address="full_fields_address",
                                bandwidth=123.45,
                                energy=67.89,
                                balance=987.65
                                )
    return history_data
