from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from common.db.entities import CampaignEntity
from common.schemas.bitads import Campaign, CampaignStatus
from common.schemas.campaign import CampaignType


def get_campaigns(
    session: Session,
    type_: Optional[CampaignType] = None,
    status: Optional[CampaignStatus] = None,
) -> List[Campaign]:
    # Start building the query
    stmt = select(CampaignEntity)

    # Create a list of filters to apply (only apply filters if the corresponding parameter is provided)
    filters = []
    if type_ is not None:
        filters.append(CampaignEntity.type == type_)
    if status is not None:
        filters.append(CampaignEntity.status == status.value)

    # Apply filters if any exist
    if filters:
        stmt = stmt.where(and_(*filters))

    # Execute the query
    result = session.execute(stmt)

    # Fetch all rows
    rows = result.scalars().all()

    # Return as Pydantic models
    return [Campaign.model_validate(row) for row in rows]
