"""
Repository functions for interacting with CompletedVisit entity and aggregating data.

These functions provide operations such as retrieving aggregated data, getting unique visit counts,
adding a visitor, and checking if a visit exists.

Functions:
    get_aggregated_data(session: Session, from_block: int = None, to_block: int = None) -> AggregatedData:
        Retrieves aggregated data for completed visits based on optional block range conditions.

    get_unique_visits_count(session: Session, campaign_id: str, start_block: int, end_block: int) -> int:
        Retrieves the count of unique visits for a specific campaign within a block range.

    add_visitor(session: Session, visitor: CompletedVisitSchema):
        Adds a new visitor entry to the database.

    is_visit_exists(session: Session, id_: str) -> bool:
        Checks if a visit with the specified ID exists in the database.
"""

from collections import defaultdict
from typing import Dict, Optional

from sqlalchemy import func, case, and_, select, distinct
from sqlalchemy.orm import Session

from common.db.entities import CompletedVisit
from common.schemas.aggregated import AggregatedData, AggregationSchema
from common.schemas.completed_visit import CompletedVisitSchema


def get_aggregated_data(
    session: Session,
    from_block: int = None,
    to_block: int = None,
    *campaign_ids
) -> AggregatedData:
    """
    Retrieves aggregated data for completed visits from the database.

    Args:
        session (Session): The SQLAlchemy session object.
        from_block (int, optional): Minimum block number threshold for completed visits (default: None).
        to_block (int, optional): Maximum block number threshold for completed visits (default: None).

    Returns:
        AggregatedData: An AggregatedData object containing aggregated visit data.

    """
    query = session.query(
        CompletedVisit.campaign_id,
        CompletedVisit.miner_hotkey,
        func.count().label("visits"),
        func.sum(case((CompletedVisit.is_unique, 1), else_=0)).label(
            "visits_unique"
        ),
        func.sum(case((CompletedVisit.at, 1), else_=0)).label("at_count"),
        func.sum(CompletedVisit.count_through_rate_click).label(
            "count_through_rate_click"
        ),
        func.sum(CompletedVisit.refund).label("total_refunds"),
        func.sum(CompletedVisit.sales).label("total_sales"),
        func.sum(CompletedVisit.sale_amount).label("sales_amount"),
    )

    conditions = []
    if from_block is not None:
        conditions.append(CompletedVisit.complete_block > from_block)
    if to_block is not None:
        conditions.append(CompletedVisit.complete_block <= to_block)
    if campaign_ids:
        conditions.append(CompletedVisit.campaign_id.in_(campaign_ids))

    if conditions:
        query = query.where(and_(*conditions))

    query = query.group_by(
        CompletedVisit.campaign_id, CompletedVisit.miner_hotkey
    )

    aggregations = defaultdict(lambda: {})

    results = query.all()

    for result in results:
        campaign_id = result.campaign_id
        miner_hotkey = result.miner_hotkey
        visits = result.visits
        visits_unique = result.visits_unique
        at_count = result.at_count
        count_through_rate_click = result.count_through_rate_click
        total_sales = result.total_sales
        total_refunds = result.total_refunds
        sales_amount = result.sales_amount

        aggregations[campaign_id][miner_hotkey] = AggregationSchema(
            visits=visits,
            visits_unique=visits_unique,
            at=at_count,
            count_through_rate_click=count_through_rate_click,
            total_sales=total_sales,
            total_refunds=total_refunds,
            sales_amount=sales_amount,
        )

    return AggregatedData(data=aggregations)


def get_unique_visits_count(
    session: Session, campaign_id: str, start_block: int, end_block: int
) -> int:
    """
    Retrieves the count of unique visits for a specific campaign within a block range.

    Args:
        session (Session): The SQLAlchemy session object.
        campaign_id (str): The ID of the campaign.
        start_block (int): The starting block number (inclusive).
        end_block (int): The ending block number (inclusive).

    Returns:
        int: The count of unique visits.

    """
    result = session.execute(
        select(func.count(distinct(CompletedVisit.id)))
        .where(CompletedVisit.campaign_id == campaign_id)
        .where(CompletedVisit.is_unique == True)
        .where(CompletedVisit.complete_block.between(start_block, end_block))
    )
    return result.scalar()


def add_visitor(session: Session, visitor: CompletedVisitSchema):
    """
    Adds a new visitor entry to the database.

    Args:
        session (Session): The SQLAlchemy session object.
        visitor (CompletedVisitSchema): The visitor data to add.

    """
    entity = CompletedVisit(**visitor.model_dump())
    session.add(entity)


def is_visit_exists(session: Session, id_: str) -> bool:
    """
    Checks if a visit with the specified ID exists in the database.

    Args:
        session (Session): The SQLAlchemy session object.
        id_ (str): The ID of the visit to check.

    Returns:
        bool: True if the visit exists, False otherwise.

    """
    result = session.get(CompletedVisit, id_)
    return result is not None


def get_miners_reputation(
    session: Session,
    from_block: Optional[int] = None,
    to_block: Optional[int] = None,
    *campaign_ids
) -> Dict[str, int]:
    """
    Retrieves reputation data for miners based on completed visits and optional filtering criteria.

    Args:
        session (Session): The database session object.
        from_block (int, optional): The starting block number (inclusive) for filtering completed visits. Defaults to None.
        to_block (int, optional): The ending block number (inclusive) for filtering completed visits. Defaults to None.
        *campaign_ids (str): Variable-length list of campaign IDs to filter completed visits by.

    Returns:
        Dict[str, int]: A dictionary mapping miner hotkeys to their total sales reputation.

    Notes:
        - Retrieves reputation data by aggregating sales from completed visits for each miner.
        - If `from_block` is provided, filters completed visits with `complete_block` greater than or equal to `from_block`.
        - If `to_block` is provided, filters completed visits with `complete_block` less than or equal to `to_block`.
        - If `campaign_ids` are provided, filters completed visits for specific campaign IDs.

    Raises:
        No specific exceptions are raised by this function directly.

    Example usage:
        miners_reputation = get_miners_reputation(session, from_block=1000, to_block=2000, 'campaign_id_1', 'campaign_id_2')
        # Retrieves reputation data for miners with completed visits between blocks 1000 and 2000, for specific campaign IDs.
    """
    # Create the base query
    query = session.query(
        CompletedVisit.miner_hotkey,
        func.sum(CompletedVisit.sales).label("total_sales"),
    )

    filters = []
    if from_block is not None:
        filters.append(CompletedVisit.complete_block >= from_block)
    if to_block is not None:
        filters.append(CompletedVisit.complete_block <= to_block)
    if campaign_ids:
        filters.append(CompletedVisit.campaign_id.in_(campaign_ids))

    if filters:
        query = query.where(and_(*filters))

    query = query.group_by(CompletedVisit.miner_hotkey)

    # noinspection PyTypeChecker
    return dict(query.all())
