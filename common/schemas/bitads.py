"""
BitAds schemas
"""
from datetime import datetime
from enum import IntEnum
from typing import Optional, List, Set, Dict

from pydantic import BaseModel, Field, ConfigDict

from common.miner.schemas import VisitorActivitySchema
from common.schemas.campaign import CampaignType
from common.schemas.device import Device
from common.schemas.sales import SalesStatus
from common.schemas.shopify import OrderDetails


class BaseResponse(BaseModel):
    """
    Base response model for API responses.

    Attributes:
        errors (Optional[List[int]]): List of error codes if errors occurred, default is None.
    """

    errors: Optional[List[int]] = None


class Setting(BaseModel):
    """
    Model representing a setting with name and value.

    Attributes:
        name (str): Name of the setting.
        value (str): Value of the setting.
    """

    name: str
    value: str


class Campaign(BaseModel):
    """
    Model representing a campaign.

    Attributes:
        in_progress (int): Number indicating if the campaign is in progress.
        product_title (str): Title of the product associated with the campaign.
        created_at (datetime): Date and time when the campaign was created.
        is_aggregate (int): Number indicating if the campaign is an aggregate.
        product_unique_id (str): Unique ID of the product associated with the campaign.
        validator_id (int): ID of the validator associated with the campaign.
        status (int): Status of the campaign.
        product_button_link (str): Link associated with the product button.
        date_end (datetime): End date and time of the campaign.
        product_count_day (int): Count of the product per day.
        updated_at (datetime): Date and time when the campaign was last updated.
        product_short_description (str): Short description of the product associated with the campaign.
        product_full_description (str): Full description of the product associated with the campaign.
        product_button_text (str): Text on the product button associated with the campaign.
        product_images (str): Images of the product associated with the campaign.
        product_theme (str): Theme of the product associated with the campaign.
        id (str): ID of the campaign.
        type (CampaignType): Type of the campaign, defaults to CampaignType.REGULAR.
    """

    # in_progress: Optional[int] = None
    # product_title: Optional[str] = None
    # created_at: Optional[datetime] = None
    # is_aggregate: Optional[int] = None
    product_unique_id: str
    # validator_id: Optional[int] = None
    status: Optional[int] = None
    # product_button_link: Optional[str] = None
    # date_end: Optional[datetime] = None
    # product_count_day: Optional[int] = None
    # updated_at: Optional[datetime] = None
    # product_short_description: Optional[str] = None
    # product_full_description: Optional[str] = None
    # product_button_text: Optional[str] = None
    # product_images: Optional[str] = None
    # product_theme: Optional[str] = None
    product_link: Optional[str] = None
    id: str
    type: CampaignType = CampaignType.REGULAR

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class CampaignStatus(IntEnum):
    DEACTIVATED = 0
    ACTIVATED = 1


class PingResponse(BaseResponse):
    """
    Response model for the ping endpoint.

    Attributes:
        result (bool): Result of the ping operation.
        miners (Optional[Set[str]]): Set of miner IDs, default is an empty set.
        validators (Optional[Set[str]]): Set of validator IDs, default is an empty set.
        settings (Optional[List[Setting]]): List of settings, default is an empty list.
        campaigns (Optional[List[Campaign]]): List of campaigns, default is an empty list.
    """

    result: bool
    miners: Optional[Set[str]] = set()
    validators: Optional[Set[str]] = set()
    settings: Optional[List[Setting]] = list()
    campaigns: Optional[List[Campaign]] = list()


class UniqueIdData(BaseModel):
    """
    Model representing data containing a link and miner unique ID.

    Attributes:
        link (str): Link associated with the data.
        miner_unique_id (str): Miner unique ID, aliased as 'minerUniqueId'.
    """

    link: str
    miner_unique_id: str = Field(alias="minerUniqueId")


class GetMinerUniqueIdResponse(BaseResponse):
    """
    Response model for getting miner unique ID.

    Attributes:
        data (UniqueIdData): Data containing link and miner unique ID.
    """

    data: UniqueIdData


