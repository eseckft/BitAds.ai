from common.db.database import DatabaseManager
from common.services.validator.base import ValidatorService
from common.services.validator.impl import ValidatorServiceImpl
from neurons.validator.core import CoreValidator


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
