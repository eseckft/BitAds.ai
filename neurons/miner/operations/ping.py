from typing import Tuple

import bittensor as bt

from common.clients.bitads.base import BitAdsClient
from common.helpers.logging import LogLevel, green, red
from common.schemas.bitads import (
    GetMinerUniqueIdResponse,
    UniqueIdData,
    MinerUniqueLinkSchema,
)
from common.services.unique_link.base import MinerUniqueLinkService
from neurons.base.operations import BaseOperation
from neurons.protocol import Ping


class PingOperation(BaseOperation[Ping]):
    def __init__(
        self,
        metagraph: bt.metagraph,
        config: bt.config,
        bit_ads_client: BitAdsClient,
        unique_link_service: MinerUniqueLinkService,
        wallet: bt.wallet,
        **_,
    ):
        super().__init__(metagraph, config, **_)
        self.unique_link_service = unique_link_service
        self.bit_ads_client = bit_ads_client
        self.wallet = wallet
        self.cache = {}
        self.reload_cache = True

    async def forward(self, synapse: Ping) -> Ping:
        if self.reload_cache:
            assignments = await self.unique_link_service.get_unique_links_for_hotkey(
                self.wallet.get_hotkey().ss58_address
            )
            self.cache = {a.campaign_id: a for a in assignments}
        for campaign in synapse.active_campaigns:
            unique_link = self.cache.get(campaign.product_unique_id)
            if unique_link:
                synapse.submitted_tasks.append(
                    GetMinerUniqueIdResponse(
                        data=UniqueIdData(
                            link=unique_link.link, minerUniqueId=unique_link.id
                        )
                    )
                )
                bt.logging.info(
                    prefix=LogLevel.VALIDATOR,
                    msg=green(
                        f"Unique link for campaign ID: {campaign.product_unique_id} already generated. "
                        f"Sending it to the Validator: {synapse.dendrite.hotkey}",
                    ),
                )
            else:
                try:
                    response = await self._get_campaign_unique_id(
                        campaign.product_unique_id
                    )
                    if not response:
                        raise
                    synapse.submitted_tasks.append(response)
                    bt.logging.info(
                        prefix=LogLevel.BITADS,
                        msg=green(
                            f"Successfully created a unique link for campaign ID: {campaign.product_unique_id} "
                            f"and forwarded it to the Validator: {synapse.dendrite.hotkey}",
                        ),
                    )
                    self.reload_cache = True
                except Exception as e:
                    bt.logging.warning(
                        prefix=LogLevel.BITADS,
                        msg=red(
                            f"Error creating unique link for campaign ID: {campaign.product_unique_id}"
                        ),
                    )
        synapse.result = True
        return synapse

    async def blacklist(self, synapse: Ping) -> Tuple[bool, str]:
        return await super().blacklist(synapse)

    async def priority(self, synapse: Ping) -> float:
        return await super().priority(synapse)

    async def _get_campaign_unique_id(self, campaign_id: str):
        response = self.bit_ads_client.get_miner_unique_id(campaign_id)
        if not response:
            return

        await self.unique_link_service.add_unique_link(
            MinerUniqueLinkSchema(
                id=response.data.miner_unique_id,
                campaign_id=campaign_id,
                hotkey=self.wallet.get_hotkey().ss58_address,
                link=response.data.link,
            )
        )

        return response
