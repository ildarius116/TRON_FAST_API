from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class HistoryResponseSchema(BaseModel):
    address: str
    bandwidth: Optional[float]
    energy: Optional[float]
    balance: Optional[float]
    timestamp: datetime


class HistoryResponseSchemas(BaseModel):
    page: int
    per_page: int
    logs: List[HistoryResponseSchema]
