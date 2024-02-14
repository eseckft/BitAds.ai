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
import typing
import bittensor as bt

# Bittensor Miner Template:
import template

# import base miner class which takes care of most of the boilerplate
from template.base.miner import BaseMinerNeuron
from template.protocol import Task
from helpers.constants.hint import Hint
from helpers.constants.const import Const
from helpers.constants.main import Main
from helpers.file import File
from helpers.request import Request
from datetime import datetime, timedelta
import subprocess

file = File()
request = Request()

timeout_ping = False

v_current = False

class Miner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(Miner, self).__init__(config=config)
        self.get_cc()
        self.prepare()
        # TODO(developer): Anything specific to your use case you can do here

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
        file.create_dirs(File.TYPE_MINER)

    async def forward(
        self, synapse: Task
    ) -> Task:
        synapse.dummy_output = {}

        task = synapse.dummy_input
        print('dummy_input', task)
        if task != False and len(task) != 0:
            Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_VALIDATOR, "I received a task of the campaign type")
            miner_has_unique_url = file.unique_link_exists(Main.wallet_hotkey,
                                                        Main.wallet_hotkey, File.TYPE_MINER,
                                                        task['product_unique_id'])

            if miner_has_unique_url:
                response = file.getUniqueUrl(Main.wallet_hotkey, Main.wallet_hotkey,
                                             File.TYPE_MINER, task['product_unique_id'])
                synapse.dummy_output = response
                Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_VALIDATOR, "I already have a link for campaign " + task[
                    'product_unique_id'] + " and I am sending it to the validator.")
            else:
                file.saveCampaign(Main.wallet_hotkey, File.TYPE_MINER, task)
                synapse.dummy_output = self.getCampaignUniqueId(task['product_unique_id'])
                Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_BITADS, "I created a new unique link for campaign " + task[
                    'product_unique_id'] + " and passed it to the validator.")

            file.removeCampaign(Main.wallet_hotkey, File.TYPE_MINER, task['product_unique_id'])
        else:
            Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_BITADS, "Validator pinging")

        return synapse

    async def blacklist(
        self, synapse: template.protocol.Dummy
    ) -> typing.Tuple[bool, str]:
        if synapse.dendrite.hotkey not in self.metagraph.hotkeys:
            # Ignore requests from unrecognized entities.
            bt.logging.trace(
                f"Blacklisting unrecognized hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, "Hotkey recognized!"

    async def priority(self, synapse: template.protocol.Dummy) -> float:
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        prirority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: ", prirority
        )
        return prirority

    def process_ping(self):
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

    def getCampaignUniqueId(self, campaign_id):
        response = request.getMinerUniqueId(campaign_id, Main.wallet_hotkey, Main.wallet_coldkey)
        if response is not False:
            response['product_unique_id'] = campaign_id
            response['hotKey'] = Main.wallet_hotkey
            file.saveMinerUniqueUrl(Main.wallet_hotkey, Main.wallet_hotkey, File.TYPE_MINER, response)

        return response


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with Miner() as miner:
        Hint(Hint.COLOR_BLUE, Const.LOG_TYPE_LOCAL, Hint.M[1])
        Hint(Hint.COLOR_YELLOW, Const.LOG_TYPE_LOCAL, Hint.M[1])
        while True:
            miner.process_ping()
            time.sleep(20)
            if miner.should_exit:
                bt.logging.warning("Ending miner...")
                break