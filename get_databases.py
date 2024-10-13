import asyncio
import os.path
import random
import socket
import ssl
from typing import Optional, Set
from urllib.error import URLError
from urllib.request import urlretrieve

import bittensor as bt
from common import dependencies

from common.environ import Environ as CommonEnviron
from common.helpers import const

bt.logging.on()


def get_database_name(database: str):
    return (
        "_".join([CommonEnviron.NEURON_TYPE, database])
        if database != "main"
        else database
    )


def get_database_path(database: str):
    return "{name}_{network}.db".format(
        name=get_database_name(database),
        network="finney"
        if "local" in CommonEnviron.SUBTENSOR_NETWORK
        else CommonEnviron.SUBTENSOR_NETWORK,
    )


async def main():
    databases_to_retrieve = {"active", "history"}

    socket.setdefaulttimeout(5)

    # noinspection PyProtectedMember
    ssl._create_default_https_context = ssl._create_unverified_context
    for database in databases_to_retrieve.copy():
        if os.path.isfile(get_database_path(database)):
            databases_to_retrieve.remove(database)
    if not databases_to_retrieve:
        bt.logging.info("Databases already exists")
        return
    wallet = bt.wallet(CommonEnviron.WALLET_NAME, CommonEnviron.WALLET_HOTKEY)
    hotkey = wallet.get_hotkey().ss58_address
    metagraph = bt.metagraph(
        const.NETUIDS[CommonEnviron.SUBTENSOR_NETWORK], CommonEnviron.SUBTENSOR_NETWORK
    )

    bit_ads_client = dependencies.create_bitads_client(
        wallet, const.BITADS_API_URLS[CommonEnviron.SUBTENSOR_NETWORK]
    )
    response = bit_ads_client.subnet_ping()
    neurons: Optional[Set[str]] = getattr(
        response, f"{CommonEnviron.NEURON_TYPE}s", None
    )
    if neurons is None:
        bt.logging.error(
            "Neurons is none. This is not expected behavior. "
            "Please check that your wallet is valid and NEURON_TYPE environment variable is set"
        )
        return
    try:
        neurons.remove(hotkey)
    except KeyError:
        pass  # All is ok
    if not neurons:
        bt.logging.info("All is ok, but no neurons to fetch database")
        return
    while neurons:
        t_neurons = tuple(neurons)
        random_hotkey = random.choice(t_neurons)
        neurons.remove(random_hotkey)

        axon = next(iter(a for a in metagraph.axons if a.hotkey == random_hotkey), None)
        if not axon:
            bt.logging.warning(
                f"How can BitAds return {random_hotkey} as active neuron, but it's not?"
            )
            continue
        for database in databases_to_retrieve.copy():
            try:
                response = urlretrieve(
                    f"https://{axon.ip}/get_database?db={database}",
                    get_database_path(database),
                )
                if response:
                    databases_to_retrieve.remove(database)
                    bt.logging.info(
                        f"We successfully fetch {database} from {random_hotkey}!"
                    )
            except URLError:
                bt.logging.warning(
                    f"Oops, guess we got a timeout from neuron with hotkey {random_hotkey}. "
                    f"Let's try another neuron"
                )
                break
    if databases_to_retrieve:
        bt.logging.warning(
            "Unfortunately, we can't fetch existing databases from neurons. "
            "So we create blank databases"
        )
    else:
        bt.logging.info("Databases successfully fetched")


if __name__ == "__main__":
    asyncio.run(main())
