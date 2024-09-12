# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2023 bittensor.com
import argparse
import asyncio
import time
from datetime import timedelta, datetime
from typing import List

# Bittensor
import bittensor as bt
import torch

from common.helpers import const

from common import dependencies as common_dependencies, utils
from common.environ import Environ as CommonEnviron
from common.helpers.logging import LogLevel, log_startup
from common.schemas.bitads import FormulaParams, UserActivityRequest, Campaign
from common.schemas.sales import OrderQueueStatus
from common.utils import execute_periodically
from common.validator import dependencies
from common.validator.environ import Environ

# Bittensor Validator Template:
from neurons.protocol import (
    Ping,
    RecentActivity,
    SyncVisits,
)

# import base validator class which takes care of most of the boilerplate
from template.base.validator import BaseValidatorNeuron
from template.utils.config import add_blacklist_args
from template.validator.forward import forward_each_axon
from template import __version__


class CoreValidator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        super().add_args(parser)
        add_blacklist_args(cls, parser)

    def __init__(self, config=None):
        super(CoreValidator, self).__init__(config=config)

        bt.logging.info("load_state()")
        self.load_state()

        self.bitads_client = common_dependencies.create_bitads_client(
            self.wallet, self.config.bitads.url
        )
        self.database_manager = common_dependencies.get_database_manager(
            self.neuron_type, self.subtensor.network
        )
        self.validator_service = dependencies.get_validator_service(
            self.database_manager
        )
        self.bitads_service = common_dependencies.get_bitads_service(
            self.database_manager
        )
        self.order_queue_service = dependencies.get_order_queue_service(
            self.database_manager
        )
        self.miners = CommonEnviron.MINERS
        self.validators = CommonEnviron.VALIDATORS
        self.evaluate_miners_blocks = Environ.EVALUATE_MINERS_BLOCK_N
        self.miner_ratings = dict()
        self.active_campaigns: List[Campaign] = list()
        self.last_evaluate_block = 0
        self.hotkey_to_version = {}
        # self.loop.run_until_complete(self._mark_for_reprocess())
        # self.loop.create_task(self._calculate_campaigns_umax())
        # self.loop.create_task(self._evaluate_miners())

    async def forward(self, _: bt.Synapse = None):
        """
        Validator forward pass. Consists of:
        - Generating the query
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """
        await self.forward_ping()
        await self.__forward_bitads_data()
        await self._try_process_order_queue()
        await self.forward_recent_activity()
        await self._try_evaluate_miners()

    @execute_periodically(timedelta(minutes=30))
    async def forward_recent_activity(self):
        responses = await forward_each_axon(self, RecentActivity(), *self.miners)
        activity = {
            hotkey: ra.activity for hotkey, ra in responses.items() if ra.activity
        }
        if not activity:
            bt.logging.info("No activity found by users in subnet")
            return
        self.bitads_client.send_user_activity(
            UserActivityRequest(user_activity=activity)
        )

    async def forward_ping(self):
        current_block = self.subtensor.get_current_block()
        if current_block % Environ.PING_MINERS_N != 0:
            # TODO: here may be optional improve.
            #  If we reach this line not every N blocks than do additional period check like last_ping_block
            bt.logging.debug(
                f"It's not time to ping miners yet. Current block: {current_block}"
            )
            return
        bt.logging.info(
            f"Start ping miners with active campaigns: {[c.id for c in self.active_campaigns]}"
        )
        responses = await forward_each_axon(
            self, Ping(active_campaigns=self.active_campaigns), *self.miners
        )
        self.hotkey_to_version = {
            hotkey: response.script_version for hotkey, response in responses.items()
        }
        await self.validator_service.add_miner_ping(
            current_block,
            {
                t.data.miner_unique_id: hotkey
                for hotkey, r in responses.items()
                for t in r.submitted_tasks
            },
        )
        bt.logging.info("End ping miners")

    async def _forward_bitads_data(self, delay: float = 12.0):
        while True:
            try:
                await self.__forward_bitads_data()
            except:
                bt.logging.exception("Failed to sync bitads data")
            finally:
                await asyncio.sleep(delay)

    async def __forward_bitads_data(self, timeout: float = 6.0):
        bt.logging.info("Start sync bitads process")
        offset = await self.bitads_service.get_last_update_bitads_data(
            self.wallet.get_hotkey().ss58_address
        )
        bt.logging.debug(
            f"Sync visits with offset: {offset} with miners: {self.miners}"
        )
        responses = await forward_each_axon(
            self,
            SyncVisits(offset=offset),
            *self.miners,
            timeout=timeout,
        )

        visits = {visits for synapse in responses.values() for visits in synapse.visits}

        if not visits:
            bt.logging.debug("No visits received from miners")
            return

        bt.logging.debug(
            f"Received visits from miners with ids: {[v.id for v in visits]}"
        )

        await self.bitads_service.add_by_visits(visits)
        if hasattr(self, "settings"):
            sale_to = datetime.utcnow() - timedelta(
                seconds=self.settings.cpa_blocks * const.BLOCK_DURATION.total_seconds()
            )
            await self.bitads_service.update_sale_status_if_needed(sale_to)
        else:
            bt.logging.info(
                "There is no settings now, but it's not a problem. "
                "We are update sale status when settings appears"
            )
        bt.logging.info("End sync bitads process")

    def sync(self):
        super().sync()
        if not getattr(self, "bitads_client", None):
            bt.logging.info(
                "We will skip synchronization this time since the client is not ready yet",
                LogLevel.LOCAL,
            )
            return
        self.loop.run_until_complete(self._ping_bitads())
        self.loop.run_until_complete(self._send_load_data())

    def should_set_weights(self) -> bool:
        return super().should_set_weights() and self.miner_ratings

    def set_weights(self):
        bt.logging.debug(f"Start setting weights: {self.miner_ratings}")
        hotkey_to_uid = {n.hotkey: n.uid for n in self.metagraph.neurons}

        miner_ratings = {
            uid: self.miner_ratings.get(hotkey, 0.0) * 1
            if __version__ == self.hotkey_to_version.get(hotkey)
            else 0
            for hotkey, uid in hotkey_to_uid.items()
        }

        bt.logging.debug(f"UID to rating: {miner_ratings}")

        result, msg = self.subtensor.set_weights(
            wallet=self.wallet,
            netuid=self.config.netuid,
            uids=list(miner_ratings.keys()),
            weights=list(miner_ratings.values()),
            wait_for_finalization=True,
            wait_for_inclusion=False,
            version_key=__spec_version__,
        )
        self.update_scores(
            torch.FloatTensor(list(miner_ratings.values())).to(self.device),
            list(miner_ratings.keys()),
        )
        self.miner_ratings.clear()
        if result is True:
            bt.logging.info("set_weights on chain successfully!")
        else:
            bt.logging.error("set_weights failed", msg)

    @execute_periodically(Environ.PING_PERIOD)
    async def _ping_bitads(self):
        bt.logging.info("Start ping BitAds")
        response = self.bitads_client.subnet_ping()
        if not response or not response.result:
            return

        self.miners = response.miners
        self.validators = response.validators
        self.active_campaigns = response.campaigns or []
        self.settings = FormulaParams.from_settings(response.settings)
        self.validator_service.settings = self.settings
        self.evaluate_miners_blocks = self.settings.evaluate_miners_blocks
        current_block = self.subtensor.get_current_block()
        await self.validator_service.sync_active_campaigns(
            current_block, self.active_campaigns
        )
        bt.logging.info("End ping BitAds")

    @execute_periodically(timedelta(minutes=15))
    async def _send_load_data(self):
        self.bitads_client.send_system_load(utils.get_load_average_json())

    async def _try_evaluate_miners(self):
        try:
            current_block = self.subtensor.get_current_block()
            if (current_block % self.evaluate_miners_blocks == 0) or (
                # self.last_evaluate_block and
                current_block - self.last_evaluate_block
                >= self.evaluate_miners_blocks
            ):
                self.last_evaluate_block = current_block
                from_block = current_block - Environ.CALCULATE_UMAX_BLOCKS
                bt.logging.info(
                    f"Start evaluate miners from "
                    f"block {from_block} to block {current_block}"
                )
                self.miner_ratings = await self.validator_service.calculate_ratings(
                    from_block, current_block
                )
                bt.logging.info("End evaluate miners")
        except ValueError as ex:
            bt.logging.warning(*ex.args)
        except:
            bt.logging.exception("Evaluate miners exception")

    async def _try_process_order_queue(self):
        data_to_process = await self.order_queue_service.get_data_to_process()
        if not data_to_process:
            bt.logging.info("No data to process in order queue")
            return
        current_block = self.subtensor.get_current_block()
        hotkey = self.wallet.get_hotkey().ss58_address
        result = await self.bitads_service.add_by_queue_items(
            current_block, hotkey, data_to_process
        )
        await self.order_queue_service.update_queue_status(result)

    async def _mark_for_reprocess(self):
        ids = await self.order_queue_service.get_all_ids()
        await self.order_queue_service.update_queue_status(
            {id_: OrderQueueStatus.PENDING for id_ in ids}
        )


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    bt.logging.set_debug()
    log_startup("Validator")
    with dependencies.get_core_validator() as validator:
        while True:
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                break
