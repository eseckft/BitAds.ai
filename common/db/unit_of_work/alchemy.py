from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from common.db.repositories.visitors import SQLAlchemyVisitorRepository
from common.db.unit_of_work.base import UnitOfWork


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, sessionmaker: Callable[[], AsyncSession]):
        self.sessionmaker = sessionmaker

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    async def __aenter__(self):
        self._session = self.sessionmaker()
        self.visitors = SQLAlchemyVisitorRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self._session.close()
