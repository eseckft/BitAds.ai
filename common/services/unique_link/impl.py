import logging
from typing import Optional, List

from common.db.database import DatabaseManager
from common.db.repositories import unique_link
from common.schemas.bitads import MinerUniqueLinkSchema
from common.services.unique_link.base import MinerUniqueLinkService

log = logging.getLogger(__name__)


class MinerUniqueLinkServiceImpl(MinerUniqueLinkService):
    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager

    async def get_unique_links_for_campaign(
        self, campaign_id: str
    ) -> List[MinerUniqueLinkSchema]:
        with self.database_manager.get_session("main") as session:
            return unique_link.get_unique_links_for_campaign(session, campaign_id)

    async def get_unique_link_for_campaign_and_hotkey(
        self, campaign_id: str, hotkey: str
    ) -> Optional[MinerUniqueLinkSchema]:
        with self.database_manager.get_session("main") as session:
            return unique_link.get_unique_link_for_campaign_and_hotkey(
                session, campaign_id, hotkey
            )

    async def get_unique_links_for_hotkey(self, hotkey: str) -> List[MinerUniqueLinkSchema]:
        with self.database_manager.get_session("main") as session:
            return unique_link.get_unique_link_for_hotkey(session, hotkey)

    async def add_unique_link(self, data: MinerUniqueLinkSchema):
        with self.database_manager.get_session("main") as session:
            return unique_link.add_by_unique_data(
                session, data
            )
