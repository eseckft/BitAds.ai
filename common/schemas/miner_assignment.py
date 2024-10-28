from typing import List

from pydantic import BaseModel, ConfigDict


class MinerAssignmentModel(BaseModel):
    unique_id: str
    hotkey: str

    model_config = ConfigDict(from_attributes=True)


class SetMinerAssignmentsRequest(BaseModel):
    assignments: List[MinerAssignmentModel]
