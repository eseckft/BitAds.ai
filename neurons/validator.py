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

# import base validator class which takes care of most of the boilerplate
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
        return need_ping

    async def process(self):
        global timeout_process
        global data_campaigns
        global data_aggregations
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
                data_campaigns = response['campaign']
                data_aggregations = response['aggregation']

                if len(data_campaigns) > 0:
                    Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_BITADS, Hint.LOG_TEXTS[8] + str(len(data_campaigns)), 1)
                if len(data_aggregations) > 0:
                    Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_BITADS, Hint.LOG_TEXTS[9] + str(len(data_aggregations)), 1)

        return need_process_campaign

    async def process_campaign(self):
        global data_campaigns

        for campaign in data_campaigns:
            Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_BITADS, Hint.LOG_TEXTS[6], 1)

            file.saveCampaign(Main.wallet_hotkey, File.TYPE_VALIDATOR, campaign)

            Hint.print_campaign_info(campaign)

            for uid in range(self.metagraph.n.item()):
                if uid == self.uid:
                    continue
                axon = self.metagraph.axons[uid]

                if self.block - self.metagraph.last_update[uid] < self.config.neuron.epoch_length:  # active
                    thread = threading.Thread(target=self.sendMessage, args=(axon, campaign))
                    thread.start()
                else:
                    Hint(Hint.COLOR_YELLOW, Const.LOG_TYPE_MINER, "Miner: " + axon.hotkey + " is not active")

            data_campaigns.pop(0)
            time.sleep(2)
            break

    def sendMessage(self, axon, campaign):
        Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_MINER, "Miner: " + axon.hotkey + " is active")
        miner_has_unique_url = file.unique_link_exists(Main.wallet_hotkey, axon.hotkey, File.TYPE_VALIDATOR,
                                                       campaign['product_unique_id'])
        if miner_has_unique_url is False:
            Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_MINER,
                "Miner: " + axon.hotkey + ". I send the task to the miner.", False)

            response_from_miner = self.dendrite.query(
                axons=[axon],
                synapse=Task(dummy_input=campaign),
                deserialize=False,
                timeout=60
            )

            has_unique_link = False

            for res in response_from_miner:
                if res.dummy_output is not None:
                    has_unique_link = True
                    Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_MINER, "Miner: " + axon.hotkey + ". " + Hint.LOG_TEXTS[10])
                    file.saveMinerUniqueUrl(Main.wallet_hotkey, axon.hotkey, File.TYPE_VALIDATOR, res.dummy_output)
            if has_unique_link is False:
                """
                """
                # Hint(Hint.COLOR_RED, Const.LOG_TYPE_MINER, "Miner: " + axon.hotkey + ". " + Hint.LOG_TEXTS[11])
        else:
            Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_MINER, "Miner: " + axon.hotkey + ". " + Hint.LOG_TEXTS[12])
            # response_from_miner = self.dendrite.query(
            #     axons=[axon],
            #     synapse=Task(dummy_input=[]),
            #     deserialize=False,
            #     timeout=60
            # )
            # print('response_from_miner', response_from_miner)

    async def process_aggregation(self):
        global data_aggregations
        for aggregation in data_aggregations:
            print('aggregation', aggregation)
            for uid in range(self.metagraph.n.item()):
                if uid == self.uid:
                    continue
                axon = self.metagraph.axons[uid]
                if axon.hotkey == aggregation['miner_wallet_address']:
                    file.saveMinerUniqueUrlStats(Main.wallet_hotkey, aggregation['product_item_unique_id'],
                                                 File.TYPE_VALIDATOR, aggregation)
                    u = aggregation['visits_unique']
                    c = (aggregation['count_through_rate_click'] / aggregation['visits']) * 100
                    d = aggregation['visits'] - aggregation['duration_more_than_3_seconds']
                    k = 20
                    q = 1 - (d / aggregation['visits'])
                    e = u + (k * u * c)
                    m = 10000
                    rating = 1
                    if (e / m) * q < 1:
                        rating = (e / m) * q

                    Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_BITADS, Hint.LOG_TEXTS[7], 1)

                    # Set the weights on chain via our subtensor connection.
                    self.subtensor.set_weights(
                        wallet=self.wallet,
                        netuid=self.config.netuid,
                        uids=[uid],
                        weights=[rating],
                        wait_for_finalization=True,
                        version_key=int(hashlib.sha256(aggregation['id'].encode()).hexdigest(), 16) % (2 ** 64),
                    )

                    Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_VALIDATOR,
                        "Miner " + aggregation['miner_wallet_address'] + " was rated " + str(rating) + ".")

                    save_data = {"U": u, "C": c, "D": d, "K": k, "Q": q, "E": e, "M": m, "Rating": rating}
                    file.saveMinerUniqueUrlScore(Main.wallet_hotkey, aggregation['product_unique_id'],
                                                 aggregation['product_item_unique_id'], File.TYPE_VALIDATOR, save_data)
                    break
            data_aggregations.pop(0)
            time.sleep(2)
            break

    async def forward(self):
        global stepSize
        self.sync()
        self.moving_averaged_scores = torch.zeros((self.metagraph.n)).to(self.device)

        await self.process_ping()
        await self.process()

        if self.step % stepSize == 0:
            if len(data_campaigns) > 0:
                await self.process_campaign()
            elif len(data_aggregations) > 0:
                await self.process_aggregation()
        # return await forward(self)
        time.sleep(1)


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        Hint(Hint.COLOR_BLUE, Const.LOG_TYPE_LOCAL, Hint.V[1])
        Hint(Hint.COLOR_YELLOW, Const.LOG_TYPE_LOCAL, Hint.V[1])
        while True:
            time.sleep(5)
