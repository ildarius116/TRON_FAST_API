from src.schemas.history import HistoryResponseSchemas
from src.utils.repository import AbstractRepository


class HistoryService:
    def __init__(self, history_repository: AbstractRepository):
        self.history_repository: AbstractRepository = history_repository()

    async def add_history(self, account: dict) -> int:
        account_dict = {'address': account.get('address', ''),
                        'balance': account.get('balance', 0.0),
                        'bandwidth': account.get('bandwidth', {}).get('available', 0.0),
                        'energy': account.get('energy', {}).get('available', 0.0),
                        }
        history_id = await self.history_repository.add_one(account_dict)
        return history_id

    async def get_history_one(self, history_id: int):
        history_dict = await self.history_repository.get_one(history_id)
        return history_dict

    async def get_history_paginated(self, history: HistoryResponseSchemas):
        history_dict = history.model_dump()
        history_list = await self.history_repository.get_all(**history_dict)
        history.logs = history_list
        return history
