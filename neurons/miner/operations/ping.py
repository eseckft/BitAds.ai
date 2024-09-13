from typing import Tuple

import bittensor as bt

from common.clients.bitads.base import BitAdsClient
from common.helpers.logging import LogLevel, green
from common.services.storage.base import BaseStorage
from neurons.base.operations import BaseOperation
from neurons.protocol import Ping


class PingOperation(BaseOperation[Ping]):
    def __init__(
        self,
        metagraph: bt.metagraph,
        config: bt.config,
        bit_ads_client: BitAdsClient,
        storage: BaseStorage,
        wallet: bt.wallet,
        **_,
    ):
        super().__init__(metagraph, config, **_)
        self.bit_ads_client = bit_ads_client
        self.storage = storage
        self.wallet = wallet

    async def forward(self, synapse: Ping) -> Ping:
        for campaign in synapse.active_campaigns:
            if self.storage.unique_link_exists(
                campaign.product_unique_id,
            ):
                response = self.storage.get_unique_url(
                    campaign.product_unique_id,
                )
                synapse.submitted_tasks.append(response)
                bt.logging.info(
                    prefix=LogLevel.VALIDATOR,
                    msg=green(
                        f"Unique link for campaign ID: {campaign.product_unique_id} already generated. "
                        f"Sending it to the Validator: {campaign.id}",
                    ),
                )
            else:
                self.storage.save_campaign(campaign)
                response = self._get_campaign_unique_id(
                    campaign.product_unique_id
                )
                if response:
                    synapse.submitted_tasks.append(response)
                    bt.logging.info(
                        prefix=LogLevel.BITADS,
                        msg=green(
                            f"Successfully created a unique link for campaign ID: {campaign.product_unique_id} "
                            f"and forwarded it to the Validator: {campaign.product_unique_id}",
                        ),
                    )

            self.storage.remove_campaign(campaign.product_unique_id)
        synapse.result = True
        return synapse

    async def blacklist(self, synapse: Ping) -> Tuple[bool, str]:
        return await super().blacklist(synapse)

    async def priority(self, synapse: Ping) -> float:
        return await super().priority(synapse)

    def _get_campaign_unique_id(self, campaign_id: str):
        response = self.bit_ads_client.get_miner_unique_id(campaign_id)
        if not response:
            return

        self.storage.save_miner_unique_url(campaign_id, response)

        return response
