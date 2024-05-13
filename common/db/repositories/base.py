from abc import abstractmethod, ABC
from typing import Optional, Generic, TypeVar, List

from pydantic import BaseModel

from common.miner.schemas import VisitorSchema
from common.schemas.aggregated import AggregatedData
from common.schemas.completed_visit import CompletedVisitSchema
from common.schemas.visit import VisitStatus
from common.validator.schemas import ValidatorTrackingData

Model = TypeVar("Model", bound=BaseModel)
ID = TypeVar("ID")


class BaseRepository(ABC, Generic[Model, ID]):
    @abstractmethod
    async def create(self, model_instance: Model) -> Model:
        pass

    @abstractmethod
    async def get(self, id_: ID) -> Optional[Model]:
        pass

    @abstractmethod
    async def list(
        self, order_by: Optional[str] = None, **filters
    ) -> List[Model]:
        pass

    @abstractmethod
    async def exists(self, id_: ID) -> bool:
        pass


class VisitorRepository(ABC):
    @abstractmethod
    async def add_visitor(self, visitor: VisitorSchema):
        pass

    @abstractmethod
    async def get_visitor(self, id_: str) -> Optional[VisitorSchema]:
        pass

    @abstractmethod
    async def update_status(self, id_: str, status: VisitStatus) -> None:
        pass

    @abstractmethod
    async def get_new_visits(self, limit: int = 500) -> List[VisitorSchema]:
        pass


class TrackingDataRepository(ABC):
    @abstractmethod
    async def add_data(self, data: ValidatorTrackingData):
        pass

    @abstractmethod
    async def get_data(self, id_: str) -> Optional[ValidatorTrackingData]:
        pass

    @abstractmethod
    async def get_uncompleted_data(
        self, limit: int = 500
    ) -> List[ValidatorTrackingData]:
        pass

    @abstractmethod
    async def get_new_data(
        self, limit: int = 500, offset: int = 0
    ) -> List[ValidatorTrackingData]:
        pass

    @abstractmethod
    async def update_status(self, id_: str, status: VisitStatus) -> None:
        pass

    @abstractmethod
    async def increment_counts(
        self,
        id_: str,
        image_click: int = 0,
        mouse_movement: int = 0,
        read_more_click: int = 0,
        through_rate_click: int = 0,
    ):
        pass

    @abstractmethod
    async def update_visit_duration(self, id_: str, duration: int):
        pass


class CompletedVisitRepository(ABC):
    @abstractmethod
    async def add_visitor(self, visitor: CompletedVisitSchema):
        pass

    @abstractmethod
    async def is_visit_exists(self, id_: str) -> bool:
        pass

    @abstractmethod
    async def get_unique_visits_count(
        self, campaign_id: str, start_block: int, end_block: int
    ) -> int:
        pass

    @abstractmethod
    async def get_aggregated_data(
        self, from_block: int = None, to_block: int = None
    ) -> AggregatedData:
        pass
