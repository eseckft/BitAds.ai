from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, List

import uvicorn
from bitads_security.checkers import check_hash
from fastapi import FastAPI, Depends, HTTPException, Header, Query, status

from common import dependencies as common_dependencies
from common.environ import Environ as CommonEnviron
from common.schemas.bitads import BitAdsDataSchema
from common.schemas.shopify import ShopifyBody, SaleData
from common.services.queue.exceptions import RefundNotExpectedWithoutOrder
from common.validator import dependencies
from common.validator.environ import Environ
from proxies import __validator_version__
from proxies.apis.fetch_from_db_test import router as test_router
from proxies.apis.get_database import router as database_router
from proxies.apis.logging import router as logs_router
from proxies.apis.version import router as version_router

database_manager = common_dependencies.get_database_manager(
    "validator", CommonEnviron.SUBTENSOR_NETWORK
)
bitads_service = common_dependencies.get_bitads_service(database_manager)
order_queue = dependencies.get_order_queue_service(database_manager)


# noinspection PyUnresolvedReferences
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database_manager = database_manager
    yield


app = FastAPI(
    version="0.3.6",
    lifespan=lifespan,
    debug=True,
    docs_url=None,
    redoc_url=None,
)

app.include_router(version_router)
app.include_router(test_router)
app.include_router(logs_router)
app.include_router(database_router)


def validate_hash(
    x_unique_id: Annotated[str, Header()],
    x_signature: Annotated[str, Header()],
    campaign_id: str = "",
    body: dict = None,
    sep: Annotated[str, Query(include_in_schema=False)] = "",
) -> None:
    if not check_hash(x_unique_id, x_signature, campaign_id, body, sep):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


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


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=Environ.PROXY_PORT,
        ssl_certfile="cert.pem",
        ssl_keyfile="key.pem",
    )
