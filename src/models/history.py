from sqlalchemy import Column, String, Float, TIMESTAMP, func, Integer
from sqlalchemy.orm import declarative_base
from typing import Optional
from datetime import datetime

from src.schemas.history import HistoryResponseSchema

Base = declarative_base()


class HistoryModel(Base):
    __tablename__ = 'history'

    id: int = Column(Integer, primary_key=True)
    address: str = Column(String(42), nullable=False)
    bandwidth: Optional[float] = Column(Float)
    energy: Optional[float] = Column(Float)
    balance: Optional[float] = Column(Float)
    timestamp: datetime = Column(TIMESTAMP, server_default=func.now())

    def to_read_model(self):
        return HistoryResponseSchema(
            id=self.id,
            address=self.address,
            bandwidth=self.bandwidth,
            energy=self.energy,
            balance=self.balance,
            timestamp=self.timestamp,
        )

    def __repr__(self) -> str:
        return f"<History(id={self.id}, address={self.address})>"
