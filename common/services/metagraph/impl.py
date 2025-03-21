import asyncio
from datetime import timedelta
from typing import TypeVar, Any

import bittensor as bt

from common.environ import Environ
from common.helpers import const
from common.services.metagraph.base import MetagraphService
from common.utils import cache_result


class BittensorMetagraphService(MetagraphService):
    @cache_result(expiration=timedelta(minutes=5))  # 5 minutes cache
    async def _get_metagraph_info(self) -> bt.Metagraph | None:
        async with bt.AsyncSubtensor(Environ.SUBTENSOR_NETWORK) as subtensor:
            return await subtensor.metagraph(
                const.NETUIDS[Environ.SUBTENSOR_NETWORK]
            )

    async def get_axon_data(
        self, hotkey: str, ip_address: str = None, coldkey: str = None
    ) -> dict:
        metagraph_info = await self._get_metagraph_info()
        try:
            index = metagraph_info.hotkeys.index(hotkey)
        except ValueError:
            return dict(exists=False)
        else:
            axon = metagraph_info.axons[index]
            stake = metagraph_info.total_stake[index]
            ip_address_match = not ip_address or ip_address == axon.ip
            coldkey_match = not coldkey or coldkey == axon.coldkey
            if not ip_address_match or not coldkey_match:
                return dict(exists=False)

            return dict(exists=True, stake=float(stake))

    async def hotkey_to_uid(self) -> list[dict[str, Any]]:
        metagraph_info = await self._get_metagraph_info()
        return [
            dict(uid=i, hotkey=a)
            for i, a in enumerate(metagraph_info.hotkeys)
        ]


if __name__ == "__main__":
    service = BittensorMetagraphService()
    result = asyncio.run(
        service.get_axon_data(
            "5DvTpiniW9s3APmHRYn8FroUWyfnLtrsid5Mtn5EwMXHN2ed"
        )
    )
    print(result)
