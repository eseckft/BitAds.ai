from typing import Optional, List

from sqlalchemy import update, select, exists, and_
from sqlalchemy.orm import Session

from common.db.repositories.alchemy import BaseSQLAlchemyRepository
from common.db.repositories.base import VisitorRepository
from common.miner.db.entities.active import Visitor
from common.miner.schemas import VisitorSchema
from common.schemas.visit import VisitStatus


class SQLAlchemyVisitorRepository(VisitorRepository, BaseSQLAlchemyRepository):
    def __init__(self, session: Session):
        super().__init__(session, Visitor, VisitorSchema)

    async def add_visitor(self, visitor: VisitorSchema):
        # Check if the visitor is unique
        is_unique = await self._is_visitor_unique(
            visitor.ip_address, visitor.campaign_id
        )
        visitor.is_unique = is_unique
        return await self.create(visitor)

    async def get_visitor(self, id_: str) -> Optional[VisitorSchema]:
        return await self.get(id_)

    async def update_status(self, id_: str, status: VisitStatus) -> None:
        stmt = update(Visitor).where(Visitor.id == id_).values(status=status)
        self.session.execute(stmt)

    async def get_new_visits(self, limit: int = 500) -> List[VisitorSchema]:
        stmt = (
            select(Visitor)
            .where(Visitor.status != VisitStatus.completed)
            .limit(limit)
        )
        result = self.session.execute(stmt)
        return [
            VisitorSchema.model_validate(r) for r in result.scalars().all()
        ]

    async def _is_visitor_unique(
        self, ip_address: str, campaign_id: str
    ) -> bool:
        stmt = select(
            exists().where(
                and_(
                    Visitor.ip_address == ip_address,
                    Visitor.campaign_id == campaign_id,
                )
            )
        )
        result = self.session.execute(stmt)
        return not result.scalar()
