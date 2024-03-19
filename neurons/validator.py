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

# Bittensor
import bittensor as bt
import torch

from helpers.constants.const import Const
from helpers.constants.hint import Hint
from helpers.constants.main import Main
from helpers.file import File
from template.base.validator import BaseValidatorNeuron
from template.protocol import Task

timeout_process = False

stepSize = 10

data_campaigns = []
data_aggregations = []

v_current = False
miners = []

u_max = False
ctr_max = False
wu = False
wc = False


class Validator(BaseValidatorNeuron):
    async def process_ping(self):
        global miners
        need_ping, response = super().process_ping()
        if response:
            miners = response["miners"]
        return need_ping, response

    async def process(self):
        global timeout_process
        global data_campaigns
        global data_aggregations
        global u_max
        global ctr_max
        global wu
        global wc
        need_process_campaign = False

        if not timeout_process or datetime.now() > timeout_process:
            need_process_campaign = True
            timeout_process = datetime.now() + timedelta(
                minutes=Const.VALIDATOR_MINUTES_PROCESS_CAMPAIGN
            )

        if need_process_campaign:
            data_campaigns = []
            data_aggregations = []
            Hint(Hint.COLOR_WHITE, Const.LOG_TYPE_BITADS, Hint.LOG_TEXTS[5], 2)
            response = self._request.get_task(Main.wallet_hotkey, Main.wallet_coldkey)
            if "result" in response:
                u_max = int(response["Umax"])
                ctr_max = float(response["CTRmax"])
                wu = float(response["Wu"])
                wc = float(response["Wc"])

                data_campaigns = response["campaign"]
                data_aggregations = response["aggregation"]

                if data_campaigns:
                    Hint(
                        Hint.COLOR_GREEN,
                        Const.LOG_TYPE_BITADS,
                        Hint.LOG_TEXTS[8] + str(len(data_campaigns)),
                        1,
                    )
                else:
                    Hint(
                        Hint.COLOR_YELLOW,
                        Const.LOG_TYPE_BITADS,
                        "There are no active campaigns for work.",
                        1,
                    )
                if data_aggregations:
                    Hint(
                        Hint.COLOR_GREEN,
                        Const.LOG_TYPE_BITADS,
                        Hint.LOG_TEXTS[9] + str(len(data_aggregations)),
                        1,
                    )
                else:
                    Hint(
                        Hint.COLOR_YELLOW,
                        Const.LOG_TYPE_BITADS,
                        "There are no statistical data to establish the miners' rating.",
                        1,
                    )

        return need_process_campaign

    async def process_campaign(self):
        global data_campaigns

        for campaign in data_campaigns:
            Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_BITADS, Hint.LOG_TEXTS[6], 1)

            self._file.save_campaign(Main.wallet_hotkey, File.TYPE_VALIDATOR, campaign)

            Hint.print_campaign_info(campaign)

            axons = []
            ips = {}

            for uid in range(self.metagraph.n.item()):
                if uid == self.uid:
                    continue

                axon = self.metagraph.axons[uid]
                ips[axon.hotkey] = f"{axon.ip}:{axon.port}"

                if axon.hotkey in miners:
                    axons.append(axon)

            campaign["uid"] = Main.wallet_hotkey

            response_from_miner = self.dendrite.query(
                axons=axons,
                synapse=Task(dummy_input=campaign),
                deserialize=False,
                timeout=60,
            )

            for response in response_from_miner:
                has_unique_link = False
                if response.dummy_output:
                    has_unique_link = True
                    miner_hot_key = response.dummy_output["hotKey"]
                    Hint(
                        Hint.COLOR_GREEN,
                        Const.LOG_TYPE_MINER,
                        str(ips[miner_hot_key]) + ". " + Hint.LOG_TEXTS[10],
                    )
                if not has_unique_link:
                    pass

            data_campaigns.pop(0)
            time.sleep(2)
            # break

    def send_message(self, axon, campaign):
        pass

    async def process_aggregation(self):
        global data_aggregations
        global u_max
        global ctr_max
        global wu
        global wc

        miner_uids = []
        miner_ratings = []
        aggregation_id = None

        for aggregation in data_aggregations:
            for uid in range(self.metagraph.n.item()):
                if uid == self.uid:
                    continue
                axon = self.metagraph.axons[uid]
                if axon.hotkey == aggregation["miner_wallet_address"]:
                    self._file.save_miner_unique_url_stats(
                        Main.wallet_hotkey,
                        aggregation["product_item_unique_id"],
                        File.TYPE_VALIDATOR,
                        aggregation,
                    )
                    if aggregation["visits_unique"] == 0:
                        ctr = 0
                    else:
                        ctr = (
                            aggregation["count_through_rate_click"]
                            / aggregation["visits_unique"]
                        )
                    u_norm = aggregation["visits_unique"] / u_max
                    ctr_norm = ctr / ctr_max
                    rating = round((wu * u_norm + wc * ctr_norm), 5)
                    rating = min(rating, 1)

                    Hint(
                        Hint.COLOR_GREEN,
                        Const.LOG_TYPE_BITADS,
                        Hint.LOG_TEXTS[7],
                        1,
                    )

                    miner_uids.append(uid)
                    miner_ratings.append(rating)

                    Hint(
                        Hint.COLOR_GREEN,
                        Const.LOG_TYPE_VALIDATOR,
                        f"Miner with UID {uid} for Campaign {aggregation['product_unique_id']} has the score {rating}."
                    )

                    save_data = {
                        "ctr": ctr,
                        "u_norm": u_norm,
                        "ctr_norm": ctr_norm,
                        "ctr_max": ctr_max,
                        "wu": wu,
                        "wc": wc,
                        "u_max": u_max,
                        "Rating": rating,
                    }
                    self._file.save_miner_unique_url_score(
                        Main.wallet_hotkey,
                        aggregation["product_unique_id"],
                        aggregation["product_item_unique_id"],
                        File.TYPE_VALIDATOR,
                        save_data,
                    )
                    break
            aggregation_id = aggregation["id"]

        if aggregation_id:
            print("minerUids", miner_uids)
            print("minerRatings", miner_ratings)

            self.subtensor.set_weights(
                wallet=self.wallet,
                netuid=self.config.netuid,
                uids=miner_uids,
                weights=miner_ratings,
                wait_for_finalization=False,
                wait_for_inclusion=False,
                version_key=int(hashlib.sha256(aggregation_id.encode()).hexdigest(), 16)
                % (2**64),
            )

        data_aggregations = []
        self.update_scores(torch.FloatTensor(miner_ratings).to(self.device), miner_uids)

    def rew(self, query: int, response: int) -> float:
        return 1.0 if response == query * 2 else 0

    async def forward(self, **kwargs):
        global stepSize
        self.sync()
        self.moving_averaged_scores = torch.zeros(self.metagraph.n).to(self.device)

        await self.process_ping()
        await self.process()

        if data_aggregations:
            await self.process_campaign()
        elif data_aggregations:
            await self.process_aggregation()


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        Hint(Hint.COLOR_BLUE, Const.LOG_TYPE_LOCAL, Hint.V[1])
        Hint(Hint.COLOR_YELLOW, Const.LOG_TYPE_LOCAL, Hint.V[1])
        while True:
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                bt.logging.warning("Ending validator...")
                break
