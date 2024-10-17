from abc import ABC, abstractmethod
from typing import List, Optional

from common.schemas.bitads import Campaign


class CampaignService(ABC):
    @abstractmethod
    async def get_active_campaigns(self) -> List[Campaign]:
        pass

    @abstractmethod
    async def set_campaigns(self, campaigns: List[Campaign]):
        pass

    @abstractmethod
    async def get_campaign_by_id(self, id_: str) -> Optional[Campaign]:
        pass
