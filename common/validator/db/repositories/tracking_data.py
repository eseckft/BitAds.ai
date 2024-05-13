from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from common.db.repositories.alchemy import BaseSQLAlchemyRepository
from common.db.repositories.base import TrackingDataRepository
from common.validator.schemas import TrackingDataSchema
from common.validator.db.entities.active import TrackingData


class SQLAlchemyTrackingDataRepository(
    TrackingDataRepository, BaseSQLAlchemyRepository
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TrackingData, TrackingDataSchema)

    async def add_data(self, data: TrackingDataSchema):
        return await self.create(data)

    async def get_data(self, id_: UUID) -> Optional[TrackingDataSchema]:
        return await self.get(id_)
