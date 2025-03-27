import os
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
from typing import AsyncGenerator
from app.models import Base

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', "sqlite+aiosqlite:///./test.db")
DEBUG = os.getenv('DEBUG', False)

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=eval(DEBUG)
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Функция-генератор асинхронных сессий.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# 6. Инициализация БД (для lifespan)
async def init_db() -> None:
    """
    Функция создает все таблицы при старте приложения
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """Функция уУдаления всех таблиц (для тестов)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
