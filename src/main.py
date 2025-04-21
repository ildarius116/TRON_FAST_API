import uvicorn
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from src.database import init_db
from src.app import main_router


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
app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
