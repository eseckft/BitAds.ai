from typing import Annotated

from fastapi import Depends

from common.db.database import DatabaseManager
from common.dependencies import get_database_manager
from common.services.queue.base import OrderQueueService
from common.services.queue.impl import OrderQueueServiceImpl
from common.services.validator.base import ValidatorService
from common.services.validator.impl import ValidatorServiceImpl
from neurons.old.validator.core import CoreValidator


def get_core_validator() -> CoreValidator:
    """
    Returns an instance of CoreValidator.

    Returns:
        CoreValidator: An instance of the CoreValidator class.
    """
    return CoreValidator()


def get_validator_service(
    database_manager: DatabaseManager,
) -> ValidatorService:
    """
    Creates and returns a ValidatorService instance.

    Args:
        database_manager (DatabaseManager): The database manager instance.

    Returns:
        ValidatorService: An instance of ValidatorServiceImpl configured with the provided DatabaseManager.
    """
    return ValidatorServiceImpl(database_manager)


def get_order_queue_service(
    database_manager: Annotated[DatabaseManager, Depends(get_database_manager)]
) -> OrderQueueService:
    return OrderQueueServiceImpl(database_manager)
