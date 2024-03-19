from typing import Optional

from clients.base import BitAdsClient, BaseHTTPClient
from helpers import md5_utils
from helpers.constants import paths, Const
from schemas.bit_ads import (
    PingResponse,
    GetMinerUniqueIdResponse,
    TaskResponse,
)


class AsyncBitAdsClient(BitAdsClient, BaseHTTPClient):
    async def subnet_ping(self) -> Optional[PingResponse]:
        print(
            "request hash example: ",
            md5_utils.calculate_md5_for_files_in_folders(
                Const.FOLDERS_TO_CHECK
            ),
        )  # TODO: it is really needed?
        async with self._make_request(
            "GET", paths.BitAdsPaths.SUBNET_PING
        ) as response:
            body = await response.read()
            return PingResponse.parse_raw(body)

    async def get_task(self) -> Optional[TaskResponse]:
        pass

    async def get_miner_unique_id(self) -> Optional[GetMinerUniqueIdResponse]:
        pass
