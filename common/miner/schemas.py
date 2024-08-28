"""
Miner schemas
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from common.schemas.device import Device
from common.schemas.visit import VisitStatus


class VisitorSchema(BaseModel):
    """
    Schema representing a visitor entity with detailed attributes.

    Attributes:
        id (str): Unique identifier for the visitor.
        ip_address (str): IP address of the visitor.
        referer (Optional[str], optional): Referer URL from where the visitor came. Defaults to None.
        user_agent (str): User agent string of the visitor.
        campaign_id (str): ID of the campaign associated with the visitor.
        campaign_item (str): Specific item or page within the campaign associated with the visitor.
        miner_hotkey (str): Hotkey identifier of the miner associated with the visitor.
        miner_block (int): Block number related to the miner.
        at (bool): Boolean indicating the state of 'at'.
        device (Optional[Device], optional): Device information of the visitor. Defaults to None.
        is_unique (Optional[bool], optional): Boolean indicating if the visitor is unique. Defaults to None.
        return_in_site (bool, optional): Boolean indicating if the visitor has returned to the site. Defaults to False.
        country (Optional[str], optional): Country of origin of the visitor. Defaults to None.
        status (Optional[VisitStatus], optional): Visit status of the visitor. Defaults to None.
        created_at (Optional[datetime], optional): Date and time when the visitor record was created. Defaults to None.

    Config:
        model_config (ConfigDict): Configuration dictionary for the model, enabling attribute conversion and freezing.
    """

    id: str
    referer: Optional[str] = None
    ip_address: str
    country: Optional[str] = None
    country_code: Optional[str] = None
    user_agent: str
    campaign_id: str
    campaign_item: str
    miner_hotkey: str
    miner_block: int
    at: bool
    device: Optional[Device] = None
    is_unique: Optional[bool] = None
    return_in_site: bool = False
    status: Optional[VisitStatus] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, frozen=True)


class VisitorActivitySchema(BaseModel):
    """
    Schema representing visitor activity information.

    Attributes:
        ip (str): IP address of the visitor.
        date (date): Date of the activity.
        count (int): Count of the activity.

    Config:
        model_config (ConfigDict): Configuration dictionary for the model, enabling attribute conversion.
    """

    ip: str
    date: date
    count: int

    model_config = ConfigDict(from_attributes=True)
