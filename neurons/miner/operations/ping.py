from typing import Tuple

from neurons.miner.operations.base import BaseOperation
from neurons.protocol import Ping


class PingOperation(BaseOperation[Ping]):
    async def forward(self, synapse: Ping) -> Ping:
        synapse.d = 1
        return synapse

    async def blacklist(self, synapse: Ping) -> Tuple[bool, str]:
        return await super().blacklist(synapse)

    async def priority(self, synapse: Ping) -> float:
        return await super().priority(synapse)
