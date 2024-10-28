"""
Repository functions for interacting with the Campaign entity in the database.

These functions provide operations such as retrieving active campaign IDs,
adding or creating new campaigns, and updating campaign status and attributes.

Functions:
    get_active_campaign_ids(session) -> Set[str]:
        Retrieves IDs of active campaigns from the database.

    add_or_create_campaign(session: Session, id_: str, block: int) -> None:
        Adds a new campaign to the database or updates an existing one.

    update_campaign_status(session: Session, campaign_id: str, status: bool):
        Updates the status of a campaign in the database.

    update_campaign_umax(session: Session, campaign_id: str, umax: float):
        Updates the 'umax' attribute of a campaign in the database.
"""

from typing import Set
from typing import Set, List

from sqlalchemy import update, and_
from sqlalchemy.orm import Session

from common.schemas.campaign import CampaignType
from common.validator.db.entities.active import Campaign
from common.validator.schemas import CampaignSchema


def get_active_campaign_ids(session) -> Set[str]:
    """
    Retrieves IDs of active campaigns from the database.

    Args:
        session (Session): The SQLAlchemy session object.

    Returns:
        Set[str]: A set of active campaign IDs.

    """
    active_campaigns = (
        session.query(Campaign.id).filter(Campaign.status == True).all()
    )
    return {campaign.id for campaign in active_campaigns}


def add_or_create_campaign(
    session: Session,
    id_: str,
    block: int,
    type_: CampaignType = CampaignType.REGULAR,
) -> None:
    """
    Adds a new campaign to the database or updates an existing one.

    Args:
        session (Session): The SQLAlchemy session object.
        id_ (str): The ID of the campaign.
        block (int): The block number associated with the campaign.
        type_ (CampaignType): The type of the campaign
    """
    existing_campaign = (
        session.query(Campaign).filter(Campaign.id == id_).first()
    )
    if existing_campaign:
        existing_campaign.last_active_block = block
        existing_campaign.status = True
        existing_campaign.type = type_
    else:
        new_campaign = Campaign(
            id=id_, status=True, last_active_block=block, type=type_
        )
        session.add(new_campaign)


def update_campaign_status(session: Session, campaign_id: str, status: bool):
    """
    Updates the status of a campaign in the database.

    Args:
        session (Session): The SQLAlchemy session object.
        campaign_id (str): The ID of the campaign to update.
        status (bool): The new status of the campaign.

    """
    stmt = (
        update(Campaign)
        .where(Campaign.id == campaign_id)
        .values(
            status=status,
        )
    )
    session.execute(stmt)


def update_campaign_umax(session: Session, campaign_id: str, umax: float):
    """
    Updates the 'umax' attribute of a campaign in the database.

    Args:
        session (Session): The SQLAlchemy session object.
        campaign_id (str): The ID of the campaign to update.
        umax (float): The new 'umax' value for the campaign.

    """
    session.execute(
        update(Campaign).where(Campaign.id == campaign_id).values(umax=umax)
    )


def get_active_campaigns(
    session: Session, from_block: int = None, to_block: int = None
) -> List[CampaignSchema]:
    """
    Retrieves a list of active campaign entities from the database based on optional block range.

    Args:
        session (Session): The database session object.
        from_block (int, optional): The starting block number (inclusive) for filtering active campaigns. Defaults to None.
        to_block (int, optional): The ending block number (exclusive) for filtering active campaigns. Defaults to None.

    Returns:
        List[CampaignSchema]: List of validated CampaignSchema objects representing active campaigns.

    Notes:
        - If neither `from_block` nor `to_block` is provided, retrieves all active campaigns.
        - If only `from_block` is provided, retrieves active campaigns with `last_active_block` greater than `from_block`.
        - If only `to_block` is provided, retrieves active campaigns with `last_active_block` less than or equal to `to_block`.
        - If both `from_block` and `to_block` are provided, retrieves active campaigns within the block range.

    Raises:
        No specific exceptions are raised by this function directly.

    Example usage:
        active_campaigns = get_active_campaigns(session, from_block=1000, to_block=2000)
        # Retrieves active campaigns with last_active_block between 1000 (inclusive) and 2000 (exclusive).
    """
    query = session.query(Campaign)

    conditions = []
    # if from_block is not None:
    #     conditions.append(Campaign.last_active_block > from_block)
    # if to_block is not None:
    #     conditions.append(Campaign.last_active_block <= to_block)

    conditions.append(Campaign.status == True)

    if conditions:
        query = query.where(and_(*conditions))

    # noinspection PyTypeChecker
    return list(map(CampaignSchema.model_validate, query.all()))
