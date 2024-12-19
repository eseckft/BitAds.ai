from typing import Optional

from pydantic import BaseModel


class PaginationInfo(BaseModel):
    total: int
    page_size: int
    page_number: int
    next_page_number: Optional[int] = None
