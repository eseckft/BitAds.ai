from typing import List

from common.db.database import DatabaseManager
from common.db.repositories import order_history
from common.schemas.bitads import BitAdsDataSchema
from common.schemas.order_history import MinerOrderHistoryModel
from common.schemas.sales import OrderNotificationStatus
from common.services.order_history.base import OrderHistoryService


class OrderHistoryServiceImpl(OrderHistoryService):
    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager

    async def add_to_history(self, data: BitAdsDataSchema, hotkey: str) -> bool:
        with self.database_manager.get_session("main") as session:
            status = (
                OrderNotificationStatus.REFUND
                if data.refund_info
                else OrderNotificationStatus.ORDER
            )
            return order_history.add_record(session, data, hotkey, status)

    async def get_history(self, limit: int = 50) -> List[MinerOrderHistoryModel]:
        with self.database_manager.get_session("main") as session:
            return order_history.get_history(session, limit)
