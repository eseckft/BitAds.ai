from datetime import datetime, timedelta
from typing import Set, Tuple, Optional

from common.db.database import DatabaseManager
from common.db.repositories import recent_activity, user_agent_activity, hotkey_to_block
from common.db.repositories.visitor import (
    add_visitor,
    get_visits_after,
    get_max_date_excluding_hotkey,
    add_or_update,
    get_visitor,
)
from common.miner.schemas import VisitorSchema
from common.services.miner.base import MinerService
from common.services.settings.impl import SettingsContainerImpl


class MinerServiceImpl(SettingsContainerImpl, MinerService):
    """Implementation of the MinerService using a database manager.

    This class provides a concrete implementation of the MinerService
    abstract base class, handling the addition and retrieval of visitor data
    with database operations.

    Attributes:
        database_manager (DatabaseManager): Manager for handling database sessions.
        return_in_site_delta (timedelta): Time delta used for returning in-site visitors.
    """

    def __init__(
        self,
        database_manager: DatabaseManager,
        return_in_site_delta: timedelta,
    ):
        """Initializes the MinerServiceImpl with the database manager and return in-site delta.

        Args:
            database_manager (DatabaseManager): Manager for handling database sessions.
            return_in_site_delta (timedelta): Time delta used for returning in-site visitors.
        """
        super().__init__()
        self.database_manager = database_manager
        self.return_in_site_delta = return_in_site_delta

    async def add_visit(self, visitor: VisitorSchema):
        """Adds a single visitor record.

        This method adds a visitor record to the database, updating recent activity
        and user agent activity.

        Args:
            visitor (VisitorSchema): The visitor record to add.
        """
        current_datetime = datetime.utcnow()
        return_in_site_from = current_datetime - self.return_in_site_delta
        unique_deadline = current_datetime - timedelta(
            hours=self._params.unique_visits_duration
        )
        with self.database_manager.get_session("active") as session:
            add_visitor(session, visitor, return_in_site_from, unique_deadline)

            current_date = current_datetime.date()
            recent_activity.insert_or_update(session, visitor.ip_address, current_date)
            user_agent_activity.insert_or_update(
                session, visitor.user_agent, current_date
            )

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
        with self.database_manager.get_session("active") as session:
            return get_visits_after(session, after, limit, *exclude_hotkeys)

    async def get_last_update_visit(self, exclude_hotkey: str) -> datetime:
        """Retrieves the datetime of the last visitor update, excluding the specified hotkey.

        Args:
            exclude_hotkey (str): The hotkey to exclude from the search.

        Returns:
            datetime: The datetime of the last visitor update.
        """
        with self.database_manager.get_session("active") as session:
            return get_max_date_excluding_hotkey(session, exclude_hotkey)

    async def add_visits(self, visits: Set[VisitorSchema]) -> None:
        """Adds multiple visitor records.

        Args:
            visits (Set[VisitorSchema]): The set of visitor records to add.
        """
        unique_visits = {visit.id: visit for visit in visits if visit.id is not None}
        with self.database_manager.get_session("active") as session:
            for td in unique_visits.values():
                add_or_update(session, td)

    async def get_hotkey_and_block(self) -> Tuple[str, int]:
        with self.database_manager.get_session("main") as session:
            result = hotkey_to_block.get_hotkey_to_block(session)
            if not result:
                raise ValueError("Hotkey to block not found")
            return result

    async def set_hotkey_and_block(self, hotkey: str, block: int) -> None:
        with self.database_manager.get_session("main") as session:
            hotkey_to_block.set_hotkey_and_block(session, hotkey, block)

    async def get_visit_by_id(self, id_: str) -> Optional[VisitorSchema]:
        with self.database_manager.get_session("active") as session:
            return get_visitor(session, id_)
