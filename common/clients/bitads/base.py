"""
Client for interacting with BitAds services.

This class extends BaseHTTPClient to provide methods for making HTTP requests to BitAds
API endpoints and handling responses.

Attributes:
    _base_url (str): The base URL for BitAds API requests.
    _headers (dict): A dictionary of headers to include in BitAds API requests.

Methods:
    _make_request(
        method: str,
        endpoint: str,
        params: dict = None,
        json: dict = None,
        target_model: Optional[Type[BaseResponse]] = BaseResponse
    ) -> Optional[Response]:
        Makes an HTTP request to a BitAds API endpoint.

    subnet_ping() -> Optional[PingResponse]:
        Abstract method to ping a subnet in the BitAds network.

    get_miner_unique_id(campaign_id: str) -> Optional[GetMinerUniqueIdResponse]:
        Abstract method to retrieve a unique miner identifier for a given campaign ID.

    send_system_load(system_load: SystemLoad):
        Abstract method to send system load information to BitAds.

    send_user_activity(request: UserActivityRequest):
        Abstract method to send user activity information to BitAds.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Type, TypeVar

from common.clients.base import BaseHTTPClient
from common.helpers.logging import log_errors
from common.schemas.bitads import (
    PingResponse,
    BaseResponse,
    GetMinerUniqueIdResponse,
    SystemLoad,
    UserActivityRequest,
)

Response = TypeVar("Response", bound=BaseResponse)


class BitAdsClient(BaseHTTPClient, ABC):
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] = None,
        json: Dict[str, Any] = None,
        target_model: Optional[Type[BaseResponse]] = BaseResponse,
    ) -> Optional[Response]:
        """
        Make an HTTP request to a BitAds API endpoint.

        Args:
            method (str): The HTTP method to use (GET, POST, PUT, DELETE, etc.).
            endpoint (str): The endpoint path to append to the base URL.
            params (dict, optional): Query parameters for the request (default: None).
            json (dict, optional): JSON body for the request (default: None).
            target_model (Type[BaseResponse], optional): The model class to parse the response into
                (default: BaseResponse).

        Returns:
            Optional[Response]: The parsed response object, or None if there was an error.

        """
        response = super()._make_request(method, endpoint, params, json)
        if response and target_model:
            response = target_model.parse_raw(response)
            log_errors(response.errors)
        return response

    @abstractmethod
    def subnet_ping(self) -> Optional[PingResponse]:
        """
        Abstract method to ping a subnet in the BitAds network.

        Returns:
            Optional[PingResponse]: The response containing ping information, or None if there was an error.

        """

    @abstractmethod
    def get_miner_unique_id(
        self, campaign_id: str
    ) -> Optional[GetMinerUniqueIdResponse]:
        """
        Abstract method to retrieve a unique miner identifier for a given campaign ID.

        Args:
            campaign_id (str): The ID of the campaign.

        Returns:
            Optional[GetMinerUniqueIdResponse]: The response containing the unique miner ID,
                or None if there was an error.

        """

    @abstractmethod
    def send_system_load(self, system_load: SystemLoad):
        """
        Abstract method to send system load information to BitAds.

        Args:
            system_load (SystemLoad): The system load information to send.

        """

    @abstractmethod
    def send_user_activity(self, request: UserActivityRequest):
        """
        Abstract method to send user activity information to BitAds.

        Args:
            request (UserActivityRequest): The user activity information to send.

        """
