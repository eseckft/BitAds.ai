from typing import Tuple

import bittensor as bt

from common.services.bitads.base import BitAdsService
from common.services.validator.base import ValidatorService
from neurons.base.operations import BaseOperation
from neurons.protocol import SyncTrackingData


class SyncTrackingDataOperation(BaseOperation[SyncTrackingData]):
    def __init__(
        self,
        metagraph: bt.metagraph,
        config: bt.config,
        validator_service: ValidatorService,
        bitads_service: BitAdsService,
        **_
    ):
        super().__init__(metagraph, config, **_)
        self.bitads_service = bitads_service
        self.validator_service = validator_service

    async def forward(self, synapse: SyncTrackingData) -> SyncTrackingData:
        data = await self.validator_service.get_tracking_data_after(
            synapse.offset, synapse.limit
        )
        synapse.tracking_data = data
        bitads_data = await self.bitads_service.get_data_by_ids({d.id for d in data})
        synapse.bitads_data = bitads_data
        return synapse

    async def blacklist(self, synapse: SyncTrackingData) -> Tuple[bool, str]:
        return await super().blacklist(synapse)

    async def priority(self, synapse: SyncTrackingData) -> float:
        return await super().priority(synapse)
