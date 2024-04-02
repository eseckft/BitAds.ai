from typing import List, Any, Optional, Union, Set

import pydantic
from pydantic import Field


class BaseResponse(pydantic.BaseModel):
    errors: Optional[List[int]] = None


class PingResponse(BaseResponse):
    result: bool
    miners: Optional[Set[str]] = None
    validators: Optional[List[str]] = None


class Campaign(pydantic.BaseModel):
    in_progress: int
    product_title: str
    created_at: str
    is_aggregate: int
    product_unique_id: str
    validator_id: int
    status: int
    product_button_link: str
    date_end: str
    product_count_day: int
    updated_at: str
    product_short_description: str
    product_full_description: str
    test: int
    product_button_text: str
    product_images: str  # TODO: not real list
    product_theme: str
    id: str
    uid: Optional[str] = None


class Aggregation(pydantic.BaseModel):
    id: Union[str, int]
    miner_wallet_address: str
    product_unique_id: str
    product_item_unique_id: str
    visits_unique: int
    count_through_rate_click: int


class TaskResponse(BaseResponse):
    result: bool
    u_max: int = Field(alias="Umax")
    ctr_max: float = Field(alias="CTRmax")
    wu: float = Field(alias="Wu")
    wc: float = Field(alias="Wc")
    campaign: List[Campaign]
    aggregation: List[Aggregation]


class GetMinerUniqueIdResponse(BaseResponse):
    product_unique_id: Optional[Union[int, str]] = None
    product_item_unique_id: Optional[Union[int, str]] = None
    hot_key: Optional[str] = Field(None, alias="hotKey")

    class Config:
        extra = "allow"


class Score(pydantic.BaseModel):
    ctr: float
    u_norm: float
    ctr_norm: float
    ctr_max: float
    wu: float
    wc: float
    u_max: float
    rating: float
