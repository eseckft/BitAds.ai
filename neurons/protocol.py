from typing import Optional

import bittensor as bt


class Ping(bt.Synapse):
    d: Optional[int] = None
