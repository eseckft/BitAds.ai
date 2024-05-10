import uuid
from datetime import datetime
from typing import Optional, Any, Dict

from pydantic import BaseModel


class VisitorSchema(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    referrer: str
    ip_address: str
    miner_assigned: str
    target_landing_page: str
    user_agent: str
    country: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    additional_headers: Dict[str, Any] = {}

    class Config:
        orm_mode = True
