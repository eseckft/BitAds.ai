from datetime import datetime

from common import utils
from common.miner.schemas import VisitorSchema
from common.schemas.completed_visit import CompletedVisitSchema
from common.schemas.shopify import SaleData
from common.validator.schemas import ValidatorTrackingData, Action


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


def to_bitads_extra_data(sale_data: SaleData):
    return (
        dict(order_info=sale_data.order_details, sale_date=sale_data.order_details.sale_date)
        if sale_data.type == Action.sale
        else dict(refund_info=sale_data.order_details)
    )


def to_extra_amounts(sale_data: SaleData, ndigits: int = 5):
    modifier = 1 if sale_data.type == Action.sale else -1
    sales_amount = round(sum(float(i.price) for i in sale_data.order_details.items), ndigits)
    return {
        "sale_amount": sales_amount * modifier,
        "sales"
        if sale_data.type == Action.sale
        else "refund": len(sale_data.order_details.items)
    }


def to_tracking_data(
    id_: str,
    sale_data: SaleData,
    user_agent: str,
    ip_address: str,
    country: str,
    current_block: int,
    validator_hotkey: str,
):
    return ValidatorTrackingData(
        id=id_,
        user_agent=user_agent,
        ip_address=ip_address,
        country=country,
        validator_block=current_block,
        at=False,
        device=utils.determine_device(user_agent),
        validator_hotkey=validator_hotkey,
        **to_extra_amounts(sale_data)
    )
