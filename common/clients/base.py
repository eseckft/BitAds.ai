"""
Base class for creating HTTP clients.

This class provides a foundation for making HTTP requests to a specified base URL
with customizable headers.

Attributes:
    _base_url (str): The base URL for the HTTP requests.
    _headers (dict): A dictionary of headers to be included in the HTTP requests.

Methods:
    __init__(base_url: str, **headers):
        Initializes the BaseHTTPClient with a base URL and optional headers.

    _make_request(method: str, endpoint: str, params: dict = None, json: dict = None, **kwargs) -> bytes:
        Makes an HTTP request using the specified method to the given endpoint.

"""

from abc import ABC
from typing import Dict, Any

import requests

from common.helpers.logging import log_error


class BaseHTTPClient(ABC):
    def __init__(self, base_url: str, **headers):
        """
        Initialize the BaseHTTPClient.

        Args:
            base_url (str): The base URL for the HTTP requests.
            **headers: Optional headers to be included in the HTTP requests.
        """
        self._base_url = base_url
        self._headers = headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] = None,
        json: Dict[str, Any] = None,
        **kwargs
    ) -> bytes:
        """
        Make an HTTP request.

        Args:
            method (str): The HTTP method to use (GET, POST, PUT, DELETE, etc.).
            endpoint (str): The endpoint path to append to the base URL.
            params (dict, optional): Query parameters for the request (default: None).
            json (dict, optional): JSON body for the request (default: None).
            **kwargs: Additional keyword arguments to pass to the requests library.

        Returns:
            bytes: The content of the HTTP response.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request returns an error status code.
        """
        try:
            response = requests.request(
                method,
                self._base_url + endpoint,
                headers=self._headers,
                params=params,
                json=json,
                **kwargs
            )
            response.raise_for_status()
            return response.content
        except Exception as ex:
            log_error(ex)
