import uuid
from typing import List

from pydantic import BaseModel


class TrackingDataSchema(BaseModel):
    id: uuid.UUID  # id from header (provided by miner)
    visit_duration: int  # in seconds
    scrolling_percentage: int  # percentage scrolled
    clicks: int

    class Config:
        orm_mode = True
