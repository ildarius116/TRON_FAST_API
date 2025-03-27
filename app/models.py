from sqlalchemy import Column, String, Float, TIMESTAMP, func, Integer
from sqlalchemy.orm import declarative_base
from typing import Optional
from datetime import datetime

Base = declarative_base()


class RequestLog(Base):
    __tablename__ = 'request_logs'

    id: int = Column(Integer, primary_key=True)
    address: str = Column(String(42), nullable=False)
    bandwidth: Optional[float] = Column(Float)
    energy: Optional[float] = Column(Float)
    balance: Optional[float] = Column(Float)
    timestamp: datetime = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self) -> str:
        return f"<RequestLog(id={self.id}, address={self.address})>"
