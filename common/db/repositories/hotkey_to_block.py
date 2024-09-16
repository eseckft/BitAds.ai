from typing import Tuple, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from common.db.entities import HotkeyToBlock


def get_hotkey_to_block(session: Session) -> Optional[Tuple[str, int]]:
    # Query to get the hotkey and last_block with the latest block
    stmt = (
        select(HotkeyToBlock.hotkey, HotkeyToBlock.last_block)
        .order_by(HotkeyToBlock.last_block.desc())
        .limit(1)
    )

    result = session.execute(stmt).first()

    return result


def set_hotkey_and_block(session: Session, hotkey: str, block: int) -> None:
    entity = session.get(HotkeyToBlock, hotkey)
    if not entity:
        entity = HotkeyToBlock(hotkey=hotkey, last_block=block)
        session.add(entity)
    else:
        entity.last_block = block