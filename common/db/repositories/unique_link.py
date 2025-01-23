from typing import List, Optional

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from common.db.entities import MinerUniqueLink
from common.schemas.bitads import MinerUniqueLinkSchema


def get_unique_links_for_campaign(
    session: Session, campaign_id: str
) -> List[MinerUniqueLinkSchema]:
    # Query the database to fetch the matching records based on campaign_id
    stmt = (
        select(MinerUniqueLink)
        .where(MinerUniqueLink.campaign_id == campaign_id)
        .order_by(desc(MinerUniqueLink.created_at))
    )

    # Execute the query
    result = session.execute(stmt).scalars().all()

    # Convert the result to a list of UniqueIdData models
    unique_links = [MinerUniqueLinkSchema.model_validate(row) for row in result]

    return unique_links


def get_unique_link_for_campaign_and_hotkey(
    session: Session, campaign_id: str, hotkey: str
) -> Optional[MinerUniqueLinkSchema]:
    # Query the database to fetch the record that matches both campaign_id and hotkey
    stmt = select(MinerUniqueLink).where(
        MinerUniqueLink.campaign_id == campaign_id, MinerUniqueLink.hotkey == hotkey
    )

    # Execute the query and get the first result
    result = session.execute(stmt).scalar_one_or_none()

    # If a result is found, convert it to a UniqueIdData instance

    return MinerUniqueLinkSchema.model_validate(result) if result else None


def get_unique_link_for_hotkey(
    session: Session, hotkey: str
) -> List[MinerUniqueLinkSchema]:
    # Query the database to fetch the matching records based on campaign_id
    stmt = (
        select(MinerUniqueLink)
        .where(MinerUniqueLink.campaign_id == hotkey)
        .order_by(desc(MinerUniqueLink.created_at))
    )

    # Execute the query
    result = session.execute(stmt).scalars().all()

    # Convert the result to a list of UniqueIdData models
    unique_links = [MinerUniqueLinkSchema.model_validate(row) for row in result]

    return unique_links


def add_by_unique_data(session: Session, model: MinerUniqueLinkSchema):
    entity = MinerUniqueLink(**model.model_dump())
    session.add(entity)
