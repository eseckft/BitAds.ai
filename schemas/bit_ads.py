from typing import List, Any, Optional

import pydantic


class BaseResponse(pydantic.BaseModel):
    errors: Optional[List[str | Any]] = None


class PingResponse(BaseResponse):
    pass


class TaskResponse(BaseResponse):
    pass


class GetMinerUniqueIdResponse(BaseResponse):
    pass
