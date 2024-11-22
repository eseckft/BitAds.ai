from typing import List, Optional

from common.db.repositories import miner_assignment

from common.db.database import DatabaseManager

from common.schemas.miner_assignment import MinerAssignmentModel
from common.services.miner_assignment.base import MinerAssignmentService


class MinerAssignmentServiceImpl(MinerAssignmentService):
    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager

    async def get_miner_assignments(self) -> List[MinerAssignmentModel]:
        with self.database_manager.get_session("active") as session:
            return miner_assignment.get_assignments(session)

    async def set_miner_assignments(self, assignments: List[MinerAssignmentModel]):
        with self.database_manager.get_session("active") as session:
            for assignment in assignments:
                miner_assignment.create_or_update_miner_assignment(
                    session,
                    assignment.unique_id,
                    assignment.hotkey,
                    assignment.campaign_id,
                )

    async def get_hotkey_by_campaign_item(self, campaign_item: str) -> Optional[str]:
        with self.database_manager.get_session("active") as session:
            return miner_assignment.get_hotkey_by_campaign_item(session, campaign_item)