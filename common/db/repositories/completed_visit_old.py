from collections import defaultdict

from sqlalchemy import select, func, distinct, case, and_
from sqlalchemy.orm import Session

from common.db.entities import CompletedVisit
from common.db.repositories.alchemy import BaseSQLAlchemyRepository
from common.db.repositories.base import CompletedVisitRepository
from common.schemas.aggregated import AggregatedData
from common.schemas.completed_visit import CompletedVisitSchema


class SQLAlchemyCompletedVisitRepository(
    CompletedVisitRepository, BaseSQLAlchemyRepository
):
    def __init__(self, session: Session):
        super().__init__(session, CompletedVisit, CompletedVisitSchema)

    async def add_visitor(self, visitor: CompletedVisitSchema):
        return await self.create(visitor)

    async def is_visit_exists(self, id_: str) -> bool:
        result = await self.get(id_)
        return result is not None

    async def get_unique_visits_count(
        self, campaign_id: str, start_block: int, end_block: int
    ) -> int:
        result = self.session.execute(
            select(func.count(distinct(CompletedVisit.id)))
            .where(CompletedVisit.campaign_id == campaign_id)
            .where(CompletedVisit.is_unique == True)
            .where(
                CompletedVisit.complete_block.between(start_block, end_block)
            )
        )
        return result.scalar()

    async def get_aggregated_data(
        self, from_block: int = None, to_block: int = None
    ) -> AggregatedData:
        query = self.session.query(
            CompletedVisit.campaign_id,
            CompletedVisit.miner_hotkey,
            func.count().label("visits"),
            func.sum(case((CompletedVisit.is_unique, 1), else_=0)).label(
                "visits_unique"
            ),
            func.sum(case((CompletedVisit.at, 1), else_=0)).label("at_count"),
            func.sum(CompletedVisit.count_through_rate_click).label(
                "count_through_rate_click"
            ),
        )

        conditions = []
        if from_block is not None:
            conditions.append(CompletedVisit.complete_block > from_block)
        if to_block is not None:
            conditions.append(CompletedVisit.complete_block <= to_block)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.group_by(
            CompletedVisit.campaign_id, CompletedVisit.miner_hotkey
        )

        results = query.all()

        aggregations = defaultdict(dict)

        for result in results:
            campaign_id = result.campaign_id
            miner_hotkey = result.miner_hotkey
            visits = result.visits
            visits_unique = result.visits_unique
            at_count = result.at_count
            count_through_rate_click = result.count_through_rate_click

            aggregations[campaign_id][miner_hotkey] = {
                "visits": visits,
                "visits_unique": visits_unique,
                "at": at_count,
                "count_through_rate_click": count_through_rate_click,
            }

        return AggregatedData(data=aggregations)
