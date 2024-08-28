"""
Completed visits schemas
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from common.schemas.device import Device


class CompletedVisitSchema(BaseModel):
    """
    Schema representing a completed visit entity.

    Attributes:
        id (str): The unique identifier for the visit.
        referer (Optional[str], optional): The referer URL, if available.
        ip_address (str): The IP address of the visitor.
        country (Optional[str], optional): The country of the visitor.
        user_agent (str): The user agent string of the visitor.
        campaign_id (str): The ID of the campaign associated with the visit.
        campaign_item (str): The item or page within the campaign.
        miner_hotkey (str): The hotkey of the miner associated with the visit.
        at (bool): Boolean indicating whether the visit is at.
        device (Optional[Device], optional): The type of device used by the visitor.
        is_unique (bool): Boolean indicating if the visit is unique.
        return_in_site (bool): Boolean indicating if the visitor returned to the site.
        count_image_click (int): Count of image clicks during the visit.
        count_mouse_movement (int): Count of mouse movements during the visit.
        count_read_more_click (int): Count of 'read more' clicks during the visit.
        count_through_rate_click (int): Count of through rate clicks during the visit.
        miner_block (int): Number of blocks mined by the miner during the visit.
        validator_block (int): Number of blocks validated during the visit.
        complete_block (int): Number of blocks completed during the visit.
        created_at (datetime, optional): The timestamp when the visit was completed.
        model_config (ConfigDict, optional): Configuration dictionary for Pydantic model.

    Note:
        The `created_at` attribute defaults to the current UTC timestamp using `datetime.utcnow`.
    """

    id: str
    referer: Optional[str] = None
    ip_address: str
    country: Optional[str] = None
    user_agent: str
    campaign_id: str
    campaign_item: str
    miner_hotkey: str
    at: bool
    device: Optional[Device] = None
    is_unique: bool
    return_in_site: bool
    count_image_click: int
    count_mouse_movement: int
    count_read_more_click: int
    count_through_rate_click: int
    miner_block: int
    validator_block: int
    complete_block: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    refund: Optional[int] = None
    sales: Optional[int] = None
    sale_amount: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
