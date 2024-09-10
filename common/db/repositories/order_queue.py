from datetime import datetime
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from common.schemas.sales import OrderQueueSchema, OrderQueueStatus
from common.validator.db.entities.active import OrderQueue

from common.schemas.shopify import OrderDetails


def add_data(
    session: Session, id_: str, order_info: OrderDetails
) -> OrderQueueSchema:
    entity = OrderQueue(id=id_, order_info=order_info)
    session.add(entity)

    session.commit()
    # Refresh the instance to get updated fields
    session.refresh(entity)

    # Return the pydantic schema with ORM mode enabled
    return OrderQueueSchema.model_validate(entity)


def get_by_id(session: Session, id_: str) -> Optional[OrderQueueSchema]:
    entity = session.get(OrderQueue, id_)

    return OrderQueueSchema.model_validate(entity) if entity else None


def update_data(
    session: Session,
    id_: str,
    order_info: OrderDetails = None,
    refund_info: OrderDetails = None,
) -> None:
    entity = session.get(OrderQueue, id_)

    if order_info:
        entity.order_info = order_info
    if refund_info:
        entity.refund_info = refund_info

    entity.status = OrderQueueStatus.PENDING


def get_data_for_processing(
    session: Session, limit: int = 500
) -> List[OrderQueueSchema]:
    # Query to select rows where status is not 'PROCESSED' and order by last_processing_date ascending
    stmt = (
        select(OrderQueue)
        .where(OrderQueue.status != OrderQueueStatus.PROCESSED)
        .order_by(OrderQueue.last_processing_date.asc())
        .limit(limit)
    )

    # Execute the query
    result = session.execute(stmt)

    # Fetch all rows
    rows = result.scalars().all()

    # Return as Pydantic models
    return [OrderQueueSchema.model_validate(row) for row in rows]


def update_status(session: Session, id_: str, status: OrderQueueStatus):
    entity = session.get(OrderQueue, id_)
    entity.status = status
    entity.last_processing_date = datetime.utcnow()