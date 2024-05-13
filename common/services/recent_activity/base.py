from abc import ABC, abstractmethod
from typing import List

from common.miner.schemas import VisitorActivitySchema


class RecentActivityService(ABC):
    @abstractmethod
    async def get_recent_activity(
        self, recent_activity_count: int = None, limit: int = None
    ) -> List[VisitorActivitySchema]:
        pass

    @abstractmethod
    async def clear_old_recent_activity(self) -> None:
        pass
