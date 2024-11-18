import asyncio
import contextlib
import socket
import threading
from collections.abc import AsyncIterator, Callable, Sequence
from contextlib import AbstractAsyncContextManager

from common.environ import Environ
from fastapi import FastAPI
from fiber.chain import interface, chain_utils, post_ip_to_chain
from fiber.logging_utils import get_logger
from fiber.miner.core import configuration

logger = get_logger(__name__)


@contextlib.asynccontextmanager
async def _manager(
    app: FastAPI,
    lifespans: Sequence[Callable[[FastAPI], AbstractAsyncContextManager[None]]],
) -> AsyncIterator[None]:
    exit_stack = contextlib.AsyncExitStack()
    async with exit_stack:
        for lifespan in lifespans:
            await exit_stack.enter_async_context(lifespan(app))
        yield


class Lifespans:
    def __init__(
        self,
        lifespans: Sequence[Callable[[FastAPI], AbstractAsyncContextManager[None]]],
    ) -> None:
        self.lifespans = lifespans

    def __call__(self, app: FastAPI) -> AbstractAsyncContextManager[None]:
        self.app = app
        return _manager(app, lifespans=self.lifespans)


@contextlib.asynccontextmanager
async def fiber_lifespan(app: FastAPI):
    config = configuration.factory_config()
    metagraph = config.metagraph
    sync_thread = None
    if metagraph.substrate is not None:
        sync_thread = threading.Thread(
            target=metagraph.periodically_sync_nodes, daemon=True
        )
        sync_thread.start()

    yield

    logger.info("Shutting down...")

    config.encryption_keys_handler.close()
    metagraph.shutdown()
    if metagraph.substrate is not None and sync_thread is not None:
        sync_thread.join()


async def infinite_task():
    while True:
        print("Running background task...")
        # Place your logic here
        await asyncio.sleep(10)  # Delay between each iteration


def get_external_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        logger.exception("Error getting local IP")
        ip = None
    finally:
        s.close()
    return ip


# noinspection PyAsyncCall
@contextlib.asynccontextmanager
async def bitads_lifespan(app: FastAPI) -> AsyncIterator[None]:
    asyncio.create_task(infinite_task())  # Start the background task
    yield


lifespan = Lifespans([fiber_lifespan, bitads_lifespan])
