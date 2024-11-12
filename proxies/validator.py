import logging
import threading
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, List, Optional, Dict

import uvicorn
from common.helpers import const
from fastapi import FastAPI, Depends, HTTPException, Header, status, Query

from common import dependencies as common_dependencies
from common.environ import Environ as CommonEnviron
from common.miner.schemas import VisitorSchema
from common.schemas.bitads import BitAdsDataSchema
from common.schemas.miner_assignment import (
    MinerAssignmentModel,
    SetMinerAssignmentsRequest,
)
from common.schemas.shopify import ShopifyBody, SaleData
from common.services.queue.exceptions import RefundNotExpectedWithoutOrder
from common.validator import dependencies
from common.validator.environ import Environ
from proxies.apis.fetch_from_db_test import router as test_router
from proxies.apis.get_database import router as database_router
from proxies.apis.logging import router as logs_router
from proxies.apis.version import router as version_router
from proxies.apis.two_factor import router as two_factor_router
from proxies.utils.validation import validate_hash
from template.api.metagraph import check_axon_exists

database_manager = common_dependencies.get_database_manager(
    "validator", CommonEnviron.SUBTENSOR_NETWORK
)
bitads_service = common_dependencies.get_bitads_service(database_manager)
order_queue = dependencies.get_order_queue_service(database_manager)
two_factor_service = common_dependencies.get_two_factor_service(database_manager)
miner_assignment_service = common_dependencies.get_miner_assignment_service(
    database_manager
)
metagraph: Optional["bittensor.metagraph"] = None
subtensor: Optional["bittensor.subtensor"] = None


metagraph_initialized: bool = False

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def init_metagraph_and_start_sync():
    """Initialize the metagraph and start the sync thread after app startup."""
    global metagraph, subtensor, metagraph_initialized

    # Import bittensor lazily
    import bittensor as bt

    # Initialize metagraph and subtensor
    bt.logging.info("Initializing metagraph...")
    metagraph = bt.metagraph(const.NETUIDS[CommonEnviron.SUBTENSOR_NETWORK])
    subtensor = bt.subtensor(CommonEnviron.SUBTENSOR_NETWORK)
    metagraph_initialized = True
    bt.logging.info("Metagraph initialized.")

    # Start the background sync thread
    sync_thread = threading.Thread(target=sync_metagraph_background, daemon=True)
    sync_thread.start()
    bt.logging.info("Background sync thread started.")


def sync_metagraph_background(sleep: int = 30):
    """Sync metagraph in the background every N seconds."""
    global metagraph, subtensor

    while True:
        if metagraph is not None and subtensor is not None:
            try:
                metagraph.sync(subtensor=subtensor)
                log.info("Metagraph synced successfully.")
            except Exception as e:
                log.info(f"Error syncing metagraph: {e}")

        # Wait for 15 seconds before the next sync
        time.sleep(sleep)


# noinspection PyUnresolvedReferences
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start a background thread that initializes the metagraph after startup."""
    init_thread = threading.Thread(target=init_metagraph_and_start_sync, daemon=True)
    init_thread.start()
    app.state.database_manager = database_manager
    app.state.two_factor_service = two_factor_service
    yield


app = FastAPI(
    version="0.6.2",
    lifespan=lifespan,
    debug=True,
    docs_url=None,
    redoc_url=None,
)

app.include_router(version_router)
app.include_router(test_router)
app.include_router(logs_router)
app.include_router(database_router)
app.include_router(two_factor_router)


@app.put("/shopify/init", dependencies=[Depends(validate_hash)])
async def init_from_shopify(
    body: ShopifyBody[SaleData], x_unique_id: Annotated[str, Header()]
) -> None:
    try:
        await order_queue.add_to_queue(x_unique_id, body.data)
    except RefundNotExpectedWithoutOrder:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund not expected without order",
        )


@app.get(
    "/tracking_data",
    summary="Retrieve tracking data within a date range",
    description="""
         Retrieve BitAds data that has been updated within the specified date range.
         - `updated_from`: The start date of the range (inclusive).
         - `updated_to`: The end date of the range (exclusive).
         - `page_number`: The page number to retrieve.
         - `page_size`: The number of records per page.
         """,
)
async def get_tracking_data(
    updated_from: datetime = None,
    updated_to: datetime = None,
    page_number: int = 1,
    page_size: int = 500,
) -> List[BitAdsDataSchema]:
    return await bitads_service.get_bitads_data_between(
        updated_from, updated_to, page_number, page_size
    )


@app.get("/tracking_data/by_campaign_item")
async def get_bidads_data_by_campaign_item(
    campaign_item: Annotated[list, Query()],
    page_number: int = 1,
    page_size: int = 500,
) -> List[BitAdsDataSchema]:
    return await bitads_service.get_by_campaign_items(
        campaign_item, page_number, page_size
    )


@app.get("/tracking_data/{id}")
async def get_visit_by_id(id: str) -> Optional[BitAdsDataSchema]:
    result = await bitads_service.get_data_by_ids({id})
    return next(iter(result), None)


@app.put("/tracking_data", dependencies=[Depends(validate_hash)])
async def put_visit(body: VisitorSchema) -> None:
    await bitads_service.add_by_visit(body)


@app.get("/is_axon_exists")
async def is_axon_exists(
    hotkey: str, ip_address: Optional[str] = None, coldkey: Optional[str] = None
) -> Dict[str, bool]:
    global metagraph_initialized

    if not metagraph_initialized:
        raise HTTPException(
            status.HTTP_406_NOT_ACCEPTABLE,
            detail="Metagraph is still initializing, please try again later.",
        )

    # Once initialized, reuse the metagraph for the request
    return {"exists": check_axon_exists(metagraph, hotkey, ip_address, coldkey)}


@app.get("/order_ids")
async def get_order_ids() -> List[str]:
    return await order_queue.get_all_ids()


@app.get("/miner_assignments")
async def get_miner_assignments() -> SetMinerAssignmentsRequest:
    assignments = await miner_assignment_service.get_miner_assignments()
    return SetMinerAssignmentsRequest(assignments=assignments)


@app.put("/miner_assignments", dependencies=[Depends(validate_hash)])
async def set_miner_assignments(body: SetMinerAssignmentsRequest):
    await miner_assignment_service.set_miner_assignments(body.assignments)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=Environ.PROXY_PORT,
        ssl_certfile="cert.pem",
        ssl_keyfile="key.pem",
    )
