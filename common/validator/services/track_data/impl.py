from typing import Optional
from uuid import UUID

from common.validator.db.unit_of_work.base import ValidatorActiveUnitOfWork
from common.validator.schemas import TrackingDataSchema
from common.validator.services.track_data.base import TrackingDataService


class TrackingDataServiceImpl(TrackingDataService):
    def __init__(self, unit_of_work: ValidatorActiveUnitOfWork):
        self.unit_of_work = unit_of_work

    async def add_data(self, data: TrackingDataSchema):
        async with self.unit_of_work as uow:
            await uow.tracking_data.add_data(data)

    async def get_data(self, id_: UUID) -> Optional[TrackingDataSchema]:
        async with self.unit_of_work as uow:
            return await uow.tracking_data.get_data(id_)
