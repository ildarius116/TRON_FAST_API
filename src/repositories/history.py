from src.utils.repository import SQLAlchemyRepository
from src.models.history import HistoryModel


class HistoryRepo(SQLAlchemyRepository):
    model = HistoryModel
