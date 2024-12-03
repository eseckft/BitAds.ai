from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from common.schemas.miner_assignment import MinerAssignmentModel
from common.validator.db.entities.active import MinerAssignment


def create_or_update_miner_assignment(
    session: Session, unique_id: str, hotkey: str, campaign_id: str
):
    # Try to find an existing record with the given unique_id
    miner_assignment = session.get(MinerAssignment, unique_id)
    if not miner_assignment:
        miner_assignment = MinerAssignment(
            unique_id=unique_id, hotkey=hotkey, campaign_id=campaign_id
        )
        session.add(miner_assignment)
    else:
        # If found, update the hotkey
        miner_assignment.hotkey = hotkey
        miner_assignment.campaign_id = campaign_id


def get_assignments(session: Session) -> List[MinerAssignmentModel]:
    # Query all MinerAssignment records from the database
    assignments = session.query(MinerAssignment).all()

    # Convert each SQLAlchemy model instance to a Pydantic model instance
    assignment_models = [
        MinerAssignmentModel.model_validate(assignment) for assignment in assignments
    ]

    return assignment_models


def get_hotkey_by_campaign_item(session: Session, campaign_item: str) -> Optional[str]:
    """
    Fetches the hotkey associated with a given campaign item.

    Args:
        session (Session): The SQLAlchemy session to use for the query.
        campaign_item (str): The campaign item to search for.

    Returns:
        str: The hotkey associated with the campaign item.

    Raises:
        ValueError: If no record is found for the given campaign item.
    """
    stmt = select(MinerAssignment.hotkey).where(
        MinerAssignment.unique_id == campaign_item
    )
    result = session.execute(stmt).scalar_one_or_none()

    return result
