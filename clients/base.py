from abc import ABC, abstractmethod
from typing import Optional

import aiohttp

from schemas.bit_ads import (
    PingResponse,
    GetMinerUniqueIdResponse,
    TaskResponse,
)


class BaseHTTPClient(ABC):
    def __init__(self, base_url: str, **headers):
        self._base_url = base_url
        self._headers = headers

    async def _make_request(self, method: str, endpoint: str, **kwargs):
        async with aiohttp.ClientSession(
            self._base_url, headers=self._headers
        ) as session:
            async with session.request(method, endpoint, **kwargs) as response:
                yield response


class BitAdsClient(ABC):
    @abstractmethod
    async def subnet_ping(self) -> Optional[PingResponse]:
        pass

    @abstractmethod
    async def get_task(self) -> Optional[TaskResponse]:
        pass

    @abstractmethod
    async def get_miner_unique_id(self) -> Optional[GetMinerUniqueIdResponse]:
        pass


class VersionClient(ABC):
    @abstractmethod
    async def get_version(self):
        pass
