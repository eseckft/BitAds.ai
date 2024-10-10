from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from common.schemas.campaign import CampaignType
from common.schemas.device import Device
from common.schemas.visit import VisitStatus

from typing import Dict, Any


class InitVisitRequest(BaseModel):
    """
    Pydantic model representing an initialization request for a visit.

    Attributes:
        device (Optional[Device]): Optional device information for the visit.
    """

    device: Optional[Device] = None


class Action(str, Enum):
    """
    Enum defining possible actions for tracking data.

    Attributes:
        image_click: Action for image click.
        mouse_movement: Action for mouse movement.
        read_more_click: Action for read more click.
        through_rate_click: Action for through rate click.
        update_visit_duration: Action for updating visit duration.
        refund: Action for refund.
        sale: Action for sale.
    """

    image_click = "image_click"
    mouse_movement = "mouse_movement"
    read_more_click = "read_more_click"
    through_rate_click = "through_rate_click"
    update_visit_duration = "update_visit_duration"
    refund = "refund"
    sale = "sale"


class ActionRequest(BaseModel):
    """
    Pydantic model representing a request for an action.

    Attributes:
        type (Action): Type of action to perform.
        amount (float): Amount associated with the action (default: 0.0).
    """

    type: Action
    amount: float = 0.0


class ValidatorTrackingData(BaseModel):
    """
    Pydantic model representing tracking data for a validator.

    Attributes:
        id (str): Identifier for the tracking data.
        user_agent (str): User agent string.
        ip_address (str): IP address.
        country (Optional[str]): Country associated with the tracking data (optional).
        campaign_id (str): Identifier of the associated campaign.
        validator_block (int): Validator block number.
        validator_hotkey (str): Validator hotkey.
        at (bool): Boolean indicating whether the tracking data is at.
        device (Optional[Device]): Optional device information.
        created_at (Optional[datetime]): Optional timestamp of creation.
        updated_at (Optional[datetime]): Optional timestamp of last update.
        status (Optional[VisitStatus]): Optional visit status.

        count_image_click (Optional[int]): Optional count of image clicks.
        count_mouse_movement (Optional[int]): Optional count of mouse movements.
        count_read_more_click (Optional[int]): Optional count of read more clicks.
        count_through_rate_click (Optional[int]): Optional count of through rate clicks.
        visit_duration (Optional[int]): Optional visit duration in seconds.
        is_unique (Optional[bool]): Optional boolean indicating uniqueness of the visit.

        model_config (ConfigDict): Configuration for model attributes, frozen after initialization.
    """

    id: str
    user_agent: str
    ip_address: str
    country: Optional[str] = None
    campaign_id: Optional[str] = None
    validator_block: int
    validator_hotkey: str
    at: bool
    device: Optional[Device] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: Optional[VisitStatus] = None

    count_image_click: Optional[int] = None
    count_mouse_movement: Optional[int] = None
    count_read_more_click: Optional[int] = None
    count_through_rate_click: Optional[int] = None
    visit_duration: Optional[int] = None
    is_unique: Optional[bool] = None

    refund: Optional[int] = None
    sales: Optional[int] = None
    sale_amount: Optional[float] = None

    model_config = ConfigDict(from_attributes=True, frozen=True)


class MinerPingSchema(BaseModel):
    """
    Pydantic model representing a schema for miner ping data.

    Attributes:
        hot_key (str): Miner hotkey.
        block (int): Block number.
        created_at (Optional[datetime]): Optional timestamp of creation.

        model_config (ConfigDict): Configuration for model attributes, frozen after initialization.
    """

    hot_key: str
    block: int
    created_at: Optional[datetime] = None

    model_config: ConfigDict = ConfigDict(from_attributes=True)


class CampaignSchema(BaseModel):
    """
    Pydantic model representing a schema for campaign data.

    Attributes:
        id (str): Identifier for the campaign.
        status (bool): Status of the campaign.
        last_active_block (int): Last active block number.
        created_at (datetime): Timestamp of creation.
        updated_at (datetime): Timestamp of last update.
        umax (float): Umax value associated with the campaign.
        type (CampaignType): Type of the campaign.

        model_config (ConfigDict): Configuration for model attributes, frozen after initialization.
    """

    id: str
    status: bool
    last_active_block: int
    created_at: datetime
    updated_at: datetime
    umax: float
    type: CampaignType
    cpa_blocks: Optional[int] = Field(7200, alias="CPABlocks")

    model_config: ConfigDict = ConfigDict(from_attributes=True)
