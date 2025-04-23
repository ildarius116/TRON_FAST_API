from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class HistoryResponseSchema(BaseModel):
    address: str
    bandwidth: Optional[float]
    energy: Optional[float]
    balance: Optional[float]
    timestamp: datetime

    class Config:
        from_attributes = True


class HistoryResponseSchemas(BaseModel):
    page: int = Field(1, ge=1, le=100, description="Номер страницы")
    per_page: int = Field(10, ge=1, le=100, description="Элементов на странице")
    logs: Optional[List[HistoryResponseSchema]] = None
