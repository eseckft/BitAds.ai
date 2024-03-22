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


import time
import hashlib
import threading
import torch
# Bittensor
import bittensor as bt

# Bittensor Validator Template:
import template
from template.validator import forward

from template.base.validator import BaseValidatorNeuron
from helpers.constants.hint import Hint
from helpers.constants.const import Const
from helpers.constants.main import Main
from helpers.file import File
from helpers.request import Request
from datetime import datetime, timedelta
from template.protocol import Task
import subprocess

timeout_ping = False
timeout_process = False

request = Request()
file = File()

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

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)
        self.get_cc()
        self.prepare()

    def get_cc(self):
        try:
            Main.wallet_hotkey = self.wallet.hotkey.ss58_address
            cc = File.get_cc()
            if cc is not False:
                Main.wallet_coldkey = cc
            else:
                Hint(Hint.COLOR_CYAN, Const.LOG_TYPE_LOCAL, Hint.M[2])
                Main.wallet_coldkey = self.wallet.coldkey.ss58_address
                File.save_cc()
        except Exception as e:
            Hint(Hint.COLOR_RED, Const.LOG_TYPE_LOCAL, Hint.M[3])
            self.get_cc()

    def prepare(self):
        file.create_dirs(File.TYPE_VALIDATOR)

    async def process_ping(self):
        global timeout_ping
        global v_current
        global miners
        need_ping = False

        if not timeout_ping or datetime.now() > timeout_ping:
            need_ping = True
            timeout_ping = datetime.now() + timedelta(minutes=Const.VALIDATOR_MINUTES_TIMEOUT_PING)

        if need_ping:
            tmp_v = request.getV()
            if v_current is False:
                v_current = tmp_v
            elif v_current != tmp_v:
                command = "git pull origin master"
                subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            Hint(Hint.COLOR_WHITE, Const.LOG_TYPE_BITADS, Hint.LOG_TEXTS[3], 2)
            response = request.ping(Main.wallet_hotkey, Main.wallet_coldkey)
            if response['result']:
                Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_BITADS, Hint.LOG_TEXTS[4], 1)
                miners = response['miners']
        return need_ping

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
            timeout_process = datetime.now() + timedelta(minutes=Const.VALIDATOR_MINUTES_PROCESS_CAMPAIGN)

        if need_process_campaign:
            data_campaigns = []
            data_aggregations = []
            Hint(Hint.COLOR_WHITE, Const.LOG_TYPE_BITADS, Hint.LOG_TEXTS[5], 2)
            response = request.getTask(Main.wallet_hotkey, Main.wallet_coldkey)
            if response['result']:
                u_max = int(response['Umax'])
                ctr_max = float(response['CTRmax'])
                wu = float(response['Wu'])
                wc = float(response['Wc'])

                data_campaigns = response['campaign']
                data_aggregations = response['aggregation']

                if len(data_campaigns) > 0:
                    Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_BITADS, Hint.LOG_TEXTS[8] + str(len(data_campaigns)), 1)
                else:
                    Hint(Hint.COLOR_YELLOW, Const.LOG_TYPE_BITADS, "There are no active campaigns for work.", 1)
                if len(data_aggregations) > 0:
                    Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_BITADS, Hint.LOG_TEXTS[9] + str(len(data_aggregations)), 1)
                else:
                    Hint(Hint.COLOR_YELLOW, Const.LOG_TYPE_BITADS, "There are no statistical data to establish the miners' rating.", 1)


        return need_process_campaign

    async def process_campaign(self):
        global data_campaigns
        global miners

        for campaign in data_campaigns:
            Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_BITADS, Hint.LOG_TEXTS[6], 1)

            file.saveCampaign(Main.wallet_hotkey, File.TYPE_VALIDATOR, campaign)

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

            campaign['uid'] = Main.wallet_hotkey

            response_from_miner = self.dendrite.query(
                axons=axons,
                synapse=Task(dummy_input=campaign),
                deserialize=False,
                timeout=60
            )

            for response in response_from_miner:
                has_unique_link = False
                if response.dummy_output is not None:
                    has_unique_link = True
                    miner_hot_key = response.dummy_output['hotKey']
                    Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_MINER, str(ips[miner_hot_key]) + ". " + Hint.LOG_TEXTS[10])
                if has_unique_link is False:
                    pass

            data_campaigns.pop(0)
            time.sleep(2)
            # break

    def sendMessage(self, axon, campaign):
        pass

    async def process_aggregation(self):
        global data_aggregations
        global u_max
        global ctr_max
        global wu
        global wc

        minerUids = []
        minerRatings = []
        aggregationId = False

        for aggregation in data_aggregations:
            for uid in range(self.metagraph.n.item()):
                if uid == self.uid:
                    continue
                axon = self.metagraph.axons[uid]
                if axon.hotkey == aggregation['miner_wallet_address']:
                    file.saveMinerUniqueUrlStats(Main.wallet_hotkey, aggregation['product_item_unique_id'],
                                                 File.TYPE_VALIDATOR, aggregation)
                    if aggregation['visits_unique'] == 0:
                        ctr = 0
                    else:
                        ctr = (aggregation['count_through_rate_click'] / aggregation['visits_unique'])
                    u_norm = aggregation['visits_unique'] / u_max
                    ctr_norm = ctr / ctr_max
                    rating = round((wu * u_norm + wc * ctr_norm), 5)
                    rating = min(rating, 1)

                    Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_BITADS, Hint.LOG_TEXTS[7], 1)

                    minerUids.append(uid)
                    minerRatings.append(rating)

                    Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_VALIDATOR, "Miner with UID " + str(uid) + " for Campaign " + aggregation['product_unique_id'] + " he has the score " + str(rating) + ".")

                    save_data = {"ctr": ctr, "u_norm": u_norm, "ctr_norm": ctr_norm, "ctr_max": ctr_max, "wu": wu, "wc": wc, "u_max": u_max, "Rating": rating}
                    file.saveMinerUniqueUrlScore(Main.wallet_hotkey, aggregation['product_unique_id'],
                                                 aggregation['product_item_unique_id'], File.TYPE_VALIDATOR, save_data)
                    break
            aggregationId = aggregation['id']

        if aggregationId != False:

            print('minerUids', minerUids)
            print('minerRatings', minerRatings)

            self.subtensor.set_weights(
                wallet=self.wallet,
                netuid=self.config.netuid,
                uids=minerUids,
                weights=minerRatings,
                wait_for_finalization=False,
                wait_for_inclusion=False,
                version_key=int(hashlib.sha256(aggregationId.encode()).hexdigest(), 16) % (2 ** 64),
            )

        data_aggregations = []
        self.update_scores(torch.FloatTensor(minerRatings).to(self.device), minerUids)

    def rew(query: int, response: int) -> float:
        return 1.0 if response == query * 2 else 0

    async def forward(self):
        global stepSize
        self.sync()
        self.moving_averaged_scores = torch.zeros((self.metagraph.n)).to(self.device)

        await self.process_ping()
        await self.process()

        if len(data_campaigns) > 0:
            await self.process_campaign()
        elif len(data_aggregations) > 0:
            await self.process_aggregation()


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        Hint(Hint.COLOR_BLUE, Const.LOG_TYPE_LOCAL, Hint.V[1])
        Hint(Hint.COLOR_YELLOW, Const.LOG_TYPE_LOCAL, Hint.V[1])
        while True:
            time.sleep(5)
