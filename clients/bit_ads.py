from typing import Optional, Union

from clients.base import (
    AsyncBitAdsClient,
    BaseAsyncHTTPClient,
    BitAdsClient,
    BaseHTTPClient,
)
from helpers import md5_utils
from helpers.constants import paths, Const
from schemas.bit_ads import (
    PingResponse,
    GetMinerUniqueIdResponse,
    TaskResponse,
)


class AsyncAsyncBitAdsClientAsync(AsyncBitAdsClient, BaseAsyncHTTPClient):
    async def subnet_ping(self) -> Optional[PingResponse]:
        print(
            "request hash example: ",
            md5_utils.calculate_md5_for_files_in_folders(
                Const.FOLDERS_TO_CHECK
            ),
        )
        async with self._make_request(
            "GET", paths.BitAdsPaths.SUBNET_PING
        ) as response:
            body = await response.read()
            return PingResponse.parse_raw(body)

    async def get_task(self) -> Optional[TaskResponse]:
        pass

    async def get_miner_unique_id(
        self, campaign_id: Union[str, int]
    ) -> Optional[GetMinerUniqueIdResponse]:
        pass


class SyncBitAdsClient(BitAdsClient, BaseHTTPClient):
    def subnet_ping(self) -> Optional[PingResponse]:
        body = self._make_request("GET", paths.BitAdsPaths.SUBNET_PING)
        return PingResponse.parse_obj(body) if body else None

    def get_task(self) -> Optional[TaskResponse]:
        body = self._make_request("GET", paths.BitAdsPaths.GET_TASK)
        return TaskResponse.parse_obj(body) if body else None

    def get_miner_unique_id(
        self, campaign_id: Union[str, int]
    ) -> Optional[GetMinerUniqueIdResponse]:
        body = self._make_request(
            "GET",
            paths.BitAdsPaths.GENERATE_MINER_CAMPAIGN_URL.format(
                id=campaign_id
            ),
        )
        return GetMinerUniqueIdResponse.parse_obj(body) if body else None
