from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class MinerAssignmentModel(BaseModel):
    unique_id: str
    hotkey: str
    campaign_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SetMinerAssignmentsRequest(BaseModel):
    assignments: List[MinerAssignmentModel]
