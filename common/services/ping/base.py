from abc import ABC, abstractmethod
from typing import Optional

from common.schemas.bitads import PingResponse


class PingService(ABC):
    """Abstract base class for a Ping Service.

    This class defines the interface for a service that processes pings and
    returns a response.

    Methods:
        process_ping() -> Optional[PingResponse]:
            Processes a ping and returns a PingResponse if available.
    """

    @abstractmethod
    def process_ping(self) -> Optional[PingResponse]:
        """Processes a ping and returns a PingResponse if available.

        This method should be implemented by subclasses to handle the logic
        for processing a ping.

        Returns:
            Optional[PingResponse]: An instance of `PingResponse` containing
            the result of the ping, or `None` if no response is available.
        """
        pass
