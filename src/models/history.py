from sqlalchemy import String, TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional
from datetime import datetime

from src.schemas.history import HistoryResponseSchema
from src.database import Base


class HistoryModel(Base):
    __tablename__ = 'history'

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(42), nullable=False)
    bandwidth: Mapped[Optional[float]]
    energy: Mapped[Optional[float]]
    balance: Mapped[Optional[float]]
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

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
