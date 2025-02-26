"""
Database entities
"""

from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import DateTime, Enum, String, Integer, PickleType
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from common.schemas.campaign import CampaignType
from common.schemas.sales import OrderNotificationStatus

Base = declarative_base()


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
    created_at: Mapped[Optional[datetime]]
    date_started: Mapped[Optional[datetime]]
    date_approved: Mapped[Optional[datetime]]
    product_name: Mapped[Optional[str]]
    store_name: Mapped[Optional[str]]
    validator_id: Mapped[Optional[int]]
    country_of_registration: Mapped[Optional[str]]
    company_registration_number: Mapped[Optional[str]]
    countries_approved_for_product_sales: Mapped[Optional[str]]
    updated_at: Mapped[Optional[datetime]]
    product_refund_period_duration: Mapped[Optional[int]]


class TwoFactorCodes(Base):
    __tablename__ = "two_factor_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ip_address: Mapped[str]
    user_agent: Mapped[Optional[str]]
    hotkey: Mapped[str]
    code: Mapped[str]


class MinerUniqueLink(Base):
    __tablename__ = "miner_unique_link"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    campaign_id: Mapped[str]
    hotkey: Mapped[str]
    link: Mapped[str]


class MinerOrderHistory(Base):
    __tablename__ = "miner_order_history"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_processing_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    hotkey: Mapped[str]
    data: Mapped[Dict[str, Any]] = mapped_column(PickleType)
    status: Mapped[OrderNotificationStatus] = mapped_column(
        Enum(OrderNotificationStatus), default=OrderNotificationStatus.NEW
    )
