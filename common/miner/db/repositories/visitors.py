from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from common.db.repositories.alchemy import BaseSQLAlchemyRepository
from common.db.repositories.base import VisitorRepository
from common.miner.db.entities.active import Visitor
from common.miner.schemas import VisitorSchema


class SQLAlchemyVisitorRepository(VisitorRepository, BaseSQLAlchemyRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Visitor, VisitorSchema)

    async def add_visitor(self, visitor: VisitorSchema):
        return await self.create(visitor)

    async def get_visitor(self, id_: UUID) -> Optional[VisitorSchema]:
        return await self.get(id_)
