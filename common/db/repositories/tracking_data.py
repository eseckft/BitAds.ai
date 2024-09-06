"""
Repository functions for interacting with TrackingData entity in the database.

These functions provide operations such as adding, updating, retrieving, and querying tracking data.

Functions:
    add_data(session: Session, data: ValidatorTrackingData, unique_deadline: datetime):
        Adds tracking data to the database.

    add_or_update(session: Session, data: ValidatorTrackingData):
        Adds or updates tracking data in the database.

    get_data(session: Session, id_: str) -> Optional[ValidatorTrackingData]:
        Retrieves tracking data by ID.

    get_uncompleted_data(session: Session, updated_at_deadline: datetime,
                         limit: int = 500, offset: int = 0) -> List[ValidatorTrackingData]:
        Retrieves uncompleted tracking data based on deadline and pagination.

    get_new_data(session: Session, limit: int = 500, offset: int = 0) -> List[ValidatorTrackingData]:
        Retrieves new tracking data for synchronization.

    update_status(session: Session, id_: str, status: VisitStatus):
        Updates the status of tracking data.

    increment_counts(session: Session, id_: str, image_click: int = 0, mouse_movement: int = 0,
                     read_more_click: int = 0, through_rate_click: int = 0):
        Increments various counts in tracking data.

    update_visit_duration(session: Session, id_: str, duration: int):
        Updates the visit duration in tracking data.

    is_visitor_unique(session: Session, ip_address: str, campaign_id: str,
                      unique_deadline: datetime) -> bool:
        Checks if a visitor is unique within a given deadline.

    get_max_date_excluding_hotkey(session: Session, exclude_hotkey: str) -> Optional[datetime]:
        Retrieves the maximum updated date excluding a specified hotkey.

    get_tracking_data_after(session: Session, after: Optional[datetime] = None,
                            limit: int = 500) -> Set[ValidatorTrackingData]:
        Retrieves tracking data updated after a given date.

"""

from datetime import datetime
from typing import Optional, List, Set

from sqlalchemy import update, select, and_, exists, func, or_
from sqlalchemy.orm import Session

from common.schemas.visit import VisitStatus
from common.validator.db.entities.active import TrackingData
from common.validator.schemas import ValidatorTrackingData


def add_data(
    session: Session, data: ValidatorTrackingData, unique_deadline: datetime
):
    """
    Adds tracking data to the database.

    Args:
        session (Session): The SQLAlchemy session object.
        data (ValidatorTrackingData): The tracking data to add.
        unique_deadline (datetime): The deadline for uniqueness check.

    """
    entity = TrackingData(**data.model_dump())
    entity.is_unique = is_visitor_unique(
        session, data.ip_address, data.campaign_id, unique_deadline
    )
    session.add(entity)
    return ValidatorTrackingData.model_validate(entity)


def add_or_update(session: Session, data: ValidatorTrackingData):
    """
    Adds or updates tracking data in the database.

    Args:
        session (Session): The SQLAlchemy session object.
        data (ValidatorTrackingData): The tracking data to add or update.

    """
    entity = session.get(TrackingData, data.id)

    if entity:
        # Update existing entity's attributes
        for key, value in data.model_dump().items():
            setattr(entity, key, value)
    else:
        # Create a new entity
        entity = TrackingData(**data.model_dump())
        entity.status = VisitStatus.new
        session.add(entity)


def get_data(session: Session, id_: str) -> Optional[ValidatorTrackingData]:
    """
    Retrieves tracking data by ID.

    Args:
        session (Session): The SQLAlchemy session object.
        id_ (str): The ID of the tracking data to retrieve.

    Returns:
        Optional[ValidatorTrackingData]: The validated schema representation of the retrieved tracking data,
                                         or None if not found.

    """
    entity = session.get(TrackingData, id_)
    return ValidatorTrackingData.model_validate(entity) if entity else None


