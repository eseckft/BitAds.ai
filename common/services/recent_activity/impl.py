from typing import List

from common.db.database import DatabaseManager
from common.db.repositories import recent_activity
from common.miner.environ import Environ
from common.miner.schemas import VisitorActivitySchema
from common.services.recent_activity.base import RecentActivityService


class RecentActivityServiceImpl(RecentActivityService):
    def __init__(
        self,
        database_manager: DatabaseManager,
        recent_activity_days: int = Environ.RECENT_ACTIVITY_DAYS,
        recent_activity_count: int = Environ.RECENT_ACTIVITY_COUNT,
        recent_activity_limit: int = Environ.LIMIT_RECENT_ACTIVITY,
    ):
        self.database_manager = database_manager
        self.recent_activity_limit = recent_activity_limit
        self.recent_activity_days = recent_activity_days
        self.recent_activity_count = recent_activity_count

    async def get_recent_activity(
        self, recent_activity_count: int = None, limit: int = None
    ) -> List[VisitorActivitySchema]:
        with self.database_manager.get_session("active") as session:
            return recent_activity.get_recent_activity(
                session,
                recent_activity_count or self.recent_activity_count,
                limit or self.recent_activity_limit,
                self.recent_activity_days,
            )

    async def clear_old_recent_activity(self) -> None:
        with self.database_manager.get_session("active") as session:
            recent_activity.clean_old_data(session, self.recent_activity_days)
