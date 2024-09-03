# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2023 bittensor.com
import asyncio
import time
from datetime import timedelta
from typing import Type

import bittensor as bt

from common import dependencies as common_dependencies, utils
from common.environ import Environ as CommonEnviron
from common.helpers.logging import log_startup
from common.miner import dependencies
from common.miner.environ import Environ
from common.utils import execute_periodically
from neurons.base.operations import BaseOperation
from neurons.miner.operations.ping import PingOperation
from neurons.miner.operations.recent_activity import RecentActivityOperation
from neurons.miner.operations.sync_visits import SyncVisitsOperation
from neurons.protocol import SyncVisits

# import base miner class which takes care of most of the boilerplate
from template.base.miner import BaseMinerNeuron
from template.mock import MockDendrite
from template.validator.forward import forward_each_axon


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


# Bittensor Miner Template:


class CoreMiner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(CoreMiner, self).__init__(config=config)
        # Create asyncio event loop to manage async tasks.
        self.loop = asyncio.get_event_loop()

        self.loop.create_task(self._sync_visits())

        self.bit_ads_client = common_dependencies.create_bitads_client(
            self.wallet, self.config.bitads.url
        )
        self.storage = common_dependencies.get_storage(self.neuron_type, self.wallet)

        self.validators = CommonEnviron.VALIDATORS
        self.miners = CommonEnviron.MINERS

        self.database_manager = common_dependencies.get_database_manager(
            self.neuron_type, self.subtensor.network
        )
        self.miner_service = dependencies.get_miner_service(self.database_manager)
        self.recent_activity_service = dependencies.get_recent_activity_service(
            self.database_manager
        )

        # Dendrite lets us send messages to other nodes (axons) in the network.
        if self.config.mock:
            self.dendrite = MockDendrite(wallet=self.wallet)
        else:
            self.dendrite = bt.dendrite(wallet=self.wallet)
        bt.logging.info(f"Dendrite: {self.dendrite}")

        operations = [
            PingOperation,
            RecentActivityOperation,
            SyncVisitsOperation,
        ]

        for operation in map(self._create_operation, operations):
            self.axon.attach(operation.forward, operation.blacklist, operation.priority)

    def sync(self):
        super().sync()
        self.loop.run_until_complete(self._send_load_data())
        self.loop.run_until_complete(self._ping_bitads())
        self.loop.run_until_complete(self._clear_recent_activity())

    @execute_periodically(Environ.PING_PERIOD)
    async def _ping_bitads(self):
        bt.logging.info("Start ping BitAds")
        response = self.bit_ads_client.subnet_ping()
        if response and response.result:
            self.validators = response.validators
            self.miners = response.miners
        bt.logging.info("End ping BitAds")

    @execute_periodically(Environ.CLEAR_RECENT_ACTIVITY_PERIOD)
    async def _clear_recent_activity(self):
        bt.logging.info("Start clear recent activity")
        await self.recent_activity_service.clear_old_recent_activity()
        bt.logging.info("End clear recent activity")

    async def _sync_visits(self, delay: float = 12.0):
        while True:
            try:
                await self.__sync_visits()
            except:
                bt.logging.exception("Sync error")
            finally:
                await asyncio.sleep(delay)

    async def __sync_visits(self, timeout: float = 11.0):
        bt.logging.info("Start sync process")
        offset = await self.miner_service.get_last_update_visit(
            self.wallet.get_hotkey().ss58_address
        )
        bt.logging.debug(f"Sync visits with offset: {offset}")
        bt.logging.debug(f"Sync visits with miners: {self.miners}")
        responses = await forward_each_axon(
            self,
            SyncVisits(offset=offset),
            *self.miners,
            timeout=timeout,
        )
        bt.logging.debug(f"Sync visits responses: {responses}")
        visits = {visit for synapse in responses.values() for visit in synapse.visits}
        await self.miner_service.add_visits(visits)
        bt.logging.info("End sync process")

    @execute_periodically(timedelta(minutes=15))
    async def _send_load_data(self):
        bt.logging.info("Start send load data to BitAds")
        self.bit_ads_client.send_system_load(utils.get_load_average_json())
        bt.logging.info("End send load data to BitAds")

    def save_state(self):
        """
        Nothing to save at this moment
        """

    def _create_operation(self, op_type: Type[BaseOperation]):
        return op_type(**self.__dict__)


# This is the main function, which runs the miner.
if __name__ == "__main__":
    bt.logging.set_trace()
    log_startup("Miner")
    with dependencies.get_core_miner() as miner:
        while True:
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                break
