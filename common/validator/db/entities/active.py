import uuid

from sqlalchemy import Uuid
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class TrackingData(Base):
    __tablename__ = "tracking_data"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    visit_duration: Mapped[int]
    scrolling_percentage: Mapped[float]
    clicks: Mapped[int]
