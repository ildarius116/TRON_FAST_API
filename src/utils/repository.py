from abc import ABC, abstractmethod

from sqlalchemy import select, insert
from src.database import async_session


class AbstractRepository(ABC):
    model = None

    @abstractmethod
    async def add_one(self, *args, **kwargs):
        raise NotImplemented

    @abstractmethod
    async def get_one(self, *args, **kwargs):
        raise NotImplemented

    @abstractmethod
    async def get_all(self, *args, **kwargs):
        raise NotImplemented


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def add_one(self, data: dict) -> int:
        async with async_session() as session:
            stmt = insert(self.model).values(**data).returning(self.model.id)
            result = await session.execute(stmt)
            await session.flush()
            await session.commit()
            return result.scalar_one()

    async def get_one(self, history_id):
        async with async_session() as session:
            query = select(self.model).where(self.model.id==history_id)
            result = await session.execute(query)
            log = result.all()[0][0].to_read_model()
            return log

    async def get_all(self, page, per_page, logs):
        offset: int = (page - 1) * per_page
        async with async_session() as session:
            query = (select(self.model).
                     order_by(self.model.timestamp.desc()).
                     offset(offset).
                     limit(per_page))
            logs = await session.execute(query)
            logs = [row[0].to_read_model() for row in logs.all()]
            return logs
