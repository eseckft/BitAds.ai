from abc import ABC, abstractmethod
from typing import List, Optional

from common.schemas.miner_assignment import MinerAssignmentModel


class MinerAssignmentService(ABC):
    @abstractmethod
    async def get_miner_assignments(self) -> List[MinerAssignmentModel]:
        pass

    @abstractmethod
    async def set_miner_assignments(self, assignments: List[MinerAssignmentModel]):
        pass

    @abstractmethod
    async def get_hotkey_by_campaign_item(self, campaign_item: str) -> Optional[str]:
        pass
