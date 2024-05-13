from typing import Tuple

import bittensor as bt

from common.miner.db.unit_of_work.base import MinerActiveUnitOfWork
from common.services.recent_activity.base import RecentActivityService
from neurons.base.operations import BaseOperation
from neurons.protocol import RecentActivity


class RecentActivityOperation(BaseOperation[RecentActivity]):
    def __init__(
        self,
        metagraph: bt.metagraph,
        config: bt.config,
        recent_activity_service: RecentActivityService,
        **_
    ):
        super().__init__(metagraph, config, **_)
        self.recent_activity_service = recent_activity_service

    async def forward(self, synapse: RecentActivity) -> RecentActivity:
        synapse.activity = await self.recent_activity_service.get_recent_activity(
            synapse.count, synapse.limit
        )
        return synapse

    async def blacklist(self, synapse: RecentActivity) -> Tuple[bool, str]:
        return await super().blacklist(synapse)

    async def priority(self, synapse: RecentActivity) -> float:
        return await super().priority(synapse)
