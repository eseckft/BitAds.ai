from typing import List

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from common.db.entities import MinerOrderHistory
from common.schemas.bitads import BitAdsDataSchema
from common.schemas.order_history import MinerOrderHistoryModel
from common.schemas.sales import OrderNotificationStatus


def add_record(
    session: Session,
    data: BitAdsDataSchema,
    hotkey: str,
    status: OrderNotificationStatus = OrderNotificationStatus.NEW,
) -> bool:
    entity = session.get(MinerOrderHistory, data.id)
    if entity:
        entity.data = data.model_dump(mode="json")
        entity.status = status
        return False
    entity = MinerOrderHistory(
        id=data.id, hotkey=hotkey, data=data.model_dump(mode="json"), status=status
    )
    session.add(entity)
    return True


def get_history(session: Session, limit: int = 50) -> List[MinerOrderHistoryModel]:
    stmt = select(MinerOrderHistory)

    stmt = stmt.limit(limit).order_by(desc(MinerOrderHistory.created_at))

    result = session.execute(stmt)
    return [MinerOrderHistoryModel.model_validate(r) for r in result.scalars().all()]
