from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from common.schemas.bitads import Campaign
from common.schemas.metadata import MinersMetadataSchema
from common.services.settings.base import SettingsContainer


class ValidatorService(SettingsContainer, ABC):
    """Abstract base class defining the interface for a Validator Service.

    This class defines methods for managing ratings, campaigns, actions,
    tracking data, and visits for validators.

    Methods:
        calculate_ratings(from_block: int = None, to_block: int = None) -> Dict[str, float]:
            Calculates ratings based on block range.

        sync_active_campaigns(current_block: int, active_campaigns: List[Campaign]) -> None:
            Synchronizes active campaigns based on the current block.

        calculate_and_set_campaign_umax(from_block: int, to_block: int) -> Dict[str, float]:
            Calculates and sets campaign uMax values based on block range.

        get_visits_to_complete(page_number: int = 1, page_size: int = 500) -> List[ValidatorTrackingData]:
            Retrieves visits to complete based on pagination parameters.

        complete_visits(completed_visits: List[CompletedVisitSchema]):
            Marks visits as completed based on provided data.
    """

    @abstractmethod
    async def calculate_ratings(
        self, from_block: int = None, to_block: int = None
    ) -> Dict[str, float]:
        """Calculates ratings based on block range.

        Args:
            from_block (int, optional): Starting block number. Defaults to None.
            to_block (int, optional): Ending block number. Defaults to None.

        Returns:
            Dict[str, float]: A dictionary mapping validator IDs to rating scores.
        """
        pass

    @abstractmethod
    async def sync_active_campaigns(
        self, current_block: int, active_campaigns: List[Campaign]
    ) -> None:
        """Synchronizes active campaigns based on the current block.

        Args:
            current_block (int): The current block number.
            active_campaigns (List[Campaign]): List of active campaigns to synchronize.
        """
        pass

    @abstractmethod
    async def add_miner_ping(
        self, current_block: int, unique_id_to_hotkey: Dict[str, Tuple[str, str]]
    ):
        pass

    @abstractmethod
    async def get_miners_metadata(self) -> Dict[str, MinersMetadataSchema]:
        pass

    @abstractmethod
    async def add_miner_metadata(self, metadata: MinersMetadataSchema) -> None:
        pass
