"""
Database entities
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, String, Integer, text, Float
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from common.schemas.campaign import CampaignType
from common.schemas.device import Device

Base = declarative_base()


class CompletedVisit(Base):
    """
    Database entity representing a completed visit record.

    Attributes:
        __tablename__ (str): The name of the database table.
        id (str): Primary key identifier for the completed visit.
        referer (str, optional): Referer URL for the visit.
        ip_address (str): IP address of the visitor.
        country (str, optional): Country of origin of the visitor.
        user_agent (str): User agent string of the visitor's browser.
        campaign_id (str): Identifier of the campaign associated with the visit.
        campaign_item (str): Specific item within the campaign.
        miner_hotkey (str): Hotkey identifier of the miner associated with the visit.
        at (bool): Boolean flag indicating if the visit was an 'at' event.
        device (Optional[Device]): Enum representing the type of device used by the visitor.
        is_unique (bool): Boolean flag indicating if the visit was unique.
        return_in_site (bool): Boolean flag indicating if the visit resulted in a return to the site.
        count_image_click (int): Count of image clicks during the visit.
        count_mouse_movement (int): Count of mouse movements during the visit.
        count_read_more_click (int): Count of 'read more' clicks during the visit.
        count_through_rate_click (int): Count of clicks related to through rate during the visit.
        miner_block (int): Block number associated with the miner.
        validator_block (int): Block number associated with the validator.
        complete_block (int): Block number indicating the completion of the visit.
        created_at (datetime): Timestamp indicating when the visit record was created.
    """

    __tablename__ = "completed_visit"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    referer: Mapped[str] = mapped_column(nullable=True)
    ip_address: Mapped[str]
    country: Mapped[str] = mapped_column(nullable=True)
    user_agent: Mapped[str]
    campaign_id: Mapped[str]
    campaign_item: Mapped[str]
    miner_hotkey: Mapped[str]
    at: Mapped[bool]
    device: Mapped[Optional[Device]] = mapped_column(Enum(Device))
    is_unique: Mapped[bool]
    return_in_site: Mapped[bool]

    count_image_click: Mapped[int]
    count_mouse_movement: Mapped[int]
    count_read_more_click: Mapped[int]
    count_through_rate_click: Mapped[int]

    miner_block: Mapped[int]
    validator_block: Mapped[int]
    complete_block: Mapped[int]

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    refund: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    sales: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    sale_amount: Mapped[float] = mapped_column(Float, server_default=text("0.0"))


class HotkeyToBlock(Base):
    __tablename__ = "hotkey_to_block"

    hotkey: Mapped[str] = mapped_column(primary_key=True)
    last_block: Mapped[int]


class CampaignEntity(Base):
    __tablename__ = "campaign"

    id: Mapped[str] = mapped_column(primary_key=True)
    type: Mapped[CampaignType] = mapped_column(Enum(CampaignType))
    product_unique_id: Mapped[str]
    status: Mapped[Optional[int]]
    product_link: Mapped[Optional[str]]
