import os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tronpy import Tron
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from app.models import RequestLog
from app.database import get_db

load_dotenv()
TRON_NETWORK = os.getenv('TRON_NETWORK', "shasta")

router = APIRouter()


class AddressRequest(BaseModel):
    address: str


class AddressResponse(BaseModel):
    address: str
    bandwidth: Optional[float]
    energy: Optional[float]
    balance: Optional[float]


class LogResponse(BaseModel):
    address: str
    bandwidth: Optional[float]
    energy: Optional[float]
    balance: Optional[float]
    timestamp: datetime


class LogsResponse(BaseModel):
    page: int
    per_page: int
    logs: List[LogResponse]  # Используем уже существующую LogResponse


@router.post("/address/", response_model=AddressResponse)
async def get_address_info(request: AddressRequest,
                           db: AsyncSession = Depends(get_db)
                           ) -> Dict[str, Any]:
    """
    Функция - эндпоинт "/address/" запроса информации по адресу в сети "Трон"

    :param request: Запрос, содержащий искомый адрес
    :param db: БД для хранения результатов запроса
    :return: Словарь данных о кошельке
    """
    # проверка (валидация) адреса
    address: str = request.address.strip()
    client: Tron = Tron(network='shasta')

    if not client.is_address(address):
        raise HTTPException(status_code=400, detail="Invalid address")

    # попытка получить аккаунт
    try:
        account: Dict[str, Any] = client.get_account(address)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # обработка полученных данных
    balance: float = account.get('balance', 0.0)
    bandwidth: float = account.get('bandwidth', {}).get('available', 0.0)
    energy: float = account.get('energy', {}).get('available', 0.0)

    log: RequestLog = RequestLog(
        address=address,
        bandwidth=bandwidth,
        energy=energy,
        balance=balance
    )

    # сохранение данных в БД
    db.add(log)
    await db.commit()
    await db.refresh(log)

    return {
        "address": address,
        "bandwidth": bandwidth,
        "energy": energy,
        "balance": balance
    }


@router.get("/logs/", response_model=LogsResponse)
async def get_logs(page: int = 1,
                   per_page: int = 10,
                   db: AsyncSession = Depends(get_db)
                   ) -> Dict[str, Any]:
    """
    Функция - эндпоинт "/logs/" запроса информации по истории (Логам) полученных данных из сети "Трон"

    :param page: номер текущей страницы отображения данных
    :param per_page: количество (элементов) данных на одной странице
    :param db: БД для хранения результатов запроса
    :return: Пагинированный словарь данных Логов
    """
    # Офсет (смещение) списка данных
    skip: int = (page - 1) * per_page

    # запрос к БД с учетом смещения
    result = await db.execute(select(RequestLog).order_by(RequestLog.timestamp.desc()).offset(skip).limit(per_page))
    logs = result.scalars().all()

    return {
        "page": page,
        "per_page": per_page,
        "logs": [
            {
                "address": log.address,
                "bandwidth": log.bandwidth,
                "energy": log.energy,
                "balance": log.balance,
                "timestamp": log.timestamp
            } for log in logs
        ]
    }
