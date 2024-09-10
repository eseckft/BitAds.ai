from sqlalchemy.orm import Session

from common.validator.db.entities.active import MinerAssignment


def create_or_update_miner_assignment(
    session: Session, unique_id: str, hotkey: str
):
    # Try to find an existing record with the given unique_id
    miner_assignment = session.get(MinerAssignment, unique_id)
    if not miner_assignment:
        miner_assignment = MinerAssignment(unique_id=unique_id, hotkey=hotkey)
        session.add(miner_assignment)
    else:
        # If found, update the hotkey
        miner_assignment.hotkey = hotkey
