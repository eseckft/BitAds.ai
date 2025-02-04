"""
This module defines SQLAlchemy ORM entities for managing visitor and user agent activities in the miner subsystem.

Classes:
    Visitor: Represents a visitor entity with attributes such as ID, referer, IP address, country, user agent,
             campaign details, miner hotkey, activity metrics, device information, uniqueness status,
             return in site status, visit status, and creation timestamp.
    VisitorActivity: Represents visitor activity entity with attributes including IP address, activity date,
                     and activity count.
    UserAgent: Represents user agent activity entity with attributes including user agent string, activity date,
               and activity count.

Notes:
    - These entities are mapped to corresponding database tables in the miner subsystem.
    - Visitor entity tracks detailed visitor information including campaign details and visit metrics.
    - VisitorActivity entity tracks activity counts based on IP address and date.
    - UserAgent entity tracks activity counts based on user agent string and date.
"""
from datetime import date
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, String, Date, Integer
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from common.schemas.device import Device
from common.schemas.visit import VisitStatus

Base = declarative_base()


class Visitor(Base):
    """
    SQLAlchemy ORM class representing visitor entities.

    Attributes:
        id (str): Primary key identifier for the visitor.
        referer (str, optional): Referring URL from which the visitor arrived.
        ip_address (str): IP address of the visitor.
        country (str, optional): Country of origin of the visitor.
        user_agent (str): User-agent string identifying the visitor's browser and OS.
        campaign_id (str): ID of the campaign associated with the visitor.
        campaign_item (str): Specific item or page within the campaign the visitor interacted with.
        miner_hotkey (str): Hotkey identifying the miner associated with the visitor.
        miner_block (int): Block number associated with the miner.
        at (float): Specific value associated with the visitor's interaction.
        device (Device, optional): Enum representing the device type used by the visitor.
        is_unique (bool): Flag indicating whether the visitor is unique within a specified timeframe.
        return_in_site (bool): Flag indicating whether the visitor returned to the site within a specified timeframe.
        status (VisitStatus): Enum representing the status of the visitor's visit, default is VisitStatus.new.
        created_at (datetime): Timestamp indicating when the visitor record was created.
    """

    __tablename__ = "visitors"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    referer: Mapped[Optional[str]]
    ip_address: Mapped[str]
    country: Mapped[Optional[str]]
    country_code: Mapped[Optional[str]]
    user_agent: Mapped[str]
    campaign_id: Mapped[str]
    campaign_item: Mapped[str]
    miner_hotkey: Mapped[str]
    miner_block: Mapped[int]
    at: Mapped[bool]
    device: Mapped[Optional[Device]] = mapped_column(Enum(Device))
    is_unique: Mapped[bool]
    return_in_site: Mapped[bool]
    status: Mapped[VisitStatus] = mapped_column(
        Enum(VisitStatus), default=VisitStatus.new
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    __mapper_args__ = {
        "confirm_deleted_rows": False
    }


class VisitorActivity(Base):
    """
    SQLAlchemy ORM class representing visitor activity entities.

    Attributes:
        ip (str): Primary key representing the IP address of the visitor.
        created_at (date): Date when the visitor activity record was created, defaults to current date.
        count (int): Count of activities associated with the visitor on the given date.
    """

    __tablename__ = "visitor_activity"

    ip: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[date] = mapped_column(
        Date, primary_key=True, default=datetime.utcnow().date
    )
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __mapper_args__ = {
        "confirm_deleted_rows": False
    }


class UserAgent(Base):
    """
    SQLAlchemy ORM class representing user-agent activity entities.

    Attributes:
        user_agent (str): Primary key representing the user-agent string.
        created_at (date): Date when the user-agent activity record was created, defaults to current date.
        count (int): Count of activities associated with the user-agent on the given date.
    """

    __tablename__ = "user_agent_activity"

    user_agent: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[date] = mapped_column(
        Date, primary_key=True, default=datetime.utcnow().date
    )
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
