"""
Aggregation schemas
"""
from typing import Dict

from pydantic import BaseModel


class AggregationSchema(BaseModel):
    """
    Schema representing aggregated data for various metrics.

    Attributes:
        visits (int): Total number of visits.
        visits_unique (int): Total number of unique visits.
        at (int): Number of AT (Attention Token) units.
        count_through_rate_click (int): Number of click-through rate clicks.
        total_sales (int): Total number of sales.
        total_refunds (int): Total number of refunds.
        sales_amount (float): Total amount of sales in monetary value.
    """

    visits: int = 0
    visits_unique: int = 0
    at: int = 0
    count_through_rate_click: int = 0
    total_sales: int = 0
    total_refunds: int = 0
    sales_amount: float = 0.0


class AggregatedData(BaseModel):
    """
    Model representing aggregated data grouped by campaigns.

    Attributes:
        data (Dict[str, Dict[str, AggregationSchema]]):
            A dictionary containing campaigns as keys, each mapping to another dictionary where keys are
            miner hotkeys and values are instances of AggregationSchema representing aggregated data.
    """

    data: Dict[str, Dict[str, AggregationSchema]]
