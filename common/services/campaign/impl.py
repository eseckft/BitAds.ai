from typing import List

from common.db.database import DatabaseManager
from common.db.repositories import campaigns
from common.schemas.bitads import Campaign, CampaignStatus
from common.schemas.campaign import CampaignType
from common.services.campaign.base import CampaignService


class CampaignServiceImpl(CampaignService):
    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager

    async def get_active_campaigns(self) -> List[Campaign]:
        with self.database_manager.get_session("main") as session:
            return campaigns.get_campaigns(
                session, status=CampaignStatus.ACTIVATED
            )
