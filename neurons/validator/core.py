# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2023 bittensor.com
import argparse
import asyncio
import time
from datetime import timedelta, datetime

# Bittensor
import bittensor as bt

from common import dependencies as common_dependencies, utils
from common.environ import Environ as CommonEnviron
from common.helpers import const
from common.helpers.logging import LogLevel, log_startup
from common.schemas.bitads import FormulaParams, UserActivityRequest
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

        self.bitads_client = common_dependencies.create_bitads_client(
            self.wallet, self.config.bitads.url, self.neuron_type
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
        self.campaigns_serivce = common_dependencies.get_campaign_service(
            self.database_manager
        )
        self.miners = CommonEnviron.MINERS
        self.validators = CommonEnviron.VALIDATORS
        self.evaluate_miners_blocks = Environ.EVALUATE_MINERS_BLOCK_N
        self.miner_ratings = dict()
        self.last_evaluate_block = 0
        self.offset = None

        bt.logging.info("load_state()")
        self.load_state()

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
        try:
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
        except Exception as ex:
            bt.logging.exception(f"Recent activity forward exception: {str(ex)}")

    async def forward_ping(self):
        current_block = self.subtensor.get_current_block()
        if current_block % Environ.PING_MINERS_N != 0:
            bt.logging.debug(
                f"It's not time to ping miners yet. Current block: {current_block}"
            )
            return
        try:
            active_campaigns = await self.campaigns_serivce.get_active_campaigns()
            bt.logging.info(
                f"Start ping miners with active campaigns: {[c.id for c in active_campaigns]}"
            )
            responses = await forward_each_axon(
                self, Ping(active_campaigns=active_campaigns), *self.miners
            )
            await self.validator_service.add_miner_ping(
                current_block,
                {
                    t.data.miner_unique_id: (
                        hotkey,
                        r.active_campaigns[i].product_unique_id,
                    )
                    for hotkey, r in responses.items()
                    for i, t in enumerate(r.submitted_tasks)
                },
            )
            bt.logging.info("End ping miners")
        except Exception as ex:
            bt.logging.exception(f"Ping miners exception: {str(ex)}")

    async def _forward_bitads_data(self, delay: float = 12.0):
        while True:
            try:
                await self.__forward_bitads_data()
            except Exception as ex:
                bt.logging.exception(f"Failed to sync BitAds data: {str(ex)}")
            finally:
                await asyncio.sleep(delay)

    async def __forward_bitads_data(self, timeout: float = 6.0):
        try:
            bt.logging.info("Start sync BitAds process")
            offset = (
                datetime.fromisoformat("2024-11-01")
                if not self.offset
                else self.offset
            )
            bt.logging.debug(
                f"Sync visits with offset: {offset} with miners: {self.miners}"
            )

            responses = await forward_each_axon(
                self, SyncVisits(offset=offset), *self.miners, timeout=timeout
            )
            visits = {
                visits for synapse in responses.values() for visits in synapse.visits
            }
            if not visits:
                bt.logging.debug("No visits received from miners")
                return

            bt.logging.debug(
                f"Received visits from miners with ids: {[v.id for v in visits]}"
            )

            max_created_at_per_response = [
                max(v.created_at for v in synapse.visits)
                for synapse in responses.values()
                if synapse.visits
            ]
            if max_created_at_per_response:
                new_offset = min(max_created_at_per_response)
                self.offset = new_offset
                bt.logging.debug(f"Updated offset: {self.offset}")

            await self.bitads_service.add_by_visits(visits)

            for campaign in await self.campaigns_serivce.get_active_campaigns():
                sale_to = datetime.utcnow() - timedelta(
                    days=campaign.product_refund_period_duration
                )
                await self.bitads_service.update_sale_status_if_needed(
                    campaign.product_unique_id, sale_to
                )

            bt.logging.info("End sync BitAds process")
        except Exception as ex:
            bt.logging.exception(f"BitAds data sync exception: {str(ex)}")

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
            uid: self.miner_ratings.get(hotkey, 0.0)
            for hotkey, uid in hotkey_to_uid.items()
        }
        bt.logging.debug(f"UID to rating: {miner_ratings}")

        result, msg = self.subtensor.set_weights(
            wallet=self.wallet,
            netuid=self.config.netuid,
            uids=list(miner_ratings.keys()),
            weights=list(miner_ratings.values()),
            version_key=self.spec_version,
        )
        self.miner_ratings.clear()
        if result is True:
            bt.logging.info("set_weights on chain successfully!")
        else:
            bt.logging.error("set_weights failed", msg)

    @execute_periodically(const.PING_PERIOD)
    async def _ping_bitads(self):
        try:
            bt.logging.info("Start ping BitAds")
            response = self.bitads_client.subnet_ping()
            if not response or not response.result:
                return

            self.miners = response.miners
            self.validators = response.validators
            active_campaigns = response.campaigns or []
            settings = FormulaParams.from_settings(response.settings)
            self.validator_service.settings = settings
            self.evaluate_miners_blocks = settings.evaluate_miners_blocks
            current_block = self.subtensor.get_current_block()
            await self.validator_service.sync_active_campaigns(
                current_block, active_campaigns
            )
            await self.campaigns_serivce.set_campaigns(active_campaigns)
            bt.logging.info("End ping BitAds")
        except Exception as ex:
            bt.logging.exception(f"Ping BitAds exception: {str(ex)}")

    @execute_periodically(timedelta(minutes=15))
    async def _send_load_data(self):
        self.bitads_client.send_system_load(utils.get_load_average_json())

    async def _try_evaluate_miners(self):
        try:
            current_block = self.subtensor.get_current_block()
            if (current_block % self.evaluate_miners_blocks == 0) or (
                current_block - self.last_evaluate_block >= self.evaluate_miners_blocks
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
        except Exception as ex:
            bt.logging.exception(f"Evaluate miners exception: {str(ex)}")

    async def _try_process_order_queue(self):
        try:
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
        except Exception as ex:
            bt.logging.exception(f"Order queue processing exception: {str(ex)}")

    async def _mark_for_reprocess(self):
        ids = await self.order_queue_service.get_all_ids()
        await self.order_queue_service.update_queue_status(
            {id_: OrderQueueStatus.PENDING for id_ in ids}
        )

    def load_state(self):
        self.loop.run_until_complete(self._ping_bitads())


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    bt.logging.on()
    log_startup("Validator")
    with dependencies.get_core_validator() as validator:
        while True:
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                break
