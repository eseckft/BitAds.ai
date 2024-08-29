from common.miner.schemas import VisitorSchema
from common.schemas.completed_visit import CompletedVisitSchema
from common.validator.schemas import ValidatorTrackingData


def to_completed_visit(
    validator_data: ValidatorTrackingData,
    miner_data: VisitorSchema,
    complete_block: int,
) -> CompletedVisitSchema:
    """
    Converts validator tracking data and miner data into a completed visit schema.

    Args:
        validator_data (ValidatorTrackingData): Validator tracking data to include in the completed visit.
        miner_data (VisitorSchema): Miner data to include in the completed visit.
        complete_block (int): Block number indicating when the visit was completed.

    Returns:
        CompletedVisitSchema: Completed visit schema containing merged data from validator and miner.

    Raises:
        None

    Notes:
        The function merges the dictionaries created from `validator_data` and `miner_data`.
        It then constructs a CompletedVisitSchema object using the merged data and `complete_block`.
    """
    result = validator_data.dict() | miner_data.dict()
    return CompletedVisitSchema(complete_block=complete_block, **result)
