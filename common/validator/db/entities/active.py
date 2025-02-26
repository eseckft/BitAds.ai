from datetime import datetime
from typing import Dict, Any
from typing import Optional

from sqlalchemy import String, Enum, DateTime, Integer, Boolean, Float, text, PickleType
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from common.schemas.campaign import CampaignType
from common.schemas.device import Device
from common.schemas.sales import SalesStatus, OrderQueueStatus

Base = declarative_base()


class MinerPing(Base):
    """
    Represents pings from miners recorded at specific blocks.

    Attributes:
        id (int): Unique identifier for each ping.
        hot_key (str): Hotkey of the miner sending the ping.
        block (int): Block number at which the ping occurred.
        created_at (datetime): Timestamp of when the ping was recorded.
    """

    __tablename__ = "miner_pings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hot_key: Mapped[str] = mapped_column(String, nullable=False)
    block: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class Campaign(Base):
    """
    Represents advertising campaigns managed by the system.

    Attributes:
        id (str): Unique identifier for each campaign.
        status (bool): Boolean indicating if the campaign is active.
        last_active_block (int): Block number when the campaign was last active.
        created_at (datetime): Timestamp of when the campaign was created.
        updated_at (datetime): Timestamp of when the campaign was last updated.
        umax (float): Maximum value assigned to the campaign.
        type (CampaignType): Type of the campaign ('REGULAR' or 'CPA').

    Note:
        Default campaign type is 'REGULAR'.
    """

    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    last_active_block: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    umax: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    type: Mapped[CampaignType] = mapped_column(
        Enum(CampaignType), nullable=False, server_default=text("REGULAR")
    )
    cpa_blocks: Mapped[Optional[int]]


class BitAdsData(Base):
    __tablename__ = "bitads_data"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    # Common data:
    user_agent: Mapped[str]
    ip_address: Mapped[str]
    country: Mapped[Optional[str]]
    country_code: Mapped[Optional[str]]
    is_unique: Mapped[bool]
    device: Mapped[Optional[Device]] = mapped_column(Enum(Device), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    campaign_id: Mapped[Optional[str]]
    sales_status: Mapped[Optional[SalesStatus]] = mapped_column(
        Enum(SalesStatus), nullable=False, server_default=text("NEW")
    )

    # Validator data:
    validator_block: Mapped[Optional[int]]
    validator_hotkey: Mapped[Optional[int]]
    refund: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    sales: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    sale_amount: Mapped[float] = mapped_column(Float, server_default=text("0.0"))
    order_info: Mapped[Dict[str, Any]] = mapped_column(PickleType, nullable=True)
    refund_info: Mapped[Dict[str, Any]] = mapped_column(PickleType, nullable=True)
    sale_date: Mapped[Optional[datetime]]  # Needed for updating sales_status

    # Miner data:
    referer: Mapped[Optional[str]]
    campaign_item: Mapped[Optional[str]]
    miner_hotkey: Mapped[Optional[str]]
    miner_block: Mapped[Optional[str]]
    return_in_site: Mapped[Optional[bool]]

    __mapper_args__ = {
        "confirm_deleted_rows": False
    }

class MinerAssignment(Base):
    __tablename__ = "miner_assignment"

    unique_id: Mapped[str] = mapped_column(String, primary_key=True)
    hotkey: Mapped[str]
    campaign_id: Mapped[Optional[str]]


class OrderQueue(Base):
    __tablename__ = "order_queue"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    order_info: Mapped[Dict[str, Any]] = mapped_column(PickleType)
    refund_info: Mapped[Dict[str, Any]] = mapped_column(PickleType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_processing_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    status: Mapped[OrderQueueStatus] = mapped_column(
        Enum(OrderQueueStatus), default=OrderQueueStatus.PENDING
    )

    __mapper_args__ = {
        "confirm_deleted_rows": False
    }


class MinersMetadata(Base):
    __tablename__ = "miners_metadata"

    hotkey: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_offset: Mapped[Optional[datetime]]
