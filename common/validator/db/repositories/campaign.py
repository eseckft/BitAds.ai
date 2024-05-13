from typing import Set

from sqlalchemy import update
from sqlalchemy.orm import Session

from common.validator.db.entities.active import Campaign


class CampaignRepository:
    def __init__(self, session: Session):
        self.session = session

    async def get_active_campaign_ids(self) -> Set[str]:
        active_campaigns = (
            self.session.query(Campaign.id)
            .filter(Campaign.status == True)
            .all()
        )
        return {campaign.id for campaign in active_campaigns}

    async def add_or_create_campaign(self, id_: str, block: int) -> None:
        existing_campaign = (
            self.session.query(Campaign).filter(Campaign.id == id_).first()
        )
        if existing_campaign:
            existing_campaign.last_active_block = block
            existing_campaign.status = True
        else:
            new_campaign = Campaign(
                id=id_, status=True, last_active_block=block
            )
            self.session.add(new_campaign)

    async def update_campaign_status(self, campaign_id: str, status: bool):
        stmt = (
            update(Campaign)
            .where(Campaign.id == campaign_id)
            .values(
                status=status,
            )
        )
        self.session.execute(stmt)

    async def update_campaign_umax(self, campaign_id: str, umax: float):
        self.session.execute(
            update(Campaign)
            .where(Campaign.id == campaign_id)
            .values(umax=umax)
        )
