from typing import Optional
from pydantic import BaseModel


class AddressRequestSchema(BaseModel):
    address: str


class AddressResponseSchema(BaseModel):
    address: str
    bandwidth: Optional[float]
    energy: Optional[float]
    balance: Optional[float]

    class Config:
        from_attributes = True
