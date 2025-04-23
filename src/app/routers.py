import os
from fastapi import APIRouter, HTTPException
from tronpy import AsyncTron
from typing import Dict, Any
from dotenv import load_dotenv

from src.repositories.history import HistoryRepo
from src.schemas.address import AddressRequestSchema, AddressResponseSchema
from src.schemas.history import HistoryResponseSchemas
from src.services.history import HistoryService

load_dotenv()
TRON_NETWORK = os.getenv('TRON_NETWORK', "shasta")

router = APIRouter()


async def get_tron_account(network, address):
    """
    Функция получения ТРОН-аккаунта

    :param network:
    :param address:
    :return:
    """
    async with AsyncTron(network=network) as client:
        # проверка (валидация) адреса
        if not client.is_address(address):
            raise HTTPException(status_code=400, detail="Invalid address")

        # попытка получить аккаунт
        try:
            account: Dict[str, Any] = await client.get_account(address)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        return account


@router.post(path="/address/",
             response_model=AddressResponseSchema,
             tags=["Получение данных TRON-кошельков"],
             summary="Запрос данных кошелька",
             )
async def get_address_info(request: AddressRequestSchema) -> Dict[str, Any]:
    """
    Функция - эндпоинт "/address/" запроса информации по адресу в сети "Трон"

    :параметр - address: Адрес кошелька \n
    :возврат: Словарь данных о кошельке
    """

    address: str = request.address.strip()
    account = await get_tron_account(TRON_NETWORK, address)
    history_id = await HistoryService(HistoryRepo).add_history(account)
    history_dict = await HistoryService(HistoryRepo).get_history_one(history_id)
    return history_dict


@router.get(path="/logs/",
            response_model=HistoryResponseSchemas,
            tags=["Получение данных TRON-кошельков"],
            summary="История запросов",
            )
async def get_logs() -> Dict[str, Any]:
    """
    Функция - эндпоинт "/logs/" запроса информации по истории полученных данных из сети "Трон"

    :параметр - page: Номер страницы данных \n
    :параметр - per_page: Количество данных на одной странице \n
    :возврат: Пагинированный словарь данных истории запросов
    """
    history_dict = await HistoryService(HistoryRepo).get_history_paginated(HistoryResponseSchemas())
    return history_dict
