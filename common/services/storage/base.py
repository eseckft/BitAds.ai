from abc import ABC, abstractmethod
from typing import Union, Optional

from common.schemas.bitads import Campaign, GetMinerUniqueIdResponse


class BaseStorage(ABC):
    """Abstract base class for storage operations.

    This class defines the interface for storage operations related to campaigns
    and unique URLs for miners.

    Methods:
        save_campaign(task: Campaign) -> None:
            Saves a campaign to the storage.

        remove_campaign(campaign_id: Union[int, str]) -> None:
            Removes a campaign from the storage by its ID.

        save_miner_unique_url(product_unique_id: str, data: GetMinerUniqueIdResponse) -> None:
            Saves a miner's unique URL information to the storage.

        unique_link_exists(campaign_id: str) -> bool:
            Checks if a unique link exists for a given campaign ID.

        get_unique_url(campaign_id: str) -> Optional[GetMinerUniqueIdResponse]:
            Retrieves the unique URL information for a given campaign ID.
    """

    @abstractmethod
    def save_campaign(self, task: Campaign) -> None:
        """Saves a campaign to the storage.

        Args:
            task (Campaign): The campaign to save.
        """
        pass

    @abstractmethod
    def remove_campaign(self, campaign_id: Union[int, str]) -> None:
        """Removes a campaign from the storage by its ID.

        Args:
            campaign_id (Union[int, str]): The ID of the campaign to remove.
        """
        pass

    @abstractmethod
    def save_miner_unique_url(
        self, product_unique_id: str, data: GetMinerUniqueIdResponse
    ) -> None:
        """Saves a miner's unique URL information to the storage.

        Args:
            product_unique_id (str): The unique ID of the product.
            data (GetMinerUniqueIdResponse): The data associated with the miner's unique URL.
        """
        pass

    # @abstractmethod
    # def save_miner_unique_url_stats(self, data: Aggregation) -> None:
    #     pass

    # @abstractmethod
    # def save_miner_unique_url_score(
    #     self,
    #     product_unique_id: Union[int, str],
    #     product_item_unique_id: Union[int, str],
    #     data: Score,
    # ) -> None:

    @abstractmethod
    def unique_link_exists(self, campaign_id: str) -> bool:
        """Checks if a unique link exists for a given campaign ID.

        Args:
            campaign_id (str): The ID of the campaign.

        Returns:
            bool: True if the unique link exists, False otherwise.
        """
        pass

    @abstractmethod
    def get_unique_url(
        self, campaign_id: str
    ) -> Optional[GetMinerUniqueIdResponse]:
        """Retrieves the unique URL information for a given campaign ID.

        Args:
            campaign_id (str): The ID of the campaign.

        Returns:
            Optional[GetMinerUniqueIdResponse]: The unique URL information if it exists, None otherwise.
        """
        pass
