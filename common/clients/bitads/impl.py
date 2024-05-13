"""
Synchronous client for interacting with BitAds services.

This class extends BitAdsClient to provide synchronous methods for making HTTP requests
to BitAds API endpoints and handling responses.

Methods:
    subnet_ping() -> Optional[PingResponse]:
        Sends a GET request to ping a subnet in the BitAds network.

    get_miner_unique_id(campaign_id: str) -> Optional[GetMinerUniqueIdResponse]:
        Sends a GET request to retrieve a unique miner identifier (url) for a given campaign ID.

    send_system_load(system_load: SystemLoad):
        Sends a POST request to send system load information to BitAds.

    send_user_activity(request: UserActivityRequest):
        Sends a POST request to send user activity information to BitAds.
"""

from typing import Optional

from common.clients.bitads.base import BitAdsClient
from common.schemas.bitads import (
    PingResponse,
    GetMinerUniqueIdResponse,
    SystemLoad,
    UserActivityRequest,
)


class SyncBitAdsClient(BitAdsClient):
    def subnet_ping(self) -> Optional[PingResponse]:
        """
        Sends a GET request to ping a subnet in the BitAds network.

        Returns:
            Optional[PingResponse]: The response containing ping information, or None if there was an error.

        """
        return self._make_request(
            "GET", "/api/ping", target_model=PingResponse
        )

    def get_miner_unique_id(
        self, campaign_id: str
    ) -> Optional[GetMinerUniqueIdResponse]:
        """
        Sends a GET request to retrieve a unique miner identifier (url) for a given campaign ID.

        Args:
            campaign_id (str): The ID of the campaign.

        Returns:
            Optional[GetMinerUniqueIdResponse]: The response containing the unique miner ID,
                or None if there was an error.

        """
        return self._make_request(
            "GET",
            f"/api/generate_miner_url?{campaign_id}",
            target_model=GetMinerUniqueIdResponse,
        )

    def send_system_load(self, system_load: SystemLoad):
        """
        Sends a POST request to send system load information to BitAds.

        Args:
            system_load (SystemLoad): The system load information to send.

        """
        return self._make_request(
            "POST",
            f"/api/send_server_load",
            json=system_load.model_dump(mode="json"),
            target_model=None,
        )

    def send_user_activity(self, request: UserActivityRequest):
        """
        Sends a POST request to send user activity information to BitAds.

        Args:
            request (UserActivityRequest): The user activity information to send.

        """
        return self._make_request(
            "POST",
            f"/api/send_user_ip_activity",
            json=request.model_dump(mode="json"),
            target_model=None,
        )
