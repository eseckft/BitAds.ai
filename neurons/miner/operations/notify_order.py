import logging
from typing import Tuple

import bittensor as bt

from common.services.order_history.base import OrderHistoryService
from neurons.base.operations import BaseOperation
from neurons.protocol import NotifyOrder

logger = logging.getLogger(__name__)


class NotifyOrderOperation(BaseOperation[NotifyOrder]):
    def __init__(
        self,
        metagraph: bt.metagraph,
        config: bt.config,
        order_history_service: OrderHistoryService,
        wallet: bt.wallet,
        **_,
    ):
        super().__init__(metagraph, config, **_)
        self.order_history_service = order_history_service
        self.wallet = wallet

    async def forward(self, synapse: NotifyOrder) -> NotifyOrder:
        hotkey = self.wallet.get_hotkey().ss58_address
        for data in synapse.bitads_data:
            try:
                await self.order_history_service.add_to_history(data, hotkey)
            except Exception as ex:
                logger.error(f"Unable to add order to history: {ex}")
        synapse.result = True
        return synapse

    async def blacklist(self, synapse: NotifyOrder) -> Tuple[bool, str]:
        return await super().blacklist(synapse)

    async def priority(self, synapse: NotifyOrder) -> float:
        return await super().priority(synapse)
