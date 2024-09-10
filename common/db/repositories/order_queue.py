from typing import Optional

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
