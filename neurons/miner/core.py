# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2023 bittensor.com
import asyncio
import logging
import time
from datetime import timedelta, datetime
from typing import Type

import bittensor as bt
from common.helpers import const

from common import dependencies as common_dependencies, utils
from common.environ import Environ as CommonEnviron
from common.helpers.logging import log_startup, BittensorLoggingFilter
from common.miner import dependencies
from common.miner.environ import Environ
from common.validator.environ import Environ as ValidatorEnviron
from common.utils import execute_periodically
from neurons.base.operations import BaseOperation
from neurons.miner.operations.notify_order import NotifyOrderOperation
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
    def __init__(self, config=None):
        super(CoreMiner, self).__init__(config=config)
        self.loop = asyncio.get_event_loop()

        self.bit_ads_client = common_dependencies.create_bitads_client(
            self.wallet, self.config.bitads.url, self.neuron_type
        )

        self.validators = CommonEnviron.VALIDATORS
        self.miners = CommonEnviron.MINERS

        self.database_manager = common_dependencies.get_database_manager(
            self.neuron_type, self.subtensor.network
        )
        self.miner_service = dependencies.get_miner_service(self.database_manager)
        self.campaign_service = common_dependencies.get_campaign_service(
            self.database_manager
        )
        self.recent_activity_service = dependencies.get_recent_activity_service(
            self.database_manager
        )
        self.unique_link_service = common_dependencies.get_miner_unique_link_service(
            self.database_manager
        )
        self.order_history_service = common_dependencies.get_order_history_service(
            self.database_manager
        )
        self.migration_service = dependencies.get_migration_service(
            self.database_manager
        )

        if self.config.mock:
            self.dendrite = MockDendrite(wallet=self.wallet)
        else:
            self.dendrite = bt.dendrite(wallet=self.wallet)
        bt.logging.info(f"Dendrite: {self.dendrite}")

        operations = [
            PingOperation,
            RecentActivityOperation,
            SyncVisitsOperation,
            NotifyOrderOperation,
        ]

        for operation in map(self._create_operation, operations):
            self.axon.attach(operation.forward, operation.blacklist, operation.priority)

    def sync(self):
        try:
            super().sync()
            self.loop.run_until_complete(self._migrate_old_data())
            self.loop.run_until_complete(self._set_hotkey_and_block())
            self.loop.run_until_complete(self._ping_bitads())
            # self.loop.run_until_complete(self.__sync_visits())
            self.loop.run_until_complete(self._send_load_data())
            self.loop.run_until_complete(self._clear_recent_activity())
        except Exception as e:
            bt.logging.exception(f"Error during sync: {str(e)}")

    @execute_periodically(const.PING_PERIOD)
    async def _ping_bitads(self):
        try:
            bt.logging.info("Start ping BitAds")
            response = self.bit_ads_client.subnet_ping()
            if response and response.result:
                self.validators = response.validators
                self.miners = response.miners
                await self.campaign_service.set_campaigns(response.campaigns)
            bt.logging.info("End ping BitAds")
        except Exception as e:
            bt.logging.exception(f"Error in _ping_bitads: {str(e)}")

    @execute_periodically(Environ.CLEAR_RECENT_ACTIVITY_PERIOD)
    async def _clear_recent_activity(self):
        try:
            bt.logging.info("Start clear recent activity")
            await self.recent_activity_service.clear_old_recent_activity()
            bt.logging.info("End clear recent activity")
        except Exception as e:
            bt.logging.exception(f"Error in _clear_recent_activity: {str(e)}")

    @execute_periodically(const.MIGRATE_OLD_DATA_PERIOD)
    async def _migrate_old_data(self):
        try:
            created_at_from = datetime.utcnow() - timedelta(
                seconds=ValidatorEnviron.MR_DAYS.total_seconds() * 2
            )
            await self.migration_service.migrate(created_at_from)
        except Exception:
            bt.logging.exception("Error while data migration")

    async def __sync_visits(self, timeout: float = 11.0):
        try:
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
            visits = {
                visit for synapse in responses.values() for visit in synapse.visits
            }
            try:
                await self.miner_service.add_visits(visits)
            except Exception as e:
                bt.logging.exception(f"Unable to add visits: {str(e)}")
            bt.logging.info("End sync process")
        except Exception as e:
            bt.logging.exception(f"Error in __sync_visits: {str(e)}")

    @execute_periodically(timedelta(minutes=15))
    async def _send_load_data(self):
        try:
            bt.logging.info("Start send load data to BitAds")
            self.bit_ads_client.send_system_load(utils.get_load_average_json())
            bt.logging.info("End send load data to BitAds")
        except Exception as e:
            bt.logging.exception(f"Error in _send_load_data: {str(e)}")

    async def _set_hotkey_and_block(self):
        try:
            current_block = self.subtensor.get_current_block()
            hotkey = self.wallet.get_hotkey().ss58_address
            await self.miner_service.set_hotkey_and_block(hotkey, current_block)
        except Exception as e:
            bt.logging.exception(f"Error in _set_hotkey_and_block: {str(e)}")

    def save_state(self):
        """
        Nothing to save at this moment
        """

    def _create_operation(self, op_type: Type[BaseOperation]):
        return op_type(**self.__dict__)


if __name__ == "__main__":
    bt.logging.set_info()
    log_startup("Miner")
    logging.getLogger(bt.__name__).addFilter(BittensorLoggingFilter())
    with dependencies.get_core_miner() as miner:
        while True:
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                break
            except Exception as e:
                bt.logging.exception(f"Error in main loop: {str(e)}")
