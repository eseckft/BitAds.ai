from abc import ABC, abstractmethod
from typing import Optional

from schemas.bit_ads import PingResponse


class PingService(ABC):
    @abstractmethod
    def process_ping(self) -> Optional[PingResponse]:
        pass
