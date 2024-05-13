from datetime import datetime
from typing import Dict, Any
from uuid import UUID

from sqlalchemy import Uuid, DateTime, PickleType
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class Visitor(Base):
    __tablename__ = "visitors"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    referrer: Mapped[str]
    ip_address: Mapped[str]
    country: Mapped[str] = mapped_column(nullable=True)
    miner_assigned: Mapped[str]
    target_landing_page: Mapped[str]
    user_agent: Mapped[str]
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    additional_headers: Mapped[Dict[str, Any]] = mapped_column(PickleType)
