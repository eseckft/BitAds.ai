from datetime import datetime
from enum import IntEnum
from typing import Optional

from common.schemas.shopify import OrderDetails
from pydantic import BaseModel, ConfigDict


class SalesStatus(IntEnum):
    NEW = 0
    COMPLETED = 1


class OrderQueueStatus(IntEnum):
    PENDING = 0
    VISIT_NOT_FOUND = 1
    PROCESSED = 2
    ERROR = -1


class OrderQueueSchema(BaseModel):
    id: str
    order_info: OrderDetails
    refund_info: Optional[OrderDetails] = None
    created_at: datetime
    last_processing_date: datetime
    status: OrderQueueStatus = OrderQueueStatus.PENDING

    model_config = ConfigDict(from_attributes=True)
