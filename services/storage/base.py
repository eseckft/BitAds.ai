from abc import ABC, abstractmethod
from typing import Union, Optional

from schemas.bit_ads import GetMinerUniqueIdResponse, Score, Campaign, Aggregation


class BaseStorage(ABC):
    @abstractmethod
    def save_campaign(self, task: Campaign) -> None:
        pass

    @abstractmethod
    def remove_campaign(self, campaign_id: Union[int, str]) -> None:
        pass

    @abstractmethod
    def save_miner_unique_url(self, data: GetMinerUniqueIdResponse) -> None:
        pass

    @abstractmethod
    def save_miner_unique_url_stats(self, data: Aggregation) -> None:
        pass

    @abstractmethod
    def save_miner_unique_url_score(
        self,
        product_unique_id: Union[int, str],
        product_item_unique_id: Union[int, str],
        data: Score,
    ) -> None:
        pass

    @abstractmethod
    def unique_link_exists(self, campaign_id: Union[int, str]) -> bool:
        pass

    @abstractmethod
    def get_unique_url(
        self, campaign_id: Union[int, str]
    ) -> Optional[GetMinerUniqueIdResponse]:
        pass
