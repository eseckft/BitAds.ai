import argparse
import asyncio
import json

from common.environ import Environ
from common.validator import dependencies
from template import __spec_version__ as version_key
import bittensor as bt

database_manager = dependencies.get_database_manager(
    "validator", Environ.SUBTENSOR_NETWORK
)
validator_service = dependencies.get_validator_service(database_manager)

parser = argparse.ArgumentParser()


def add_args(parser: argparse.ArgumentParser):
    bt.wallet.add_args(parser)
    bt.subtensor.add_args(parser)

    parser.add_argument("--netuid", type=int, default=16, help="The chain subnet uid.")


async def main():
    add_args(parser)
    parser.parse_args()

    config = bt.config(parser)
    subtensor_network = config.subtensor.network
    netuid = config.netuid

    wallet = bt.wallet(config=config)
    subtensor = bt.subtensor(subtensor_network, config)
    metagraph = bt.metagraph(config.netuid, subtensor_network)

    current_block = subtensor.get_current_block()
    miner_ratings = await validator_service.calculate_ratings(to_block=current_block)

    bt.logging.info(
        f"Ratings: {json.dumps(dict(sorted(miner_ratings.items(), key=lambda i: i[1], reverse=True)), indent=4)}"
    )

    hotkey_to_uid = {n.hotkey: n.uid for n in metagraph.neurons}

    miner_ratings = {
        uid: miner_ratings.get(hotkey, 0.0) for hotkey, uid in hotkey_to_uid.items()
    }

    subtensor.set_weights(
        wallet,
        netuid,
        list(miner_ratings.keys()),
        list(miner_ratings.values()),
        version_key,
        wait_for_inclusion=True,
        wait_for_finalization=True,
    )


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    asyncio.run(main())
