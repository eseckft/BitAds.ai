from datetime import timedelta, datetime
from typing import Optional

import bittensor as bt

from common.clients.bitads.base import BitAdsClient
from common.helpers.logging import LogLevel, green
from common.schemas.bitads import PingResponse
from common.services.ping.base import PingService


class SyncPingService(PingService):
    """Synchronous implementation of the PingService using BitAds client.

    This class provides a concrete implementation of the PingService
    abstract base class, handling the ping process with a BitAds client.

    Attributes:
        _bitads_client (BitAdsClient): Client for interacting with the BitAds service.
        _timeout_ping (timedelta): Time duration between consecutive pings.
        _ping_timeout (Optional[datetime]): The next time a ping is allowed.
        _current_version (Optional[str]): The current version of the service.
    """

    def __init__(
        self,
        bitads_client: BitAdsClient,
        timeout_ping: timedelta,
    ):
        """Initializes the SyncPingService with the BitAds client and ping timeout.

        Args:
            bitads_client (BitAdsClient): Client for interacting with the BitAds service.
            timeout_ping (timedelta): Time duration between consecutive pings.
        """
        self._bitads_client = bitads_client
        self._timeout_ping = timeout_ping
        self._ping_timeout = None
        self._current_version = None

    def process_ping(self) -> Optional[PingResponse]:
        """Processes a ping and returns a PingResponse if available.

        This method initiates a ping to the BitAds service if the timeout
        duration has passed since the last ping. It updates the ping timeout
        and logs the ping activity.

        Returns:
            Optional[PingResponse]: An instance of `PingResponse` containing
            the result of the ping, or `None` if no ping was needed.
        """
        need_ping = False

        if not self._ping_timeout or datetime.now() > self._ping_timeout:
            need_ping = True
            self._ping_timeout = datetime.now() + self._timeout_ping

        if not need_ping:
            return None

        bt.logging.info(
            prefix=LogLevel.BITADS,
            msg="Initiating ping to the server to update the activity timestamp.",
        )
        response = self._bitads_client.subnet_ping()
        if not response.result:
            return None

        bt.logging.info(
            prefix=LogLevel.BITADS,
            msg=green("--> Ping successful. Activity timestamp updated."),
        )
        return response
