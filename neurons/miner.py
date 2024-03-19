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
from template.protocol import Task, MinerStatus, SpeedTest
from helpers.constants.hint import Hint
from helpers.constants.const import Const
from helpers.constants.main import Main
from helpers.file import File
from helpers.request import Request
from datetime import datetime, timedelta
import subprocess


class Miner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    async def forward(self, synapse: Task) -> Task:
        synapse.dummy_output = {}
        task = synapse.dummy_input

        if not task:
            Hint(Hint.COLOR_GREEN, Const.LOG_TYPE_BITADS, "Validator pinging")
            return synapse

        Hint(
            Hint.COLOR_GREEN,
            Const.LOG_TYPE_VALIDATOR,
            f"Received a campaign task with ID: {task['product_unique_id']} from Validator: {task['uid']}",
        )
        miner_has_unique_url = self._file.unique_link_exists(
            Main.wallet_hotkey,
            Main.wallet_hotkey,
            File.TYPE_MINER,
            task["product_unique_id"],
        )

        if miner_has_unique_url:
            response = self._file.get_unique_url(
                Main.wallet_hotkey,
                Main.wallet_hotkey,
                File.TYPE_MINER,
                task["product_unique_id"],
            )
            synapse.dummy_output = response
            Hint(
                Hint.COLOR_GREEN,
                Const.LOG_TYPE_VALIDATOR,
                "Unique link for campaign ID: "
                + task["product_unique_id"]
                + " already generated. Sending it to the Validator: "
                + task["uid"],
            )
        else:
            self._file.save_campaign(Main.wallet_hotkey, File.TYPE_MINER, task)
            synapse.dummy_output = self.get_campaign_unique_id(
                task["product_unique_id"]
            )
            Hint(
                Hint.COLOR_GREEN,
                Const.LOG_TYPE_BITADS,
                "Successfully created a unique link for campaign ID: "
                + task["product_unique_id"]
                + " and forwarded it to the Validator: "
                + task["uid"],
            )

        self._file.remove_campaign(
            Main.wallet_hotkey, File.TYPE_MINER, task["product_unique_id"]
        )

        return synapse

    async def forward_status(self, synapse: MinerStatus) -> MinerStatus:
        return synapse

    async def forward_speed(self, synapse: SpeedTest) -> SpeedTest:
        return synapse

    async def blacklist(self, synapse: Task) -> typing.Tuple[bool, str]:
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

    async def priority(self, synapse: Task) -> float:
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

    def get_campaign_unique_id(self, campaign_id):
        response = self._request.get_miner_unique_id(
            campaign_id, Main.wallet_hotkey, Main.wallet_coldkey
        )
        if response:
            response["product_unique_id"] = campaign_id
            response["hotKey"] = Main.wallet_hotkey
            self._file.save_miner_unique_url(
                Main.wallet_hotkey,
                Main.wallet_hotkey,
                File.TYPE_MINER,
                response,
            )

        return response


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with Miner() as miner:
        Hint(Hint.COLOR_BLUE, Const.LOG_TYPE_LOCAL, Hint.M[1])
        Hint(Hint.COLOR_YELLOW, Const.LOG_TYPE_LOCAL, Hint.M[1])
        while True:
            miner.process_ping()
            bt.logging.info("Miner running...", time.time())
            try:
                time.sleep(20)
            except KeyboardInterrupt:
                bt.logging.warning("Ending miner...")
                break
