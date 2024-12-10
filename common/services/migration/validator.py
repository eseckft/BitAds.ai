from datetime import datetime

from common.db import migration
from common.services.migration.base import MigrationService
from common.validator.db.entities.active import BitAdsData, OrderQueue


class ValidatorMigrationService(MigrationService):
    async def migrate(self, created_at_from: datetime):

        with self.database_manager.get_session(
            "active"
        ) as active_session, self.database_manager.get_session(
            "history"
        ) as history_session:
            migration.transfer_data(active_session, history_session, BitAdsData, created_at_from)
            migration.transfer_data(active_session, history_session, OrderQueue, created_at_from)
