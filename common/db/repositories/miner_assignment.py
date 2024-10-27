from typing import List

from sqlalchemy.orm import Session

from common.schemas.miner_assignment import MinerAssignmentModel
from common.validator.db.entities.active import MinerAssignment


def create_or_update_miner_assignment(session: Session, unique_id: str, hotkey: str):
    # Try to find an existing record with the given unique_id
    miner_assignment = session.get(MinerAssignment, unique_id)
    if not miner_assignment:
        miner_assignment = MinerAssignment(unique_id=unique_id, hotkey=hotkey)
        session.add(miner_assignment)
    else:
        # If found, update the hotkey
        miner_assignment.hotkey = hotkey


def get_assignments(session: Session) -> List[MinerAssignmentModel]:
    # Query all MinerAssignment records from the database
    assignments = session.query(MinerAssignment).all()

    # Convert each SQLAlchemy model instance to a Pydantic model instance
    assignment_models = [
        MinerAssignmentModel.model_validate(assignment) for assignment in assignments
    ]

    return assignment_models
