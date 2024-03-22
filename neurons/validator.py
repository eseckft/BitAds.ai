# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


import hashlib
import time
from datetime import datetime, timedelta
from typing import Callable, List, Optional

# Bittensor
import bittensor as bt
import torch

from clients.base import BitAdsClient, VersionClient
from helpers import dependencies
from helpers.constants.colors import green, yellow, colorize, Color
from helpers.constants.const import Const
from helpers.logging import logger, LogLevel, log_campaign_info
from schemas.bit_ads import (
    Score,
    Campaign,
    TaskResponse,
    GetMinerUniqueIdResponse,
    Aggregation,
)
from services.ping.base import PingService
from services.storage.base import BaseStorage
from template.base.validator import BaseValidatorNeuron
from template.protocol import Task


class Validator(BaseValidatorNeuron):
    neuron_type = "validator"  # for backward compatibility with "File"

    def __init__(
        self,
        bitads_client_factory: Callable[[bt.wallet], BitAdsClient],
        version_client_factory: Callable[[], VersionClient],
        ping_service_factory: Callable[
            [BitAdsClient, VersionClient, timedelta], PingService
        ],
        storage_factory: Callable[[str, bt.wallet], BaseStorage],
        config=None,
        miner_uids=None,
        miner_ratings=None,
        process_timeout=Const.VALIDATOR_MINUTES_PROCESS_CAMPAIGN,
    ):
        super().__init__(config)
        self._bitads_client = bitads_client_factory(self.wallet)
        self._ping_service = ping_service_factory(
            self._bitads_client,
            version_client_factory(),
            Const.VALIDATOR_MINUTES_TIMEOUT_PING,
        )
        self._storage = storage_factory(self.neuron_type, self.wallet)
        self._process_timeout = process_timeout
        self._aggregation_id = None
        self._timeout_process = None
        self._miner_uids = miner_uids or []
        self._miner_ratings = miner_ratings or []
        self._miners = set()

    async def process(self) -> Optional[TaskResponse]:
        need_process_campaign = False

        if not self._timeout_process or datetime.now() > self._timeout_process:
            need_process_campaign = True
            self._timeout_process = datetime.now() + self._process_timeout

        if not need_process_campaign:
            return

        logger.log(
            LogLevel.BITADS,
            "<-- I'm making a request to the server to get a campaign allocation task for miners.",
        )
        response = self._bitads_client.get_task()
        if not response or not response.result:
            return

        if response.campaign:
            logger.log(
                LogLevel.BITADS,
                green(
                    f"--> Received campaigns for distribution among miners: {len(response.campaign)}",
                ),
            )
        else:
            logger.log(
                LogLevel.BITADS,
                yellow("--> There are no active campaigns for work."),
            )

        if response.aggregation:
            logger.log(
                LogLevel.BITADS,
                green(
                    f"Received tasks for assessing miners: {len(response.aggregation)}",
                ),
            )
        else:
            logger.log(
                LogLevel.BITADS,
                yellow(
                    "--> There are no statistical data to establish the miners' rating.",
                ),
            )

        return response

    async def process_campaign(self, data_campaigns: List[Campaign]):
        for campaign in data_campaigns:
            logger.log(
                LogLevel.BITADS,
                green(
                    "--> Received a task to distribute the campaign to miners.",
                ),
            )

            self._storage.save_campaign(campaign)

            log_campaign_info(campaign)

            axons = []
            ips = {}

            for uid in range(self.metagraph.n.item()):
                if uid == self.uid:
                    continue

                axon = self.metagraph.axons[uid]
                ips[axon.hotkey] = f"{axon.ip}:{axon.port}"

                if axon.hotkey in self._miners:
                    axons.append(axon)

            campaign.uid = self.wallet.get_hotkey().ss58_address

            response_from_miner = self.dendrite.query(
                axons=axons,
                synapse=Task(dummy_input=campaign),
                deserialize=False,
                timeout=60,
            )

            for response in response_from_miner:
                if not response.dummy_output:
                    continue

                output: GetMinerUniqueIdResponse = response.dummy_output
                logger.log(
                    LogLevel.MINER,
                    green(
                        f"{ips[output.hot_key]}. The miner submitted his unique link to the campaign.",
                    ),
                )

            time.sleep(2)

    async def process_aggregation(
        self, data_aggregations: List[Aggregation], task: TaskResponse
    ):
        self._miner_uids = []
        self._miner_ratings = []
        self._aggregation_id = None

        for aggregation in data_aggregations:
            for uid in range(self.metagraph.n.item()):
                if uid == self.uid:
                    continue
                axon = self.metagraph.axons[uid]
                if axon.hotkey != aggregation.miner_wallet_address:
                    continue
                self._storage.save_miner_unique_url_stats(aggregation)
                if aggregation.visits_unique == 0:
                    ctr = 0.0
                else:
                    ctr = (
                        aggregation.count_through_rate_click
                        / aggregation.visits_unique
                    )
                u_norm = aggregation.visits_unique / task.u_max
                ctr_norm = ctr / task.ctr_max
                rating = round((task.u_max * u_norm + task.wc * ctr_norm), 5)
                rating = min(rating, 1)

                logger.log(
                    LogLevel.BITADS,
                    green(
                        "--> Received a task to evaluate the miner.",
                    ),
                )

                self._miner_uids.append(uid)
                self._miner_ratings.append(rating)

                logger.log(
                    LogLevel.VALIDATOR,
                    green(
                        f"Miner with UID {uid} for Campaign {aggregation.product_unique_id} has the score {rating}.",
                    ),
                )

                score = Score(
                    ctr=ctr,
                    u_norm=u_norm,
                    ctr_norm=ctr_norm,
                    ctr_max=task.ctr_max,
                    wu=task.wu,
                    wc=task.wc,
                    u_max=task.u_max,
                    rating=rating,
                )
                self._storage.save_miner_unique_url_score(
                    aggregation.product_unique_id,
                    aggregation.product_item_unique_id,
                    score,
                )
                break  # FIXME: creates miner ratings with one miner?

            # FIXME: We are process multiple aggregations, but settings weights only for last?
            self._aggregation_id = aggregation.id

        self.set_weights()

        self.update_scores(
            torch.FloatTensor(self._miner_ratings).to(self.device),
            self._miner_uids,
        )

    def set_weights(self):
        if not self._aggregation_id:
            return
        logger.log(LogLevel.BITADS, self._miner_uids)
        logger.log(LogLevel.BITADS, self._miner_ratings)
        self.subtensor.set_weights(
            wallet=self.wallet,
            netuid=self.config.netuid,
            uids=self._miner_uids,
            weights=self._miner_ratings,
            wait_for_finalization=False,
            wait_for_inclusion=False,
            version_key=int(
                hashlib.sha256(self._aggregation_id.encode()).hexdigest(),
                16,
            )
            % (2**64),
        )

    async def forward(self, synapse: bt.Synapse = None):
        self.moving_averaged_scores = torch.zeros(self.metagraph.n).to(
            self.device
        )

        ping_response = self._ping_service.process_ping()
        if ping_response and ping_response.miners:
            self._miners = ping_response.miners

        task_response = await self.process()

        if not task_response:
            return

        if task_response.campaign:
            await self.process_campaign(task_response.campaign)
        if task_response.aggregation:
            await self.process_aggregation(
                task_response.aggregation, task_response
            )


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator(
        dependencies.create_bitads_client,
        dependencies.create_version_client,
        dependencies.create_ping_service,
        dependencies.create_storage,
    ) as validator:
        for color in (Color.BLUE, Color.YELLOW):
            logger.log(
                LogLevel.LOCAL,
                colorize(
                    color,
                    f"{validator.neuron_type.title()} running...",
                ),
            )
        while True:
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                bt.logging.warning("Ending validator...")
                break
