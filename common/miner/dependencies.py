"""
Miner Dependencies
"""
from typing import Annotated

from fastapi import Depends

from common import dependencies
from common.db.database import DatabaseManager
from common.helpers import const
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


def get_miner_service(
    database_manager: Annotated[
        DatabaseManager, Depends(dependencies.get_database_manager_from_env)
    ]
) -> MinerService:
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
