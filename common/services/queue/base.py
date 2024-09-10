from abc import ABC, abstractmethod
from typing import List, Dict

from common.schemas.sales import OrderQueueSchema, OrderQueueStatus
from common.schemas.shopify import SaleData


class OrderQueueService(ABC):
    @abstractmethod
    async def add_to_queue(self, id_: str, sale_data: SaleData) -> None:
        pass

    @abstractmethod
    async def get_data_to_process(self, limit: int = 500) -> List[OrderQueueSchema]:
        pass

    @abstractmethod
    async def update_queue_status(self, id_to_status: Dict[str, OrderQueueStatus]) -> None:
        pass

    @abstractmethod
    async def get_all_ids(self) -> List[str]:
        pass
