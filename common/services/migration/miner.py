from datetime import datetime

from common.db import migration
from common.miner.db.entities.active import Visitor, VisitorActivity, UserAgent
from common.services.migration.base import MigrationService


class MinerMigrationService(MigrationService):
    async def migrate(self, created_at_from: datetime):
        with self.database_manager.get_session(
            "active"
        ) as active_session, self.database_manager.get_session(
            "history"
        ) as history_session:
            migration.transfer_data(active_session, history_session, Visitor, created_at_from)
            migration.transfer_data(active_session, history_session, VisitorActivity, created_at_from)
