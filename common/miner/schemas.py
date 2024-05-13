import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class VisitorSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    referrer: str
    ip_address: str
    miner_assigned: str
    target_landing_page: str
    user_agent: str
    country: Optional[str] = Field(None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    additional_headers: Dict[str, Any] = Field({})

    class Config:
        orm_mode = True
