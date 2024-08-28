from collections import defaultdict
from datetime import datetime
from typing import List, Optional, Dict

from sqlalchemy import select, func, and_, case
from sqlalchemy.orm import Session

from common.schemas.aggregated import AggregationSchema, AggregatedData
from common.schemas.bitads import BitAdsDataSchema
from common.schemas.sales import SalesStatus
from common.validator.db.entities.active import BitAdsData, MinerAssignment


def get_data_between(
    session: Session,
    updated_from: datetime = None,
    updated_to: datetime = None,
    limit: int = 500,
    offset: int = 0,
) -> List[BitAdsDataSchema]:
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
    stmt = select(BitAdsData)

    # Include the optional updated_lte filter if provided
    if updated_from:
        stmt = stmt.where(BitAdsData.updated_at >= updated_from)
    if updated_to:
        stmt = stmt.where(BitAdsData.updated_at < updated_to)

    stmt = stmt.limit(limit).offset(offset).order_by(BitAdsData.updated_at)

    result = session.execute(stmt)
    return [BitAdsDataSchema.model_validate(r) for r in result.scalars().all()]


def get_data(session: Session, id_: str) -> Optional[BitAdsDataSchema]:
    """
    Retrieves tracking data by ID.

    Args:
        session (Session): The SQLAlchemy session object.
        id_ (str): The ID of the tracking data to retrieve.

    Returns:
        Optional[ValidatorTrackingData]: The validated schema representation of the retrieved tracking data,
                                         or None if not found.

    """
    entity = session.get(BitAdsData, id_)
    return BitAdsDataSchema.model_validate(entity) if entity else None


def add_or_update(
    session: Session, data: BitAdsDataSchema, exclude_fields=("created_at",)
):
    """
    Adds or updates tracking data in the database.

    Args:
        session (Session): The SQLAlchemy session object.
        data (ValidatorTrackingData): The tracking data to add or update.

    """
    entity = session.get(BitAdsData, data.id)

    if entity:
        # Update existing entity's attributes
        for key, value in dict(data).items():
            if value is None:
                continue
            if key in exclude_fields:
                continue
            setattr(entity, key, value)
    else:
        # Create a new entity
        entity = BitAdsData(**dict(data))
        session.add(entity)


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
    stmt = select(func.max(BitAdsData.updated_at)).where(
        (BitAdsData.validator_hotkey != exclude_hotkey)
        | (BitAdsData.validator_hotkey.is_(None))
    )
    result = session.execute(stmt)
    max_date = result.scalar()
    return max_date


def complete_sales_less_than_date(
    session: Session,
    sales_to: datetime,
) -> None:
    # Query the BitAdsData records where sale_date is less than the provided date and refund is 0
    records_to_update = (
        session.query(BitAdsData)
        .filter(
            and_(
                BitAdsData.sale_date < sales_to,
                BitAdsData.refund == 0,
                BitAdsData.sales_status == SalesStatus.NEW,
            )
        )
        .all()
    )

    for record in records_to_update:
        record.sales_status = SalesStatus.COMPLETED


def get_aggregated_data(
    session: Session,
    *campaign_ids,
    from_date: datetime = None,
    to_date: datetime = None,
    from_block: int = None,
    to_block: int = None,
) -> AggregatedData:
    """
    Retrieves aggregated data for completed visits from the database,
    joined with MinerAssignment to get the correct miner hotkey.

    Args:
        session (Session): The SQLAlchemy session object.
        from_date (datetime, optional): Minimum created_at threshold for completed visits (default: None).
        to_date (datetime, optional): Maximum created_at threshold for completed visits (default: None).
        campaign_ids (tuple): Campaign IDs to filter the data (default: all).

    Returns:
        AggregatedData: An AggregatedData object containing aggregated visit data.
    """
    query = session.query(
        BitAdsData.campaign_id,
        MinerAssignment.hotkey,
        func.count().label("visits"),
        func.sum(case((BitAdsData.is_unique, 1), else_=0)).label("visits_unique"),
        func.sum(case((BitAdsData.at, 1), else_=0)).label("at_count"),
        func.sum(BitAdsData.count_through_rate_click).label("count_through_rate_click"),
        func.sum(BitAdsData.refund).label("total_refunds"),
        func.sum(BitAdsData.sales).label("total_sales"),
        func.sum(BitAdsData.sale_amount).label("sales_amount"),
    ).join(MinerAssignment, BitAdsData.campaign_item == MinerAssignment.unique_id)

    conditions = []
    if from_date is not None:
        conditions.append(BitAdsData.created_at >= from_date)
    if to_date is not None:
        conditions.append(BitAdsData.created_at <= to_date)
    if from_block is not None:
        conditions.append(BitAdsData.complete_block >= from_block)
    if to_block is not None:
        conditions.append(BitAdsData.complete_block <= to_block)
    if campaign_ids:
        conditions.append(BitAdsData.campaign_id.in_(campaign_ids))

    if conditions:
        query = query.where(and_(*conditions))

    query = query.group_by(BitAdsData.campaign_id, MinerAssignment.hotkey)

    aggregations = defaultdict(lambda: {})

    results = query.all()

    for result in results:
        campaign_id = result.campaign_id
        miner_hotkey = result.hotkey  # Use hotkey from MinerAssignment
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


def get_miners_reputation(
    session: Session,
    *campaign_ids: str,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> Dict[str, int]:
    """
    Retrieves reputation data for miners based on completed visits and optional filtering criteria.

    Args:
        session (Session): The SQLAlchemy session object.
        from_date (datetime, optional): The starting datetime (inclusive) for filtering completed visits. Defaults to None.
        to_date (datetime, optional): The ending datetime (inclusive) for filtering completed visits. Defaults to None.
        *campaign_ids (str): Variable-length list of campaign IDs to filter completed visits by.

    Returns:
        Dict[str, int]: A dictionary mapping miner hotkeys to their total sales reputation.

    Notes:
        - Retrieves reputation data by aggregating sales from completed visits for each miner.
        - If `from_date` is provided, filters completed visits with `created_at` greater than or equal to `from_date`.
        - If `to_date` is provided, filters completed visits with `created_at` less than or equal to `to_date`.
        - If `campaign_ids` are provided, filters completed visits for specific campaign IDs.
    """
    # Create the base query
    query = session.query(
        MinerAssignment.hotkey,
        func.sum(BitAdsData.sales).label("total_sales"),
    ).join(MinerAssignment, BitAdsData.campaign_item == MinerAssignment.unique_id)

    filters = []
    if from_date is not None:
        filters.append(BitAdsData.created_at >= from_date)
    if to_date is not None:
        filters.append(BitAdsData.created_at <= to_date)
    if campaign_ids:
        filters.append(BitAdsData.campaign_id.in_(campaign_ids))

    if filters:
        query = query.where(and_(*filters))

    query = query.group_by(MinerAssignment.hotkey)

    # noinspection PyTypeChecker
    return dict(query.all())