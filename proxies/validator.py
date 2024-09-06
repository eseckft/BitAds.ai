import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime
from datetime import timedelta
from typing import Annotated, List

import bittensor as bt
import uvicorn
from bitads_security.checkers import check_hash
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Header,
    Request,
    Query,
    Body,
    status,
)
from fastapi.responses import Response
from pydantic import ValidationError

from common import dependencies as common_dependencies, converters
from common.clients.bitads.base import BitAdsClient
from common.environ import Environ as CommonEnviron
from common.helpers import const
from common.schemas.bitads import FormulaParams, BitAdsDataSchema
from common.schemas.shopify import ShopifyBody, SaleData
from common.services.geoip.base import GeoIpService
from common.validator import dependencies
from common.validator.environ import Environ
from common.validator.schemas import (
    ValidatorTrackingData,
    InitVisitRequest,
    ActionRequest,
)
from proxies.apis.fetch_from_db_test import router as test_router
from proxies.apis.get_database import router as database_router
from proxies.apis.logging import router as logs_router
from proxies.apis.version import router as version_router

subtensor = common_dependencies.get_subtensor(CommonEnviron.SUBTENSOR_NETWORK)

database_manager = common_dependencies.get_database_manager(
    "validator", CommonEnviron.SUBTENSOR_NETWORK
)
validator_service = dependencies.get_validator_service(database_manager)
bitads_service = common_dependencies.get_bitads_service(database_manager)


# noinspection PyUnresolvedReferences
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.subtensor = subtensor
    app.state.database_manager = database_manager
    wallet = common_dependencies.get_wallet(
        CommonEnviron.WALLET_NAME, CommonEnviron.WALLET_HOTKEY
    )
    app.state.wallet = wallet
    bit_ads_client = common_dependencies.create_bitads_client(
        wallet, const.BITADS_API_URLS[CommonEnviron.SUBTENSOR_NETWORK]
    )
    app.state.bitads_client = bit_ads_client
    await _update_settings(bit_ads_client)
    # noinspection PyAsyncCall
    asyncio.create_task(_periodic_update_settings(bit_ads_client))
    yield
    subtensor.close()


app = FastAPI(version="0.2.13", lifespan=lifespan, debug=True)

app.include_router(version_router)
app.include_router(test_router)
app.include_router(logs_router)
app.include_router(database_router)


# app.mount(
#     "/campaigns",
#     StaticFiles(directory="statics/campaigns", html=True),
#     name="statics",
# )


def validate_hash(
    x_unique_id: Annotated[str, Header()],
    x_signature: Annotated[str, Header()],
    campaign_id: str = "",
    body: dict = None,
    sep: Annotated[str, Query(include_in_schema=False)] = "",
) -> None:
    if not check_hash(x_unique_id, x_signature, campaign_id, body, sep):
        raise HTTPException(status_code=401)


@app.put("/shopify/init", dependencies=[Depends(validate_hash)])
async def init_from_shopify(
    request: Request, body: ShopifyBody[SaleData], x_unique_id: Annotated[str, Header()]
) -> None:
    existed_datas = await bitads_service.get_data_by_ids({x_unique_id})
    if not existed_datas:
        raise HTTPException(status_code=status.HTTP_428_PRECONDITION_REQUIRED)

    wallet: bt.wallet = request.app.state.wallet
    order_details = body.data.order_details
    client_info = order_details.client_info
    customer_details = order_details.customer_info
    try:
        data = await validator_service.add_tracking_data(
            converters.to_tracking_data(
                x_unique_id,
                body.data,
                client_info.user_agent,
                client_info.browser_ip,
                customer_details.address.country,
                subtensor.get_current_block(),
                wallet.get_hotkey().ss58_address,
            ),
            next(iter(existed_datas))
        )
        await bitads_service.add_or_update_validator_bitads_data(data, body.data)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=json.loads(e.json())
        )


@app.put(
    "/{campaign_id}/init",
    dependencies=[Depends(validate_hash)],
    summary="Initialize Visit Information",
    description=(
        "This endpoint initializes visit information for a campaign. It collects user data such as user agent, IP address, "
        "and device information. The collected data is stored in the tracking database for further analysis and tracking."
    ),
)
async def collect_visit_information(
    request: Request,
    campaign_id: str,
    body: InitVisitRequest,
    user_agent: Annotated[str, Header()],
    x_unique_id: Annotated[str, Header()],
    geoip_service: Annotated[
        GeoIpService, Depends(common_dependencies.get_geo_ip_service)
    ],
) -> None:
    if not request.client:
        raise HTTPException(status_code=400, detail="Client not found")
    wallet: bt.wallet = request.app.state.wallet
    ipaddr_info = geoip_service.get_ip_info(request.client.host)
    try:
        data = ValidatorTrackingData(
            id=x_unique_id,
            user_agent=user_agent,
            ip_address=request.client.host,
            country=ipaddr_info.country_name if ipaddr_info else None,
            campaign_id=campaign_id,
            validator_block=subtensor.get_current_block(),
            at=False,
            device=body.device,
            validator_hotkey=wallet.get_hotkey().ss58_address,
        )
        await validator_service.add_tracking_data(data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=json.loads(e.json()))
    except KeyError:
        raise HTTPException(status_code=400, detail="Data already exists")


@app.post(
    "/{campaign_id}/action",
    dependencies=[Depends(validate_hash)],
    summary="Send User Action",
    description=(
        "This endpoint allows for the submission of user actions associated with a campaign. "
        "Depending on the action type specified in the request body, it increments the count of specific actions "
        "(like image clicks, mouse movements, read more clicks, and through rate clicks) or updates the visit duration."
    ),
)
async def send_action(
    body: Annotated[
        ActionRequest,
        Body(
            examples=[
                {"type": "image_click"},
                {"type": "update_visit_duration"},
            ],
        ),
    ],
    x_unique_id: Annotated[str, Header()],
) -> None:
    await validator_service.send_action(x_unique_id, body.type, body.amount)


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


async def _periodic_update_settings(
    bit_ads_client: BitAdsClient, period: timedelta = timedelta(seconds=30)
):
    while True:
        await asyncio.sleep(period.total_seconds())
        try:
            await _update_settings(bit_ads_client)
        except:
            bt.logging.exception("Update settings exception")


async def _update_settings(bit_ads_client: BitAdsClient):
    response = bit_ads_client.subnet_ping()
    if not response or not response.result:
        return
    validator_service.settings = FormulaParams.from_settings(response.settings)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=Environ.PROXY_PORT,
        ssl_certfile="cert.pem",
        ssl_keyfile="key.pem",
    )
