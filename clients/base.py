from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, Union

import aiohttp
import requests

from helpers.logging import log_errors, log_error, logger
from schemas.bit_ads import (
    PingResponse,
    GetMinerUniqueIdResponse,
    TaskResponse,
)


class BaseHTTPClient(ABC):
    def __init__(self, base_url: str, **headers):
        self._base_url = base_url
        self._headers = headers

    def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        try:
            response = requests.request(
                method,
                self._base_url + endpoint,
                headers=self._headers,
                params=kwargs,
            )
            body = response.json()
            logger.debug(f"Response from {endpoint}: {body}")
            log_errors(body.get("errors"))
            response.raise_for_status()
            return body
        except Exception as ex:
            log_error(ex)


class BaseAsyncHTTPClient(ABC):
    def __init__(self, base_url: str, **headers):
        self._base_url = base_url
        self._headers = headers

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        async with aiohttp.ClientSession(
            self._base_url, headers=self._headers
        ) as session:
            async with session.request(method, endpoint, **kwargs) as response:
                try:
                    response.raise_for_status()
                    body = await response.json()
                    log_errors(body.get("errors"))
                    return body
                except Exception as ex:
                    log_error(ex)


class BitAdsClient(ABC):
    @abstractmethod
    def subnet_ping(self) -> Optional[PingResponse]:
        pass

    @abstractmethod
    def get_task(self) -> Optional[TaskResponse]:
        pass

    @abstractmethod
    def get_miner_unique_id(
        self, campaign_id: Union[str, int]
    ) -> Optional[GetMinerUniqueIdResponse]:
        pass


class AsyncBitAdsClient(ABC):
    @abstractmethod
    async def subnet_ping(self) -> Optional[PingResponse]:
        pass

    @abstractmethod
    async def get_task(self) -> Optional[TaskResponse]:
        pass

    @abstractmethod
    async def get_miner_unique_id(
        self, campaign_id: Union[str, int]
    ) -> Optional[GetMinerUniqueIdResponse]:
        pass


class VersionClient(ABC):
    @abstractmethod
    def get_version(self) -> str:
        pass


class AsyncVersionClient(ABC):
    @abstractmethod
    async def get_version(self):
        pass
