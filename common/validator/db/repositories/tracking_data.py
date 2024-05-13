from typing import Optional, List

from sqlalchemy import update
from sqlalchemy.orm import Session

from common.db.repositories.alchemy import BaseSQLAlchemyRepository
from common.db.repositories.base import TrackingDataRepository
from common.schemas.visit import VisitStatus
from common.validator.db.entities.active import TrackingData
from common.validator.schemas import ValidatorTrackingData


class SQLAlchemyTrackingDataRepository(
    TrackingDataRepository, BaseSQLAlchemyRepository
):
    def __init__(self, session: Session):
        super().__init__(session, TrackingData, ValidatorTrackingData)

    async def add_data(self, data: ValidatorTrackingData):
        return await self.create(data)

    async def get_data(self, id_: str) -> Optional[ValidatorTrackingData]:
        return await self.get(id_)

    async def get_uncompleted_data(
        self,
        limit: int = 500,
        offset: int = 0,
    ) -> List[ValidatorTrackingData]:
        return await self.list(
            "created_at", limit, offset, status=VisitStatus.synced
        )

    async def get_new_data(
        self, limit: int = 500, offset: int = 0
    ) -> List[ValidatorTrackingData]:
        return await self.list(
            "created_at",
            limit,
            offset,
            # status=VisitStatus.new TODO: temporary get all data for sync with new validators
        )

    async def update_status(self, id_: str, status: VisitStatus) -> None:
        stmt = (
            update(TrackingData)
            .where(TrackingData.id == id_)
            .values(status=status)
        )
        self.session.execute(stmt)

    async def increment_counts(
        self,
        id_: str,
        image_click: int = 0,
        mouse_movement: int = 0,
        read_more_click: int = 0,
        through_rate_click: int = 0,
    ):
        stmt = (
            update(TrackingData)
            .where(TrackingData.id == id_)
            .values(
                count_image_click=TrackingData.count_image_click + image_click,
                count_mouse_movement=TrackingData.count_mouse_movement
                + mouse_movement,
                count_read_more_click=TrackingData.count_read_more_click
                + read_more_click,
                count_through_rate_click=TrackingData.count_through_rate_click
                + through_rate_click,
            )
        )
        self.session.execute(stmt)

    async def update_visit_duration(self, id_: str, duration: int):
        stmt = (
            update(TrackingData)
            .where(TrackingData.id == id_)
            .values(visit_duration=duration)
        )
        self.session.execute(stmt)
