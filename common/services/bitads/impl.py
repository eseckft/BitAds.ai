import logging
from datetime import datetime
from typing import List, Set

from common import converters
from common.db.database import DatabaseManager
from common.db.repositories import bitads_data
from common.miner.schemas import VisitorSchema
from common.schemas.bitads import BitAdsDataSchema
from common.schemas.completed_visit import CompletedVisitSchema
from common.schemas.sales import SalesStatus
from common.schemas.shopify import SaleData
from common.services.bitads.base import BitAdsService
from common.validator.schemas import ValidatorTrackingData


log = logging.getLogger(__name__)


class BitAdsServiceImpl(BitAdsService):
    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager

    async def add_or_update_validator_bitads_data(
        self, validator_data: ValidatorTrackingData, sale_data: SaleData
    ):
        with self.database_manager.get_session("active") as session:
            data = validator_data.model_dump() | converters.to_bitads_extra_data(
                sale_data
            )
            bitads_data.add_or_update(
                session,
                BitAdsDataSchema(
                    **data,
                    country_code=sale_data.order_details.customer_info.address.country_code,
                ),
            )

    async def get_bitads_data_between(
        self,
        updated_from: datetime = None,
        updated_to: datetime = None,
        page_number: int = 1,
        page_size: int = 500,
    ) -> List[BitAdsDataSchema]:
        limit = page_size
        offset = (page_number - 1) * page_size
        with self.database_manager.get_session("active") as session:
            return bitads_data.get_data_between(
                session, updated_from, updated_to, limit, offset
            )

    async def get_last_update_bitads_data(self, exclude_hotkey: str):
        with self.database_manager.get_session("active") as session:
            return bitads_data.get_max_date_excluding_hotkey(session, exclude_hotkey)

    async def add_by_visits(self, visits: Set[VisitorSchema]) -> None:
        with self.database_manager.get_session("active") as session:
            for visit in visits:
                bitads_data.add_or_update(
                    session, BitAdsDataSchema(**visit.model_dump())
                )

    async def add_bitads_data(self, datas: Set[BitAdsDataSchema]) -> None:
        with self.database_manager.get_session("active") as session:
            for data in datas:
                bitads_data.add_or_update(session, data)

    async def get_data_by_ids(self, ids: Set[str]) -> Set[BitAdsDataSchema]:
        result = set()
        with self.database_manager.get_session("active") as session:
            for id_ in ids:
                data = bitads_data.get_data(session, id_)
                if data:
                    result.add(data)
        return result

    async def add_completed_visits(self, visits: List[CompletedVisitSchema]):
        datas = {
            BitAdsDataSchema(
                **v.model_dump(exclude={"complete_block"}),
                sales_status=SalesStatus.COMPLETED,
            )
            for v in visits
        }
        await self.add_bitads_data(datas)

    async def update_sale_status_if_needed(self, sale_date_from: datetime) -> None:
        log.debug(f"Completing sales with date less than: {sale_date_from}")
        with self.database_manager.get_session("active") as session:
            bitads_data.complete_sales_less_than_date(session, sale_date_from)
