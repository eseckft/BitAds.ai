from datetime import datetime

from pydantic import BaseModel, ConfigDict

from common.schemas.bitads import BitAdsDataSchema
from common.schemas.sales import OrderNotificationStatus


class MinerOrderHistoryModel(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    hotkey: str
    data: BitAdsDataSchema
    status: OrderNotificationStatus

    model_config = ConfigDict(from_attributes=True)
