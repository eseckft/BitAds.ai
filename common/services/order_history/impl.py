from abc import ABC, abstractmethod
from typing import List

from common.db.database import DatabaseManager
from common.db.repositories import order_history

from common.schemas.bitads import BitAdsDataSchema
from common.services.order_history.base import OrderHistoryService


class OrderHistoryServiceImpl(OrderHistoryService):
    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager

    async def add_to_history(self, data: BitAdsDataSchema, hotkey: str) -> bool:
        with self.database_manager.get_session("main") as session:
            return order_history.add_record(session, data, hotkey)

    async def get_history(self, limit: int = 50) -> List[BitAdsDataSchema]:
        pass

