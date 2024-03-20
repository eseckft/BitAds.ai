# The MIT License (MIT)
# Copyright © 2023 Yuma Rao

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

import copy
import subprocess
import typing
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import bittensor as bt

from helpers.constants import Main, Hint, Const
from helpers.file import File
from helpers.request import Request
from template import __spec_version__ as spec_version

# Sync calls set weights and also resyncs the metagraph.
from template.utils.config import check_config, add_args, config
from template.utils.misc import ttl_get_block


class BaseNeuron(ABC):
    _NEURON_TYPE = None

    """
    Base class for Bittensor miners. This class is abstract and should be inherited by a subclass. It contains the core logic for all neurons; validators and miners.

    In addition to creating a wallet, subtensor, and metagraph, this class also handles the synchronization of the network state via a basic checkpointing mechanism based on epoch length.
    """

    @classmethod
    def check_config(cls, config: "bt.Config"):
        check_config(cls, config)

    @classmethod
    def add_args(cls, parser):
        add_args(cls, parser)

    @classmethod
    def config(cls):
        return config(cls)

    subtensor: "bt.subtensor"
    wallet: "bt.wallet"
    metagraph: "bt.metagraph"
    spec_version: int = spec_version

    @property
    def block(self):
        return ttl_get_block(self)

    def __init__(
        self,
        # client_factory: typing.Callable[[typing.Dict[str, str]], Request],
        config=None,
        ping_timeout=None,
        current_version=None,
        timeout_ping=0,
    ):
        base_config = copy.deepcopy(config or BaseNeuron.config())
        self.config = self.config()
        self.config.merge(base_config)
        self.check_config(self.config)

        # Set up logging with the provided configuration and directory.
        bt.logging(config=self.config, logging_dir=self.config.full_path)

        # If a gpu is required, set the device to cuda:N (e.g. cuda:0)
        self.device = self.config.neuron.device

        # Log the configuration for reference.
        bt.logging.info(self.config)

        # Build Bittensor objects
        # These are core Bittensor classes to interact with the network.
        bt.logging.info("Setting up bittensor objects.")

        # The wallet holds the cryptographic key pairs for the miner.
        self.wallet = bt.wallet(config=self.config)
        bt.logging.info(f"Wallet: {self.wallet}")

        # The subtensor is our connection to the Bittensor blockchain.
        self.subtensor = bt.subtensor(config=self.config)
        bt.logging.info(f"Subtensor: {self.subtensor}")

        # The metagraph holds the state of the network, letting us know about other validators and miners.
        self.metagraph = self.subtensor.metagraph(self.config.netuid)
        bt.logging.info(f"Metagraph: {self.metagraph}")

        # Check if the miner is registered on the Bittensor network before proceeding further.
        self.check_registered()

        # Each miner gets a unique identity (UID) in the network for differentiation.
        self.uid = self.metagraph.hotkeys.index(
            self.wallet.hotkey.ss58_address
        )
        bt.logging.info(
            f"Running neuron on subnet: {self.config.netuid} with uid {self.uid} using network: {self.subtensor.chain_endpoint}"
        )
        self.step = 0

        self._get_cc()
        # FIXME: Dependency alarm!!!
        self._request = Request()
        self._file = File()
        self._ping_timeout = ping_timeout
        self._timeout_ping = timeout_ping
        self._current_version = current_version

    def _get_cc(self):
        try:
            Main.wallet_hotkey = self.wallet.hotkey.ss58_address
            cc = File.get_cc()
            if cc is not False:
                Main.wallet_coldkey = cc
            else:
                Hint(Hint.COLOR_CYAN, Const.LOG_TYPE_LOCAL, Hint.M[2])
                Main.wallet_coldkey = self.wallet.coldkey.ss58_address
                File.save_cc()
        except:
            Hint(Hint.COLOR_RED, Const.LOG_TYPE_LOCAL, Hint.M[3])
            self._get_cc()

    def _prepare(self):
        self._file.create_dirs(self._NEURON_TYPE)

    @abstractmethod
    async def forward(self, synapse: bt.Synapse) -> bt.Synapse:
        ...

    @abstractmethod
    def run(self):
        ...

    def sync(self):
        """
        Wrapper for synchronizing the state of the network for the given miner or validator.
        """
        # Ensure miner or validator hotkey is still registered on the network.
        self.check_registered()

        if self.should_sync_metagraph():
            self.resync_metagraph()

        # if self.should_set_weights():
        #     self.set_weights()

        # Always save state.
        # self.save_state()

    def check_registered(self):
        # --- Check for registration.
        if not self.subtensor.is_hotkey_registered(
            netuid=self.config.netuid,
            hotkey_ss58=self.wallet.hotkey.ss58_address,
        ):
            bt.logging.error(
                f"Wallet: {self.wallet} is not registered on netuid {self.config.netuid}."
                f" Please register the hotkey using `btcli subnets register` before trying again"
            )
            exit()

    def should_sync_metagraph(self):
        """
        Check if enough epoch blocks have elapsed since the last checkpoint to sync.
        """
        return (
            self.block - self.metagraph.last_update[self.uid]
        ) > self.config.neuron.epoch_length

    def should_set_weights(self) -> bool:
        # Don't set weights on initialization.
        if self.step == 0:
            return False

        # Check if enough epoch blocks have elapsed since the last epoch.
        if self.config.neuron.disable_set_weights:
            return False

        # Define appropriate logic for when set weights.
        return (
            self.block - self.metagraph.last_update[self.uid]
        ) > self.config.neuron.epoch_length

    def save_state(self):
        bt.logging.warning(
            "save_state() not implemented for this neuron. You can implement this function to save model checkpoints or other useful data."
        )

    def load_state(self):
        bt.logging.warning(
            "load_state() not implemented for this neuron. You can implement this function to load model checkpoints or other useful data."
        )

    def process_ping(self) -> typing.Tuple[bool, typing.Optional[typing.Dict]]:
        need_ping = False

        if not self._ping_timeout or datetime.now() > self._ping_timeout:
            need_ping = True
            self._ping_timeout = datetime.now() + timedelta(
                minutes=self._timeout_ping
            )

        if not need_ping:
            return need_ping, None

        tmp_v = self._request.getV()
        if not self._current_version:
            self._current_version = tmp_v
        elif self._current_version != tmp_v:
            command = "git pull origin main"
            subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        Hint(Hint.COLOR_WHITE, Const.LOG_TYPE_BITADS, Hint.LOG_TEXTS[3], 2)
        response = self._request.ping(Main.wallet_hotkey, Main.wallet_coldkey)
        if response["result"]:
            Hint(
                Hint.COLOR_GREEN,
                Const.LOG_TYPE_BITADS,
                Hint.LOG_TEXTS[4],
                1,
            )
            return need_ping, response
