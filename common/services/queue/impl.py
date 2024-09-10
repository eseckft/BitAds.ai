from common.services.queue.exceptions import RefundNotExpectedWithoutOrder
from common.validator.schemas import Action

from common.db.database import DatabaseManager
from common.db.repositories import order_queue
from common.schemas.shopify import SaleData
from common.services.queue.base import OrderQueueService


class OrderQueueServiceImpl(OrderQueueService):
    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager

    async def add_to_queue(self, id_: str, sale_data: SaleData):
        with self.database_manager.get_session("active") as session:
            existed_data = order_queue.get_by_id(session, id_)
            if existed_data:
                kwargs = {
                    "order_info"
                    if Action.sale == sale_data.type
                    else "refund_info": sale_data.order_details
                }
                order_queue.update_data(session, id_, **kwargs)
                return

            if sale_data.type == Action.refund:
                raise RefundNotExpectedWithoutOrder

            order_queue.add_data(session, id_, sale_data.order_details)
