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
from websocket import WebSocketConnectionClosedException

from clients.base import BitAdsClient, VersionClient
from helpers import dependencies
from helpers.constants.colors import green, colorize, Color
from helpers.constants.const import Const
from helpers.logging import LogLevel, log_campaign_info, log_task
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

    def process(self) -> Optional[TaskResponse]:
        need_process_campaign = False

        if not self._timeout_process or datetime.now() > self._timeout_process:
            need_process_campaign = True
            self._timeout_process = datetime.now() + self._process_timeout

        if not need_process_campaign:
            return

        bt.logging.info(
            prefix=LogLevel.BITADS,
            msg="<-- I'm making a request to the server to get a campaign allocation task for miners.",
        )
        response = self._bitads_client.get_task()

        if not response or not response.result:
            return

        log_task(response)

        return response

    def process_campaign(self, data_campaigns: List[Campaign]):
        for campaign in data_campaigns:
            bt.logging.info(
                prefix=LogLevel.BITADS,
                msg=green(
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
                bt.logging.info(
                    prefix=LogLevel.MINER,
                    msg=green(
                        f"{ips[output.hot_key]}. The miner submitted his unique link to the campaign.",
                    ),
                )

            time.sleep(2)

    def process_aggregation(
        self, data_aggregations: List[Aggregation], task: TaskResponse
    ):
        if task.new:
            # new
            self._miner_uids = {}
            self._miner_ratings = {}
            self._aggregation_id = None

            for uid in range(self.metagraph.n.item()):
                axon = self.metagraph.axons[uid]
                if axon.hotkey in self._miners:
                    self._miner_uids[uid] = uid
                    self._miner_ratings[uid] = 0.0

            campaign_count = len(task.new)

            for aggregation in task.new:
                for miner_wallet in task.new[aggregation]:
                    for uid in range(self.metagraph.n.item()):
                        if uid == self.uid:
                            continue
                        axon = self.metagraph.axons[uid]
                        if axon.hotkey != miner_wallet:
                         continue

                        if task.new[aggregation][miner_wallet]['visits_unique'] == 0:
                            ctr = 0.0
                        else:
                            ctr = (
                                    task.new[aggregation][miner_wallet]['count_through_rate_click']
                                    / task.new[aggregation][miner_wallet]['visits_unique']
                            )
                        if ctr > 0.2:
                            ctr = 0
                        u_norm = task.new[aggregation][miner_wallet]['visits_unique'] / task.new[aggregation][miner_wallet]['umax']
                        ctr_norm = ctr / task.ctr_max
                        rating = round((task.wu * u_norm + task.wc * ctr_norm), 5)
                        rating = min(rating, 1)

                        task.new[aggregation][miner_wallet]['rating'] = rating

                        if uid not in self._miner_ratings:
                            self._miner_ratings[uid] = 0

                        self._miner_ratings[uid] = self._miner_ratings[uid] + rating

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
                            aggregation,
                            miner_wallet,
                            score,
                        )

            for mnr in self._miner_ratings:
                bt.logging.info(
                    prefix=LogLevel.BITADS,
                    msg=green(
                        "--> Received a task to evaluate the miner.",
                    ),
                )
                self._miner_ratings[mnr] = round(min(self._miner_ratings[mnr] / campaign_count, 1), 5)

                bt.logging.info(
                    prefix=LogLevel.VALIDATOR,
                    msg=green(
                        f"Miner with UID {mnr} has the score {self._miner_ratings[mnr]}.",
                    ),
                )

            self._miner_uids = list(self._miner_uids.values())
            self._miner_ratings = list(self._miner_ratings.values())


            print('uids', self._miner_uids)
            print('score', self._miner_ratings)

            self.set_weights()

            self.update_scores(
                torch.FloatTensor(self._miner_ratings).to(self.device),
                self._miner_uids,
            )
        else:
            # old

            self._miner_uids = {}
            self._miner_ratings = {}
            self._aggregation_id = None

            for uid in range(self.metagraph.n.item()):
                axon = self.metagraph.axons[uid]
                if axon.hotkey in self._miners:
                    self._miner_uids[uid] = uid
                    self._miner_ratings[uid] = 0.0

            for aggregation in data_aggregations:
                self._aggregation_id = aggregation.id
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

                    bt.logging.info(
                        prefix=LogLevel.BITADS,
                        msg=green(
                            "--> Received a task to evaluate the miner.",
                        ),
                    )

                    # self._miner_uids.append(uid)
                    self._miner_ratings[uid] = rating

                    bt.logging.info(
                        prefix=LogLevel.VALIDATOR,
                        msg=green(
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
                    break

            self._miner_uids = list(self._miner_uids.values())
            self._miner_ratings = list(self._miner_ratings.values())

            self.set_weights()

            self.update_scores(
                torch.FloatTensor(self._miner_ratings).to(self.device),
                self._miner_uids,
            )

    def set_weights(self):
        if not self._aggregation_id or not self._miner_uids:
            bt.logging.warning(
                f"Nothing to set for weights. Current miner uids: {self._miner_uids}"
            )
            return
        bt.logging.info(prefix=LogLevel.BITADS, msg=self._miner_uids)
        bt.logging.info(prefix=LogLevel.BITADS, msg=self._miner_ratings)
        try:
            # Set the weights on chain via our subtensor connection.
            result, msg = self.subtensor.set_weights(
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
            if result is True:
                bt.logging.info("set_weights on chain successfully!")
            else:
                bt.logging.error("set_weights failed", msg)
        except WebSocketConnectionClosedException:
            bt.logging.warning(
                "The websocket connection is lost, we are restoring it..."
            )
            self.subtensor.connect_websocket()
        except Exception as ex:
            bt.logging.error(f"Set weights error: {ex}")

    def should_set_weights(self) -> bool:
        """
        Cus' of our neuron_type is "miner" - not "MinerNeuron", BaseNeuron `should_set_weights` is not working
        """
        return False

    async def forward(self, synapse: bt.Synapse = None):
        self.moving_averaged_scores = torch.zeros(self.metagraph.n).to(
            self.device
        )

    def process_ping(self):
        ping_response = self._ping_service.process_ping()
        if ping_response and ping_response.miners:
            self._miners = ping_response.miners

        task_response = self.process()
        if not task_response:
            return

        if task_response.campaign:
            self.process_campaign(task_response.campaign)
        if task_response.aggregation or task_response.new:
            self.process_aggregation(task_response.aggregation, task_response)


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    for color in (Color.BLUE, Color.YELLOW):
        bt.logging.info(
            prefix=LogLevel.LOCAL,
            msg=colorize(
                color,
                f"{Const.VALIDATOR} running...",
            ),
        )
    with Validator(
        dependencies.create_bitads_client,
        dependencies.create_version_client,
        dependencies.create_ping_service,
        dependencies.create_storage,
    ) as validator:
        while True:
            validator.process_ping()
            try:
                time.sleep(20)
            except KeyboardInterrupt:
                bt.logging.warning("Ending validator...")
                break
