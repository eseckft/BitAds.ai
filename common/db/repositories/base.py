from abc import abstractmethod, ABC
from typing import Optional, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel

from common.schemas.visitor import VisitorSchema

Model = TypeVar("Model", bound=BaseModel)
ID = TypeVar("ID")


class BaseRepository(ABC, Generic[Model, ID]):
    @abstractmethod
    async def create(self, model_instance: Model) -> Model:
        pass

    @abstractmethod
    async def get(self, id_: ID) -> Optional[Model]:
        pass


class VisitorRepository(ABC):
    @abstractmethod
    async def add_visitor(self, visitor: VisitorSchema):
        pass

    @abstractmethod
    async def get_visitor(self, id_: UUID) -> Optional[VisitorSchema]:
        pass
