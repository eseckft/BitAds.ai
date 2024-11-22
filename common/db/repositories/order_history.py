from common.db.entities import MinerOrderHistory
from common.schemas.bitads import BitAdsDataSchema
from sqlalchemy.orm import Session


def add_record(session: Session, data: BitAdsDataSchema, hotkey: str) -> bool:
    entity = session.get(MinerOrderHistory, data.id)
    if entity:
        entity.data = data.model_dump(mode="json")
        return False
    entity = MinerOrderHistory(id=data.id, hotkey=hotkey, data=data.model_dump(mode="json"))
    session.add(entity)
    return True
