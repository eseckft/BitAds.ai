from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from common.validator.schemas import TrackingDataSchema


class TrackingDataService(ABC):
    @abstractmethod
    async def add_data(self, data: TrackingDataSchema):
        pass

    @abstractmethod
    async def get_data(self, id_: UUID) -> Optional[TrackingDataSchema]:
        pass
