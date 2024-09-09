import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Annotated, Optional

import bittensor as bt
import uvicorn
from fastapi import (
    FastAPI,
    Request,
    Depends,
    BackgroundTasks,
    Header,
    HTTPException,
    status,
)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from common import dependencies as common_dependencies, utils
from common.clients.bitads.base import BitAdsClient
from common.environ import Environ as CommonEnviron
from common.helpers import const
from common.miner import dependencies
from common.miner.environ import Environ
from common.miner.schemas import VisitorSchema
from common.schemas.bitads import FormulaParams
from common.schemas.campaign import CampaignType
from common.services.geoip.base import GeoIpService
from proxies.apis.fetch_from_db_test import router as test_router
from proxies.apis.version import router as version_router
from proxies.apis.logging import router as logs_router
from proxies.apis.get_database import router as database_router
from proxies import __miner_version__


subtensor = common_dependencies.get_subtensor(CommonEnviron.SUBTENSOR_NETWORK)
database_manager = common_dependencies.get_database_manager(
    "miner", CommonEnviron.SUBTENSOR_NETWORK
)
miner_service = dependencies.get_miner_service(database_manager)
campaign_to_product_link = {}
campaign_ids = set()


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
    await _update_settings(bit_ads_client)
    # noinspection PyAsyncCall
    asyncio.create_task(_periodic_update_settings(bit_ads_client))
    yield
    subtensor.close()


app = FastAPI(version=__miner_version__, lifespan=lifespan, debug=True)
app.mount("/statics", StaticFiles(directory="statics"), name="statics")

app.include_router(version_router)
app.include_router(test_router)
app.include_router(logs_router)
app.include_router(database_router)


log = logging.getLogger(__name__)


@app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
async def internal_exception_handler(request: Request, exc: Exception):
    log.error(exc, exc_info=True)
    return RedirectResponse(request.url)


@app.get("/{campaign_id}/{campaign_item}")
async def fetch_request_data_and_redirect(
    campaign_id: str,
    campaign_item: str,
    request: Request,
    geoip_service: Annotated[
        GeoIpService, Depends(common_dependencies.get_geo_ip_service)
    ],
    user_agent: Annotated[str, Header()],
    referer: Annotated[Optional[str], Header()] = None,
):
    if campaign_id not in campaign_ids:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    id_ = str(uuid.uuid4())
    ip = request.client.host
    wallet: bt.wallet = request.app.state.wallet
    ipaddr_info = geoip_service.get_ip_info(ip)
    visitor = VisitorSchema(
        id=id_,
        referer=referer,
        ip_address=request.client.host,
        campaign_id=campaign_id,
        user_agent=user_agent,
        campaign_item=campaign_item,
        miner_hotkey=wallet.get_hotkey().ss58_address,
        miner_block=subtensor.get_current_block(),
        at=False,
        device=utils.determine_device(user_agent),
        return_in_site=False,
        country=ipaddr_info.country_name if ipaddr_info else None,
        country_code=ipaddr_info.country_code if ipaddr_info else None,
    )
    await miner_service.add_visit(visitor)
    log.info(f"Saved visit: {visitor.id}")
    # background_tasks.add_task(
    #     _save_request_info,
    #     id_=id_,
    #     campaign_id=campaign_id,
    #     campaign_item=campaign_item,
    #     referer=referer,
    #     user_agent=user_agent,
    #     request=request,
    #     geoip_service=geoip_service,
    # )
    url = (
        f"{campaign_to_product_link[campaign_id]}?visit_hash={id_}"
        if campaign_id in campaign_to_product_link
        else f"https://v.bitads.ai/campaigns/{campaign_id}?id={id_}"
    )
    return RedirectResponse(url=url)


@app.get("/fingerprint")
async def fingerprint():
    return HTMLResponse(content=FINGERPRINT_HTML_CONTENT)


async def _save_request_info(
    id_: str,
    referer: Optional[str],
    user_agent: str,
    campaign_id: str,
    campaign_item: str,
    request: Request,
    geoip_service: GeoIpService,
):
    wallet: bt.wallet = request.app.state.wallet
    try:
        ip = request.client.host
        ipaddr_info = geoip_service.get_ip_info(ip)
        visitor = VisitorSchema(
            id=id_,
            referer=referer,
            ip_address=request.client.host,
            campaign_id=campaign_id,
            user_agent=user_agent,
            campaign_item=campaign_item,
            miner_hotkey=wallet.get_hotkey().ss58_address,
            miner_block=subtensor.get_current_block(),
            at=False,
            device=utils.determine_device(user_agent),
            return_in_site=False,
            country=ipaddr_info.country_name if ipaddr_info else None,
            country_code=ipaddr_info.country_code if ipaddr_info else None,
        )
        await miner_service.add_visit(visitor)
        log.info(f"Saved visit: {visitor.id}")
    except:
        log.exception("Exception in background task _save_request_info")


FINGERPRINT_HTML_CONTENT = html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fingerprinting</title>
        <script type="module">
          import FingerprintJS from '/statics/scripts/fingerprint_v4.js';
          const fpPromise = FingerprintJS.load();
          fpPromise
            .then(fp => fp.get())
            .then(result => {
                const visitorId = result.visitorId;
                document.write(visitorId);
                fetch('/submit_fingerprint', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ fingerprint: visitorId })
                }).then(response => {
                    if (response.ok) {
                        window.location.href = "/final_redirect";
                    } else {
                        console.error('Fingerprint submission failed');
                    }
                });
            });
        </script>
    </head>
    </html>
"""


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
    miner_service.settings = FormulaParams.from_settings(response.settings)
    campaign_ids.update(c.product_unique_id for c in response.campaigns)
    campaign_to_product_link.update(
        {
            c.product_unique_id: c.product_link
            for c in response.campaigns
            if c.type == CampaignType.CPA
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=Environ.PROXY_PORT,
        ssl_certfile="cert.pem",
        ssl_keyfile="key.pem",
    )
