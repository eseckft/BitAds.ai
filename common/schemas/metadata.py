from datetime import datetime
from typing import Optional, Self

from pydantic import BaseModel, ConfigDict


class MinersMetadataSchema(BaseModel):
    hotkey: str
    last_offset: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def default_instance(cls, hotkey: str) -> Self:
        return cls(hotkey=hotkey)
