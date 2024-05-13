from abc import ABC, abstractmethod
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from common.db.unit_of_work.base import UnitOfWork


class SQLAlchemyUnitOfWork(UnitOfWork, ABC):
    def __init__(self, sessionmaker: Callable[[], AsyncSession]):
        self.sessionmaker = sessionmaker

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    async def __aenter__(self):
        self._session = self.sessionmaker()
        self._init_repos()
        return self

    @abstractmethod
    def _init_repos(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self._session.close()
