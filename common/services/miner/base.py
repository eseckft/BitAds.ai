from abc import ABC, abstractmethod
from datetime import datetime
from typing import Set, Tuple

from common.miner.schemas import VisitorSchema
from common.services.settings.base import SettingsContainer


class MinerService(SettingsContainer, ABC):
    """Abstract base class for a Miner Service.

    This class defines the interface for a service that handles visitor data.
    It includes methods for adding and retrieving visit records, and for getting
    the last update time for visits.

    Methods:
        add_visit(visitor: VisitorSchema):
            Adds a single visitor record.

        get_visits_after(after: datetime = None, limit: int = 500) -> Set[VisitorSchema]:
            Retrieves visitor records added after the specified datetime.

        get_last_update_visit(exclude_hotkey: str) -> datetime:
            Retrieves the datetime of the last visitor update, excluding the specified hotkey.

        add_visits(visits: Set[VisitorSchema]) -> None:
            Adds multiple visitor records.
    """

    @abstractmethod
    async def add_visit(self, visitor: VisitorSchema):
        """Adds a single visitor record.

        Args:
            visitor (VisitorSchema): The visitor record to add.
        """
        pass

    @abstractmethod
    async def get_visits_after(
        self, after: datetime = None, limit: int = 500, *exclude_hotkeys
    ) -> Set[VisitorSchema]:
        """Retrieves visitor records added after the specified datetime.

        Args:
            after (datetime, optional): The datetime to retrieve records after. Defaults to None.
            limit (int, optional): The maximum number of records to retrieve. Defaults to 500.

        Returns:
            Set[VisitorSchema]: A set of visitor records.
        """
        pass

    @abstractmethod
    async def get_last_update_visit(self, exclude_hotkey: str) -> datetime:
        """Retrieves the datetime of the last visitor update, excluding the specified hotkey.

        Args:
            exclude_hotkey (str): The hotkey to exclude from the search.

        Returns:
            datetime: The datetime of the last visitor update.
        """
        pass

    @abstractmethod
    async def add_visits(self, visits: Set[VisitorSchema]) -> None:
        """Adds multiple visitor records.

        Args:
            visits (Set[VisitorSchema]): The set of visitor records to add.
        """
        pass

    @abstractmethod
    async def get_hotkey_and_block(self) -> Tuple[str, int]:
        pass

    @abstractmethod
    async def set_hotkey_and_block(self, hotkey: str, block: int) -> None:
        pass

    @abstractmethod
    async def get_visit_by_id(self, id_: str) -> VisitorSchema:
        pass
