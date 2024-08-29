"""
This module contains functions for interacting with the Visitor entity in the database.
The Visitor entity represents visitors to a website or service, tracking their interactions
and statuses.

Functions:
- add_visitor(session: Session, visitor: VisitorSchema, return_in_site_from: datetime,
              unique_deadline: datetime) -> None:
    Adds a new visitor entity to the database or updates an existing one.

- add_or_update(session: Session, data: VisitorSchema) -> None:
    Adds a new visitor entity to the database or updates an existing one.

- get_visitor(session: Session, id_: str) -> Optional[VisitorSchema]:
    Retrieves a visitor entity from the database by ID.

- update_status(session: Session, id_: str, status: VisitStatus) -> None:
    Updates the status of a visitor entity in the database.

- get_new_visits(session: Session, limit: int = 500, offset: int = 0) -> List[VisitorSchema]:
    Retrieves a list of new visitor entities from the database.

- is_visitor_unique(session: Session, ip_address: str, campaign_id: str,
                    unique_deadline: datetime) -> bool:
    Checks if a visitor with the given IP address and campaign ID is unique within a specified deadline.

- is_return_in_site(session: Session, ip_address: str, campaign_id: str,
                    created_at: datetime) -> bool:
    Checks if a visitor with the given IP address and campaign ID has returned to the site before a specified datetime.

- get_visits_after(session: Session, after: Optional[datetime] = None, limit: int = 500)
                    -> Set[VisitorSchema]:
    Retrieves a set of visitor entities from the database created after a specified datetime.

- get_max_date_excluding_hotkey(session: Session, exclude_hotkey: str) -> Optional[datetime]:
    Retrieves the maximum creation date of visitor entities excluding a specific hotkey.
"""
from datetime import datetime
from typing import Optional, List, Set

from sqlalchemy import exists, select, update, and_, func
from sqlalchemy.orm import Session

from common.miner.db.entities.active import Visitor
from common.miner.schemas import VisitorSchema
from common.schemas.visit import VisitStatus


def add_visitor(
    session: Session,
    visitor: VisitorSchema,
    return_in_site_from: datetime,
    unique_deadline: datetime,
) -> None:
    """
    Adds a new visitor entity to the database or updates an existing one.

    Args:
        session (Session): The database session object.
        visitor (VisitorSchema): The visitor schema object containing visitor data.
        return_in_site_from (datetime): The datetime from which to check return in site.
        unique_deadline (datetime): The datetime deadline for checking visitor uniqueness.
    """
    entity = Visitor(**visitor.model_dump())
    is_unique = is_visitor_unique(
        session, visitor.ip_address, visitor.campaign_id, unique_deadline
    )
    entity.is_unique = is_unique
    is_return = is_return_in_site(
        session, visitor.ip_address, visitor.campaign_id, return_in_site_from
    )
    entity.return_in_site = is_return
    session.add(entity)


def add_or_update(session: Session, data: VisitorSchema) -> None:
    """
    Adds a new visitor entity to the database or updates an existing one.

    Args:
        session (Session): The database session object.
        data (VisitorSchema): The visitor schema object containing visitor data.
    """
    entity = session.get(Visitor, data.id)

    if entity:
        # Update existing entity's attributes
        for key, value in data.model_dump().items():
            setattr(entity, key, value)
    else:
        # Create a new entity
        entity = Visitor(**data.model_dump())
        entity.status = VisitStatus.new
        session.add(entity)


def get_visitor(session: Session, id_: str) -> Optional[VisitorSchema]:
    """
    Retrieves a visitor entity from the database by ID.

    Args:
        session (Session): The database session object.
        id_ (str): The ID of the visitor entity to retrieve.

    Returns:
        Optional[VisitorSchema]: The validated VisitorSchema object if found, otherwise None.
    """
    result = session.get(Visitor, id_)
    return VisitorSchema.model_validate(result) if result else None


