from typing import Optional
from uuid import UUID

from common.db.unit_of_work.base import UnitOfWork
from common.miner.schemas import VisitorSchema
from common.miner.services.visitors.base import VisitorService


class VisitorServiceImpl(VisitorService):
    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    async def add_visitor(self, visitor: VisitorSchema) -> None:
        async with self.unit_of_work as uow:
            await uow.visitors.add_visitor(visitor)

    async def get_visitor(self, id_: UUID) -> Optional[VisitorSchema]:
        async with self.unit_of_work as uow:
            return await uow.visitors.get_visitor(id_)