def get_uncompleted_data(
    session: Session,
    updated_at_deadline: datetime,
    cpa_deadline: datetime,
    limit: int = 500,
    offset: int = 0,
) -> List[ValidatorTrackingData]:
    """
    Retrieves uncompleted tracking data based on deadline and pagination.

    Args:
        session (Session): The SQLAlchemy session object.
        updated_at_deadline (datetime): The deadline for updated_at attribute.
        limit (int, optional): The maximum number of results to retrieve (default: 500).
        offset (int, optional): The number of results to skip (default: 0).

    Returns:
        List[ValidatorTrackingData]: A list of validated schema representations of the retrieved tracking data.

    """
    stmt = (
        select(TrackingData)
        .where(TrackingData.status != VisitStatus.completed)
        .where(
            or_(
                TrackingData.campaign_id.is_(None)
                & (TrackingData.created_at < cpa_deadline),
                TrackingData.campaign_id.is_not(None)
                & (TrackingData.updated_at < updated_at_deadline),
            )
        )
        .limit(limit)
        .offset(offset)
        .order_by(TrackingData.updated_at)
    )
    result = session.execute(stmt)
    return [
        ValidatorTrackingData.model_validate(r) for r in result.scalars().all()
    ]


def get_tracking_data_between(
    session: Session,
    updated_from: datetime = None,
    updated_to: datetime = None,
    limit: int = 500,
    offset: int = 0,
) -> List[ValidatorTrackingData]:
    """
    Retrieves tracking data between dates.

    Args:
        session (Session): The SQLAlchemy session object.
        updated_at_deadline (datetime): The deadline for updated_at attribute.
        limit (int, optional): The maximum number of results to retrieve (default: 500).
        offset (int, optional): The number of results to skip (default: 0).

    Returns:
        List[ValidatorTrackingData]: A list of validated schema representations of the retrieved tracking data.

    """
    stmt = select(TrackingData)

    # Include the optional updated_lte filter if provided
    if updated_from:
        stmt = stmt.where(TrackingData.updated_at >= updated_from)
    if updated_to:
        stmt = stmt.where(TrackingData.updated_at < updated_to)

    stmt = stmt.limit(limit).offset(offset).order_by(TrackingData.updated_at)

    result = session.execute(stmt)
    return [
        ValidatorTrackingData.model_validate(r) for r in result.scalars().all()
    ]


def get_new_data(
    session: Session,
    limit: int = 500,
    offset: int = 0,
) -> List[ValidatorTrackingData]:
    """
    Retrieves new tracking data for synchronization.

    Args:
        session (Session): The SQLAlchemy session object.
        limit (int, optional): The maximum number of results to retrieve (default: 500).
        offset (int, optional): The number of results to skip (default: 0).

    Returns:
        List[ValidatorTrackingData]: A list of validated schema representations of the retrieved tracking data.

    """
    stmt = (
        select(TrackingData)
        # TODO: temporary get all data for sync with new validators
        .where(TrackingData.status != VisitStatus.completed)
        .limit(limit)
        .offset(offset)
        .order_by(TrackingData.created_at)
    )
    result = session.execute(stmt)
    return [
        ValidatorTrackingData.model_validate(r) for r in result.scalars().all()
    ]


def update_status(session: Session, id_: str, status: VisitStatus) -> None:
    """
    Updates the status of tracking data.

    Args:
        session (Session): The SQLAlchemy session object.
        id_ (str): The ID of the tracking data to update.
        status (VisitStatus): The new status to set.

    """
    stmt = (
        update(TrackingData)
        .where(TrackingData.id == id_)
        .values(status=status)
    )
    session.execute(stmt)


