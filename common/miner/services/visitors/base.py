from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from common.miner.schemas import VisitorSchema


class VisitorService(ABC):
    @abstractmethod
    async def add_visitor(self, visitor: VisitorSchema) -> None:
        pass

    @abstractmethod
    async def get_visitor(self, id_: UUID) -> Optional[VisitorSchema]:
        pass
