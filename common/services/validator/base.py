from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Set, List, Optional, Tuple

from common.schemas.bitads import Campaign, BitAdsDataSchema
from common.schemas.completed_visit import CompletedVisitSchema
from common.schemas.metadata import MinersMetadataSchema
from common.services.settings.base import SettingsContainer
from common.validator.schemas import Action, ValidatorTrackingData


class ValidatorService(SettingsContainer, ABC):
    """Abstract base class defining the interface for a Validator Service.

    This class defines methods for managing ratings, campaigns, actions,
    tracking data, and visits for validators.

    Methods:
        calculate_ratings(from_block: int = None, to_block: int = None) -> Dict[str, float]:
            Calculates ratings based on block range.

        sync_active_campaigns(current_block: int, active_campaigns: List[Campaign]) -> None:
            Synchronizes active campaigns based on the current block.

        send_action(id_: str, action: Action, amount: float = None) -> None:
            Sends an action with optional amount.

        add_tracking_data(data: ValidatorTrackingData) -> None:
            Adds tracking data for a validator.

        add_tracking_datas(tracking_datas: Set[ValidatorTrackingData]) -> None:
            Adds multiple tracking data entries for validators.

        get_tracking_data_after(after: datetime = None, limit: int = 500):
            Retrieves tracking data entries after a specified date.

        get_last_update_tracking_data(exclude_hotkey: str) -> datetime:
            Retrieves the last update timestamp of tracking data for a specified hotkey.

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
    async def send_action(
        self, id_: str, action: Action, amount: float = None
    ) -> Optional[ValidatorTrackingData]:
        """Sends an action with optional amount.

        Args:
            id_ (str): Identifier for the action.
            action (Action): Action type to send.
            amount (float, optional): Optional amount for the action. Defaults to None.
        """
        pass

    @abstractmethod
    async def add_tracking_data(
        self, data: ValidatorTrackingData, bit_ads_data: BitAdsDataSchema = None
    ) -> Optional[ValidatorTrackingData]:
        """Adds tracking data for a validator.

        Args:
            data (ValidatorTrackingData): Tracking data to add.
        """
        pass

    @abstractmethod
    async def add_tracking_datas(
        self, tracking_datas: Set[ValidatorTrackingData]
    ) -> None:
        """Adds multiple tracking data entries for validators.

        Args:
            tracking_datas (Set[ValidatorTrackingData]): Set of tracking data entries to add.
        """
        pass

    @abstractmethod
    async def get_tracking_data_after(
        self, after: datetime = None, limit: int = 500
    ) -> Set[ValidatorTrackingData]:
        """Retrieves tracking data entries after a specified date.

        Args:
            after (datetime, optional): Retrieve data after this date. Defaults to None.
            limit (int): Maximum number of entries to retrieve. Defaults to 500.
        """
        pass

    @abstractmethod
    async def get_last_update_tracking_data(self, exclude_hotkey: str) -> datetime:
        """Retrieves the last update timestamp of tracking data for a specified hotkey.

        Args:
            exclude_hotkey (str): Hotkey to exclude from the timestamp retrieval.

        Returns:
            datetime: Last update timestamp of tracking data.
        """
        pass

    @abstractmethod
    async def calculate_and_set_campaign_umax(
        self, from_block: int, to_block: int
    ) -> Dict[str, float]:
        """Calculates and sets campaign uMax values based on block range.

        Args:
            from_block (int): Starting block number.
            to_block (int): Ending block number.

        Returns:
            Dict[str, float]: A dictionary mapping campaign IDs to uMax values.
        """
        pass

    @abstractmethod
    async def get_visits_to_complete(
        self, page_number: int = 1, page_size: int = 500
    ) -> List[ValidatorTrackingData]:
        """Retrieves visits to complete based on pagination parameters.

        Args:
            page_number (int, optional): Page number of results to retrieve. Defaults to 1.
            page_size (int, optional): Number of results per page. Defaults to 500.

        Returns:
            List[ValidatorTrackingData]: List of tracking data entries representing visits to complete.
        """
        pass

    @abstractmethod
    async def complete_visits(self, completed_visits: List[CompletedVisitSchema]):
        """Marks visits as completed based on provided data.

        Args:
            completed_visits (List[CompletedVisitSchema]): List of completed visit schemas.
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
