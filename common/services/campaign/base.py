from abc import ABC, abstractmethod
from typing import List

from common.schemas.bitads import Campaign


class CampaignService(ABC):
    @abstractmethod
    async def get_active_campaigns(self) -> List[Campaign]:
        pass

    @abstractmethod
    async def set_campaigns(self, campaigns: List[Campaign]):
        pass
