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


def add_or_update_campaign(session: Session, campaign: Campaign):
    # Try to find the existing entity by its ID
    entity = session.get(CampaignEntity, campaign.id)

    # If the entity exists, update its attributes
    if entity:
        for key, value in dict(campaign).items():
            # Set the attribute on the entity
            setattr(entity, key, value)
    else:
        # Create a new entity if it doesn't exist
        entity = CampaignEntity(**dict(campaign))
        session.add(entity)


def get_by_product_unique_id(
    session: Session, product_unique_id: str
) -> Optional[Campaign]:
    # Query the database to find the campaign by its product_unique_id
    entity = (
        session.query(CampaignEntity).filter_by(product_unique_id=product_unique_id).first()
    )

    # Validate the result using Pydantic's model validation
    return Campaign.model_validate(entity) if entity else None
