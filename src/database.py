import os
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
from typing import AsyncGenerator


class Base(DeclarativeBase):
    pass


load_dotenv()
DB_NAME = os.getenv('DB_NAME', "tron")
DATABASE_URL = f"sqlite+aiosqlite:///./{DB_NAME}.db"
DEBUG = os.getenv('DEBUG', 'False')

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=eval(DEBUG)
)

async_session = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Функция-генератор асинхронных сессий.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Функция инициализации (создания) таблицы
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """
    Функция удаления всех таблиц
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