class FormulaParams(BaseModel):
    """
    Model representing parameters for a formula.

    Attributes:
        ctr_max (float): Maximum click-through rate.
        wuv (float): Weight for unique visits.
        wctr (float): Weight for click-through rate.
        wats (float): Weight for AT (Attention Token) units.
        wuvps (float): Weight for unique visits per second.
        total_visits_duration (int): Total visits duration.
        unique_visits_duration (int): Unique visits duration.
        ctr_clicks_seconds (int): Click-through rate clicks per second.
        sales_max (float): Maximum sales amount.
        cr_max (float): Maximum conversion rate.
        mr_max (int): Maximum return rate.
        w_sales (float): Weight for sales.
        w_cr (float): Weight for conversion rate.
        w_mr (float): Weight for return rate.

    Methods:
        default_instance(): Returns a default instance of FormulaParams.
        from_settings(settings: List[Setting]): Creates an instance of FormulaParams from a list of settings.
    """

    ctr_max: float = Field(0.20, alias="CTRmax")
    wuv: float = Field(0.5, alias="Wu")
    wctr: float = Field(0.5, alias="Wc")
    wats: float = Field(0.8, alias="Wats")
    wuvps: float = Field(0.2, alias="Wuvps")
    total_visits_duration: int = 2
    unique_visits_duration: int = 2
    ctr_clicks_seconds: int = 3
    sales_max: float = Field(600.0, alias="SALESmax")
    cr_max: float = Field(2.0, alias="CRmax")
    mr_max: float = Field(100, alias="MRmax")
    w_sales: float = Field(0.9, alias="Wsales")
    w_cr: float = Field(0.05, alias="Wcr")
    w_mr: float = Field(0.05, alias="Wmr")
    cpa_blocks: int = Field(7200, alias="CPABlocks")
    mr_blocks: int = Field(216000, alias="MRBlocks")
    evaluate_miners_blocks: int = Field(100, alias="EvaluateMinersBlocks")

    @classmethod
    def default_instance(cls):
        """
        Returns a default instance of FormulaParams with default values.

        Returns:
            FormulaParams: Default instance of FormulaParams.
        """
        return FormulaParams()

    @classmethod
    def from_settings(cls, settings: List[Setting]):
        """
        Creates an instance of FormulaParams from a list of settings.

        Args:
            settings (List[Setting]): List of settings to initialize FormulaParams attributes.

        Returns:
            FormulaParams: Instance of FormulaParams initialized from settings.
        """
        settings_dict = {setting.name: setting.value for setting in settings}
        return cls(**settings_dict)


class SystemLoad(BaseModel):
    """
    Model representing system load information.

    Attributes:
        timestamp (str): Timestamp of the system load information.
        hostname (str): Hostname of the system.
        load_average (Dict[str, float]): Dictionary of load averages with keys '1m', '5m', and '15m'.
    """

    timestamp: str
    hostname: str
    load_average: Dict[str, float]


class UserActivityRequest(BaseModel):
    """
    Model representing a request containing user activity data.

    Attributes:
        user_activity (Dict[str, List[VisitorActivitySchema]]):
            Dictionary where keys are identifiers and values are lists of VisitorActivitySchema representing user activity.
    """

    user_activity: Dict[str, List[VisitorActivitySchema]]


class BitAdsDataSchema(BaseModel):
    id: str

    # Common data:
    user_agent: str
    ip_address: str
    country: Optional[str] = None
    country_code: Optional[str] = None
    at: bool
    is_unique: bool
    device: Optional[Device] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    campaign_id: Optional[str] = None
    sales_status: Optional[SalesStatus] = None

    # Validator data:
    count_image_click: Optional[int] = None
    count_mouse_movement: Optional[int] = None
    count_read_more_click: Optional[int] = None
    count_through_rate_click: Optional[int] = None
    visit_duration: Optional[int] = None
    validator_block: Optional[int] = None
    validator_hotkey: Optional[str] = None
    refund: Optional[int] = None
    sales: Optional[int] = None
    sale_amount: Optional[float] = None
    order_info: Optional[OrderDetails] = None
    refund_info: Optional[OrderDetails] = None
    sale_date: Optional[datetime] = None

    # Miner data:
    referer: Optional[str] = None
    campaign_item: Optional[str] = None
    miner_hotkey: Optional[str] = None
    miner_block: Optional[int] = None
    return_in_site: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True, frozen=True, use_enum_values=True)
