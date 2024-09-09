from datetime import datetime
from typing import FrozenSet, Optional
from typing import TypeVar, Generic

from pydantic import BaseModel, Field, ConfigDict

from common.validator.schemas import Action


class Address(BaseModel):
    province: str
    country: str
    country_code: str = Field(alias="countryCode")

    model_config = ConfigDict(populate_by_name=True, frozen=True)


class CustomerInfo(BaseModel):
    id: str
    address: Address

    model_config = ConfigDict(frozen=True)


class Item(BaseModel):
    name: str
    price: str
    quantity: Optional[int] = None
    discount: Optional[str] = None
    gift_card: Optional[bool] = None
    currency: Optional[str] = None

    model_config = ConfigDict(frozen=True)


class ClientInfo(BaseModel):
    browser_ip: str
    user_agent: str

    model_config = ConfigDict(frozen=True)


class OrderDetails(BaseModel):
    totalAmount: str
    items: FrozenSet[Item]
    customer_info: CustomerInfo = Field(alias="customerInfo")
    client_info: ClientInfo = Field(alias="clientInfo")
    payment_method: str = Field(alias="paymentMethod")
    sale_date: datetime = None

    model_config = ConfigDict(populate_by_name=True, frozen=True)


class SaleData(BaseModel):
    order_hash: str
    visit_hash: str
    order_details: OrderDetails
    type: Action

    model_config = ConfigDict(extra="ignore")


class ShopifyData(BaseModel):
    type: Action
    data: SaleData


DATA = TypeVar("DATA", bound=BaseModel)


class ShopifyBody(BaseModel, Generic[DATA]):
    data: DATA
