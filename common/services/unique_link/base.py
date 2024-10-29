from abc import ABC, abstractmethod
from typing import List, Optional

from common.schemas.bitads import MinerUniqueLinkSchema


class MinerUniqueLinkService(ABC):
    @abstractmethod
    async def get_unique_links_for_campaign(
        self, campaign_id: str
    ) -> List[MinerUniqueLinkSchema]:
        pass

    @abstractmethod
    async def get_unique_link_for_campaign_and_hotkey(
        self, campaign_id: str, hotkey: str
    ) -> Optional[MinerUniqueLinkSchema]:
        pass

    @abstractmethod
    async def add_unique_link(self, data: MinerUniqueLinkSchema):
        pass
