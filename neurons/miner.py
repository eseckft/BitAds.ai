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
from clients.base import BitAdsClient
from helpers import dependencies
from helpers.constants import colorize, Color, Const
from helpers.constants.colors import green
from helpers.logging import logger, LogLevel
from services.storage.base import BaseStorage

# import base miner class which takes care of most of the boilerplate
from template.base.miner import BaseMinerNeuron
from template.protocol import Task, MinerStatus, SpeedTest


class Miner(BaseMinerNeuron):
    neuron_type = "miner"  # for backward compatibility with "File"

    def __init__(
        self,
        bitads_client_factory: typing.Callable[[bt.wallet], BitAdsClient],
        storage_factory: typing.Callable[[str, bt.wallet], BaseStorage],
        config=None,
    ):
        super().__init__(config)
        self.axon.attach(self.forward_status).attach(self.forward_speed)
        self.bitads_client = bitads_client_factory(self.wallet)
        self._storage = storage_factory(self.neuron_type, self.wallet)

    def should_set_weights(self) -> bool:
        """
        Cus' of our neuron_type is "miner" - not "MinerNeuron", BaseNeuron `should_set_weights` is not working
        """
        return False

    async def forward(self, synapse: Task) -> Task:
        """
        Processes the incoming 'Task' synapse by performing a predefined operation on the input data.
        Args:
            synapse (template.protocol.Task): The synapse object containing the 'dummy_input' data.

        Returns:
            template.protocol.Task: The synapse object with the 'dummy_output' field
        """
        task = synapse.dummy_input

        if not task:  # TODO: Not sure this is called
            logger.info(
                LogLevel.BITADS,
                green("Validator pinging"),
            )
            return synapse

        logger.info(
            LogLevel.VALIDATOR,
            green(
                f"Received a campaign task with ID: {task.product_unique_id} from Validator: {task.uid}",
            ),
        )

        if self._storage.unique_link_exists(
            task.product_unique_id,
        ):
            response = self._storage.get_unique_url(
                task.product_unique_id,
            )
            synapse.dummy_output = response
            logger.info(
                LogLevel.VALIDATOR,
                green(
                    f"Unique link for campaign ID: {task.product_unique_id} already generated. "
                    f"Sending it to the Validator: {task.uid}",
                ),
            )
        else:
            self._storage.save_campaign(task)
            synapse.dummy_output = self.get_campaign_unique_id(
                task.product_unique_id
            )
            logger.info(
                LogLevel.BITADS,
                green(
                    f"Successfully created a unique link for campaign ID: {task.product_unique_id} "
                    f"and forwarded it to the Validator: {task.product_unique_id}",
                ),
            )

        self._storage.remove_campaign(task.product_unique_id)

        return synapse

    @staticmethod
    async def forward_status(synapse: MinerStatus) -> MinerStatus:
        return synapse

    @staticmethod
    async def forward_speed(synapse: SpeedTest) -> SpeedTest:
        return synapse

    async def blacklist(self, synapse: Task) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored.

        Blacklist runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contructed via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.

        Args:
            synapse (template.protocol.Task): A synapse object constructed from the headers of the incoming request.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the synapse's hotkey is blacklisted,
                            and a string providing the reason for the decision.

        This function is a security measure to prevent resource wastage on undesired requests. It should be enhanced
        to include checks against the metagraph for entity registration, validator status, and sufficient stake
        before deserialization of synapse data to minimize processing overhead.

        Example blacklist logic:
        - Reject if the hotkey is not a registered entity within the metagraph.
        - Consider blacklisting entities that are not validators or have insufficient stake.

        In practice it would be wise to blacklist requests from entities that are not validators, or do not have
        enough stake. This can be checked via metagraph.S and metagraph.validator_permit. You can always attain
        the uid of the sender via a metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.

        Otherwise, allow the request to be processed further.
        """
        uid = self.metagraph.hotkeys.index(synapse.dendrite.hotkey)
        if (
            not self.config.blacklist.allow_non_registered
            and synapse.dendrite.hotkey not in self.metagraph.hotkeys
        ):
            # Ignore requests from un-registered entities.
            logger.trace(
                f"Blacklisting un-registered hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"

        if self.config.blacklist.force_validator_permit:
            # If the config is set to force validator permit, then we should only allow requests from validators.
            if not self.metagraph.validator_permit[uid]:
                logger.warning(
                    f"Blacklisting a request from non-validator hotkey {synapse.dendrite.hotkey}"
                )
                return True, "Non-validator hotkey"

        logger.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, "Hotkey recognized!"

    async def priority(self, synapse: Task) -> float:
        """
        The priority function determines the order in which requests are handled. More valuable or higher-priority
        requests are processed before others.

        This implementation assigns priority to incoming requests based on the calling entity's stake in the metagraph.

        Args:
            synapse (template.protocol.Task): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.

        Miners may recieve messages from multiple entities at once. This function determines which request should be
        processed first. Higher values indicate that the request should be processed first. Lower values indicate
        that the request should be processed later.

        Example priority logic:
        - A higher stake results in a higher priority value.
        """
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        prirority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        logger.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: ",
            prirority,
        )
        return prirority

    def get_campaign_unique_id(self, campaign_id):
        response = self.bitads_client.get_miner_unique_id(campaign_id)
        if not response:
            return

        response.product_unique_id = campaign_id
        response.hot_key = self.wallet.get_hotkey().ss58_address

        self._storage.save_miner_unique_url(response)

        return response

    def save_state(self):
        """Nothing to save"""


# This is the main function, which runs the miner.
if __name__ == "__main__":
    for color in (Color.BLUE, Color.YELLOW):
        logger.info(
            LogLevel.LOCAL,
            colorize(color, f"{Const.MINER} running..."),
        )
    with Miner(
        dependencies.create_bitads_client, dependencies.create_storage
    ) as miner:
        ping_service = dependencies.create_ping_service(
            miner.bitads_client,
            dependencies.create_version_client(),
            Const.MINER_MINUTES_TIMEOUT_PING,
        )
        while True:
            ping_service.process_ping()
            try:
                time.sleep(20)
            except KeyboardInterrupt:
                logger.warning("Ending miner...")
                break
