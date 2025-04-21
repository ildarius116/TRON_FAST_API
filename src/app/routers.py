import os
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from tronpy import Tron
from typing import Dict, Any
from dotenv import load_dotenv
from src.models.history import HistoryModel
from src.schemas.address import AddressRequestSchema, AddressResponseSchema
from src.schemas.history import HistoryResponseSchemas
from src.app.dependencies import PaginationDep, SessionDep

load_dotenv()
TRON_NETWORK = os.getenv('TRON_NETWORK', "shasta")

router = APIRouter()


@router.post(path="/address/",
             response_model=AddressResponseSchema,
             tags=["Получение данных TRON-кошельков"],
             summary="Запрос данных кошелька",
             )
async def get_address_info(request: AddressRequestSchema,
                           db_session: SessionDep,
                           ) -> Dict[str, Any]:
    """
    Функция - эндпоинт "/address/" запроса информации по адресу в сети "Трон"

    :параметр - address: Адрес кошелька \n
    :возврат: Словарь данных о кошельке
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

    log: HistoryModel = HistoryModel(
        address=address,
        bandwidth=bandwidth,
        energy=energy,
        balance=balance
    )

    # сохранение данных в БД
    db_session.add(log)
    await db_session.commit()

    return {
        "address": address,
        "bandwidth": bandwidth,
        "energy": energy,
        "balance": balance
    }


@router.get(path="/logs/",
            response_model=HistoryResponseSchemas,
            tags=["Получение данных TRON-кошельков"],
            summary="История запросов",
            )
async def get_logs(pagination: PaginationDep,
                   db_session: SessionDep,
                   ) -> Dict[str, Any]:
    """
    Функция - эндпоинт "/logs/" запроса информации по истории полученных данных из сети "Трон"

    :параметр - page: Номер страницы данных \n
    :параметр - per_page: Количество данных на одной странице \n
    :возврат: Пагинированный словарь данных истории запросов
    """
    # Офсет (смещение) списка данных
    offset: int = (pagination.page - 1) * pagination.per_page

    # запрос к БД с учетом смещения
    query = (select(HistoryModel).
             order_by(HistoryModel.timestamp.desc()).
             offset(offset).
             limit(pagination.per_page))
    result = await db_session.execute(query)
    logs = result.scalars().all()

    return {
        "page": pagination.page,
        "per_page": pagination.per_page,
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
