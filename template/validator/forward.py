# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2023 bittensor.com
import asyncio
import random
import time
from typing import TypeVar, Dict, List

import bittensor as bt

from template.protocol import Dummy
from template.utils import uids
from template.utils.uids import get_random_uids
from template.validator.reward import get_rewards

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


SYNAPSE = TypeVar("SYNAPSE", bound=bt.Synapse)


async def forward(self):
    """
    The forward function is called by the validator every time step.

    It is responsible for querying the network and scoring the responses.

    Args:
        self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

    """
    # get_random_uids is an example method, but you can replace it with your own.
    miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)

    # The dendrite client queries the network.
    responses = await self.dendrite(
        # Send the query to selected miner axons in the network.
        axons=[self.metagraph.axons[uid] for uid in miner_uids],
        # Construct a dummy query. This simply contains a single integer.
        synapse=Dummy(dummy_input=self.step),
        # All responses have the deserialize function called on them before returning.
        # You are encouraged to define your own deserialization function.
        deserialize=True,
    )

    # Log the results for monitoring purposes.
    bt.logging.info(f"Received responses: {responses}")

    # Adjust the scores based on responses from miners.
    rewards = get_rewards(self, query=self.step, responses=responses)

    bt.logging.info(f"Scored responses: {rewards}")
    # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
    self.update_scores(rewards, miner_uids)


async def forward_each_axon(
    self, synapse: SYNAPSE, *hotkeys, timeout: float = 12
) -> Dict[str, SYNAPSE]:
    # Helper function to log elapsed time
    def log_elapsed_time(start_time, step_name):
        elapsed_time = time.time() - start_time
        bt.logging.debug(f"[{step_name}] Elapsed time: {elapsed_time:.4f} seconds")

    # Start timing
    start_time = time.time()

    # Step 1: Get axons
    step_start_time = time.time()
    hotkeys = list(hotkeys)
    random.shuffle(hotkeys)
    axons = uids.get_axons(self, *hotkeys)
    log_elapsed_time(step_start_time, "Get axons")

    # Step 2: Forward axons
    step_start_time = time.time()
    responses: List[SYNAPSE] = await self.dendrite.forward(
        axons=axons, synapse=synapse, timeout=timeout
    )
    log_elapsed_time(step_start_time, "Forward axons")

    # Step 3: Build and return the result dictionary
    step_start_time = time.time()
    result = {r.axon.hotkey: r for r in responses}
    log_elapsed_time(step_start_time, "Build result dictionary")

    # Final elapsed time
    log_elapsed_time(start_time, "Total elapsed time")

    return result
