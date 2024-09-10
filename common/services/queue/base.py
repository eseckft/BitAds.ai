from abc import ABC, abstractmethod

from common.schemas.shopify import SaleData


class OrderQueueService(ABC):
    @abstractmethod
    async def add_to_queue(self, id_: str, sale_data: SaleData):
        pass
