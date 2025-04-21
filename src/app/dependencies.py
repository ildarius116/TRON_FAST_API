from typing import Annotated
from fastapi import Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session


class PaginationSchema(BaseModel):
    page: int = Field(1, ge=1, le=100, description="Номер страницы")
    per_page: int = Field(10, ge=1, le=100, description="Элементов на странице")


PaginationDep = Annotated[PaginationSchema, Depends(PaginationSchema)]
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
