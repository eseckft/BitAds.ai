from abc import ABC, abstractmethod
from typing import List

from common.schemas.bitads import TwoFactorRequest, TwoFactorSchema


class TwoFactorService(ABC):
    @abstractmethod
    async def add_from_request(self, request: TwoFactorRequest):
        pass

    @abstractmethod
    async def get_last_codes(self, limit: int = 5) -> List[TwoFactorSchema]:
        pass
