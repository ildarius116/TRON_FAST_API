from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any
from app.routers import router
from app.database import init_db
import logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """
    Функция асинхронного контекстного менеджера с инициализацией БД при старте
    """
    try:
        await init_db()
        yield
    except Exception as e:
        logging.error(f"Failed to initialize DB: {e}")
        raise


app = FastAPI(lifespan=lifespan)
app.include_router(router)