def update_status(session: Session, id_: str, status: VisitStatus) -> None:
    """
    Updates the status of a visitor entity in the database.

    Args:
        session (Session): The database session object.
        id_ (str): The ID of the visitor entity to update.
        status (VisitStatus): The new status value to set.
    """
    stmt = update(Visitor).where(Visitor.id == id_).values(status=status)
    session.execute(stmt)


def get_new_visits(
    session: Session, limit: int = 500, offset: int = 0
) -> List[VisitorSchema]:
    """
    Retrieves a list of new visitor entities from the database.

    Args:
        session (Session): The database session object.
        limit (int, optional): Maximum number of entities to retrieve. Defaults to 500.
        offset (int, optional): Offset for pagination. Defaults to 0.

    Returns:
        List[VisitorSchema]: List of validated VisitorSchema objects representing new visits.
    """
    stmt = (
        select(Visitor)
        .where(Visitor.status != VisitStatus.completed)
        .limit(limit)
        .offset(offset)
    )
    result = session.execute(stmt)
    return [VisitorSchema.model_validate(r) for r in result.scalars().all()]


def is_visitor_unique(
    session: Session,
    ip_address: str,
    campaign_id: str,
    unique_deadline: datetime,
) -> bool:
    """
    Checks if a visitor with the given IP address and campaign ID is unique within a specified deadline.

    Args:
        session (Session): The database session object.
        ip_address (str): The IP address of the visitor.
        campaign_id (str): The campaign ID associated with the visit.
        unique_deadline (datetime): The deadline datetime for uniqueness check.

    Returns:
        bool: True if the visitor is unique, False otherwise.
    """
    stmt = select(
        exists().where(
            and_(
                Visitor.ip_address == ip_address,
                Visitor.campaign_id == campaign_id,
                Visitor.created_at > unique_deadline,
            )
        )
    )
    result = session.execute(stmt)
    return not result.scalar()


def is_return_in_site(
    session: Session, ip_address: str, campaign_id: str, created_at: datetime
) -> bool:
    """
    Checks if a visitor with the given IP address and campaign ID has returned to the site before a specified datetime.

    Args:
        session (Session): The database session object.
        ip_address (str): The IP address of the visitor.
        campaign_id (str): The campaign ID associated with the visit.
        created_at (datetime): The datetime to check return in site.

    Returns:
        bool: True if the visitor has returned, False otherwise.
    """
    stmt = select(
        exists().where(
            and_(
                Visitor.ip_address == ip_address,
                Visitor.campaign_id == campaign_id,
                Visitor.created_at < created_at,
            )
        )
    )
    result = session.execute(stmt)
    return result.scalar()


def get_visits_after(
    session: Session, after: Optional[datetime] = None, limit: int = 500, *exclude_hotkeys
) -> Set[VisitorSchema]:
    """
    Retrieves a set of visitor entities from the database created after a specified datetime.

    Args:
        session (Session): The database session object.
        after (Optional[datetime], optional): The datetime after which visits were created. Defaults to None.
        limit (int, optional): Maximum number of entities to retrieve. Defaults to 500.

    Returns:
        Set[VisitorSchema]: Set of validated VisitorSchema objects representing visits after the specified datetime.
    """
    query = session.query(Visitor)

    if after:
        query = query.filter(Visitor.created_at > after)

    query = query.filter(Visitor.miner_hotkey.not_in(exclude_hotkeys))

    query = query.order_by(Visitor.created_at)

    query = query.limit(limit)

    results = query.all()

    return {VisitorSchema.model_validate(r) for r in results}


def get_max_date_excluding_hotkey(
    session: Session, exclude_hotkey: str
) -> Optional[datetime]:
    """
    Retrieves the maximum creation date of visitor entities excluding a specific hotkey.

    Args:
        session (Session): The database session object.
        exclude_hotkey (str): The hotkey to exclude from the query.

    Returns:
        Optional[datetime]: The maximum creation datetime of visitor entities, or None if no entities found.
    """
    stmt = select(func.max(Visitor.created_at)).where(
        Visitor.miner_hotkey != exclude_hotkey
    )
    result = session.execute(stmt)
    max_date = result.scalar()
    return max_date
