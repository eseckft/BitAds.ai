from typing import Tuple

import bittensor as bt

from common.services.miner.base import MinerService
from neurons.base.operations import BaseOperation
from neurons.protocol import SyncVisits


class SyncVisitsOperation(BaseOperation[SyncVisits]):
    def __init__(
        self,
        metagraph: bt.metagraph,
        config: bt.config,
        miner_service: MinerService,
        **_,
    ):
        super().__init__(metagraph, config, **_)
        self.miner_service = miner_service

    async def forward(self, synapse: SyncVisits) -> SyncVisits:
        bt.logging.debug(
            f"Received SyncVisits synapse. Params: {synapse} from dendrite: {synapse.dendrite.hotkey}"
        )
        visits = await self.miner_service.get_visits_after(
            synapse.offset, synapse.limit
        )
        bt.logging.debug(f"Forwarding visits with ids: {[v.id for v in visits]} to {synapse.dendrite.hotkey}")
        synapse.visits = visits
        return synapse

    async def blacklist(self, synapse: SyncVisits) -> Tuple[bool, str]:
        return await super().blacklist(synapse)

    async def priority(self, synapse: SyncVisits) -> float:
        return await super().priority(synapse)