def increment_counts(
    session: Session,
    id_: str,
    image_click: int = 0,
    mouse_movement: int = 0,
    read_more_click: int = 0,
    through_rate_click: int = 0,
    sale: int = 0,
    refund: int = 0,
    sale_amount: float = 0,
    visit_duration: int = 0,
):
    """
    Increments various counts in tracking data.

    Args:
        session (Session): The SQLAlchemy session object.
        id_ (str): The ID of the tracking data to update counts.
        image_click (int, optional): The increment for image click count (default: 0).
        mouse_movement (int, optional): The increment for mouse movement count (default: 0).
        read_more_click (int, optional): The increment for read more click count (default: 0).
        through_rate_click (int, optional): The increment for through rate click count (default: 0).

    """
    stmt = (
        update(TrackingData)
        .where(TrackingData.id == id_)
        .values(
            count_image_click=TrackingData.count_image_click + image_click,
            count_mouse_movement=TrackingData.count_mouse_movement
            + mouse_movement,
            count_read_more_click=TrackingData.count_read_more_click
            + read_more_click,
            count_through_rate_click=TrackingData.count_through_rate_click
            + through_rate_click,
            refund=TrackingData.refund + refund,
            sales=TrackingData.sales + sale,
            sale_amount=TrackingData.sale_amount + sale_amount,
            visit_duration=TrackingData.visit_duration + visit_duration,
        )
        .returning(TrackingData)
    )
    result = session.execute(stmt)
    return ValidatorTrackingData.model_validate(result.scalar_one())


def update_visit_duration(session: Session, id_: str, duration: int):
    """
    Updates the visit duration in tracking data.

    Args:
        session (Session): The SQLAlchemy session object.
        id_ (str): The ID of the tracking data to update visit duration.
        duration (int): The new visit duration value.

    """
    stmt = (
        update(TrackingData)
        .where(TrackingData.id == id_)
        .values(visit_duration=duration)
    )
    session.execute(stmt)


def is_visitor_unique(
    session: Session,
    ip_address: str,
    campaign_id: str,
    unique_deadline: datetime,
) -> bool:
    """
    Checks if a visitor is unique within a given deadline.

    Args:
        session (Session): The SQLAlchemy session object.
        ip_address (str): The IP address of the visitor.
        campaign_id (str): The ID of the campaign.
        unique_deadline (datetime): The deadline for uniqueness check.

    Returns:
        bool: True if the visitor is unique, False otherwise.

    """
    stmt = select(
        exists().where(
            and_(
                TrackingData.ip_address == ip_address,
                TrackingData.campaign_id == campaign_id,
                TrackingData.created_at > unique_deadline,
            )
        )
    )
    result = session.execute(stmt)
    return not result.scalar()


def get_max_date_excluding_hotkey(
    session: Session, exclude_hotkey: str
) -> Optional[datetime]:
    """
    Retrieves the maximum updated date excluding a specified hotkey.

    Args:
        session (Session): The SQLAlchemy session object.
        exclude_hotkey (str): The hotkey to exclude.

    Returns:
        Optional[datetime]: The maximum updated date, or None if no records found.

    """
    stmt = select(func.max(TrackingData.updated_at)).where(
        TrackingData.validator_hotkey != exclude_hotkey
    )
    result = session.execute(stmt)
    max_date = result.scalar()
    return max_date


def get_tracking_data_after(
    session: Session, after: Optional[datetime] = None, limit: int = 500
) -> Set[ValidatorTrackingData]:
    """
    Retrieves tracking data updated after a given date.
    Args:
        session (Session): The SQLAlchemy session object.
        after (Optional[datetime], optional): The date to retrieve data after (default: None).
        limit (int, optional): The maximum number of results to retrieve (default: 500).

    Returns:
        Set[ValidatorTrackingData]: A set of validated schema representations of the retrieved tracking data.

    """
    query = session.query(TrackingData)

    if after:
        query = query.filter(TrackingData.updated_at > after)

    query = query.order_by(TrackingData.updated_at)

    query = query.limit(limit)

    results = query.all()

    return {ValidatorTrackingData.model_validate(r) for r in results}


def update_order_amounts(session: Session, id_: str, sales: int, refund: int, sales_amount: float):
    stmt = (
        update(TrackingData)
        .where(TrackingData.id == id_)
        .values(
            refund=refund,
            sales=sales,
            sale_amount=sales_amount,
        )
        .returning(TrackingData)
    )
    result = session.execute(stmt)
    return ValidatorTrackingData.model_validate(result.scalar_one())
