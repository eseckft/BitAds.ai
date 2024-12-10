"""
Miner Dependencies
"""

from common.db.database import DatabaseManager
from common.helpers import const
from common.services.migration.base import MigrationService
from common.services.migration.miner import MinerMigrationService
from common.services.miner.base import MinerService
from common.services.miner.impl import MinerServiceImpl
from common.services.recent_activity.base import RecentActivityService
from common.services.recent_activity.impl import RecentActivityServiceImpl
from neurons.miner.core import CoreMiner


def get_core_miner() -> CoreMiner:
    """
    Retrieves an instance of the CoreMiner.

    Returns:
        CoreMiner: Instance of the CoreMiner.
    """
    return CoreMiner()


def get_miner_service(database_manager: DatabaseManager) -> MinerService:
    """
    Retrieves an instance of MinerService using the provided DatabaseManager and RETURN_IN_SITE_DELTA constant.

    Args:
        database_manager (DatabaseManager): Instance of DatabaseManager.

    Returns:
        MinerService: Instance of MinerService.
    """
    return MinerServiceImpl(database_manager, const.RETURN_IN_SITE_DELTA)


def get_recent_activity_service(
    database_manager: DatabaseManager,
) -> RecentActivityService:
    return RecentActivityServiceImpl(database_manager)


def get_migration_service(database_manager: DatabaseManager) -> MigrationService:
    return MinerMigrationService(database_manager)
