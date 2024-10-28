from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Set, Dict

from common.miner.schemas import VisitorSchema
from common.schemas.bitads import BitAdsDataSchema
from common.schemas.completed_visit import CompletedVisitSchema
from common.schemas.sales import OrderQueueSchema, OrderQueueStatus
from common.schemas.shopify import SaleData

from common.validator.schemas import ValidatorTrackingData


class BitAdsService(ABC):
    @abstractmethod
    async def add_or_update_validator_bitads_data(
        self, validator_data: ValidatorTrackingData, sale_data: SaleData
    ):
        pass

    @abstractmethod
    async def get_bitads_data_between(
        self,
        updated_from: datetime = None,
        updated_to: datetime = None,
        page_number: int = 1,
        page_size: int = 500,
    ) -> List[BitAdsDataSchema]:
        pass

    @abstractmethod
    async def get_last_update_bitads_data(self, exclude_hotkey: str):
        pass

    @abstractmethod
    async def add_by_visits(self, visits: Set[VisitorSchema]) -> None:
        pass

    @abstractmethod
    async def add_by_visit(self, visit: VisitorSchema) -> None:
        pass

    @abstractmethod
    async def add_bitads_data(self, datas: Set[BitAdsDataSchema]) -> None:
        pass

    @abstractmethod
    async def get_data_by_ids(self, ids: Set[str]) -> Set[BitAdsDataSchema]:
        pass

    @abstractmethod
    async def add_completed_visits(self, visits: List[CompletedVisitSchema]):
        pass

    @abstractmethod
    async def update_sale_status_if_needed(self, sale_date_from: datetime) -> None:
        pass

    @abstractmethod
    async def add_by_queue_items(
        self, validator_block: int, validator_hotkey: str, items: List[OrderQueueSchema]
    ) -> Dict[str, OrderQueueStatus]:
        pass

    @abstractmethod
    async def get_by_campaign_items(
        self,
        campaign_items: List[str],
        page_number: int = 1,
        page_size: int = 500,
    ) -> List[BitAdsDataSchema]:
        pass
