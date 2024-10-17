import logging
import uuid
from contextlib import asynccontextmanager
from typing import Annotated, Optional

import uvicorn
from fastapi import (
    FastAPI,
    Request,
    Depends,
    Header,
    HTTPException,
    status,
)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from common import dependencies as common_dependencies, utils
from common.environ import Environ as CommonEnviron
from common.miner import dependencies
from common.miner.environ import Environ
from common.miner.schemas import VisitorSchema
from common.schemas.bitads import Campaign
from common.schemas.campaign import CampaignType
from common.services.geoip.base import GeoIpService
from proxies import __miner_version__
from proxies.apis.fetch_from_db_test import router as test_router
from proxies.apis.get_database import router as database_router
from proxies.apis.logging import router as logs_router
from proxies.apis.version import router as version_router
from proxies.apis.two_factor import router as two_factor_router


database_manager = common_dependencies.get_database_manager(
    "miner", CommonEnviron.SUBTENSOR_NETWORK
)
campaign_service = common_dependencies.get_campaign_service(database_manager)
miner_service = dependencies.get_miner_service(database_manager)
two_factor_service = common_dependencies.get_two_factor_service(database_manager)


# noinspection PyUnresolvedReferences
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database_manager = database_manager
    app.state.two_factor_service = two_factor_service
    yield


app = FastAPI(version="0.4.1", lifespan=lifespan)

app.mount("/statics", StaticFiles(directory="statics"), name="statics")

app.include_router(version_router)
app.include_router(test_router)
app.include_router(logs_router)
app.include_router(database_router)
app.include_router(two_factor_router)


log = logging.getLogger(__name__)


@app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
async def internal_exception_handler(request: Request, exc: Exception):
    log.error(exc, exc_info=True)
    return RedirectResponse(request.url)


@app.get("/visitors/{id}")
async def get_visit_by_id(id: str) -> Optional[VisitorSchema]:
    return await miner_service.get_visit_by_id(id)


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
    campaigns = await campaign_service.get_active_campaigns()
    campaign: Campaign = next(
        filter(lambda c: c.product_unique_id == campaign_id, campaigns), None
    )
    if not campaign:
        raise KeyError  # In case when miner neuron not fetched campaigns
    id_ = str(uuid.uuid4())
    ip = request.client.host
    ipaddr_info = geoip_service.get_ip_info(ip)
    hotkey, block = await miner_service.get_hotkey_and_block()
    visitor = VisitorSchema(
        id=id_,
        referer=referer,
        ip_address=request.client.host,
        campaign_id=campaign_id,
        user_agent=user_agent,
        campaign_item=campaign_item,
        miner_hotkey=hotkey,
        miner_block=block,
        at=False,
        device=utils.determine_device(user_agent),
        country=ipaddr_info.country_name if ipaddr_info else None,
        country_code=ipaddr_info.country_code if ipaddr_info else None,
    )
    await miner_service.add_visit(visitor)
    log.info(f"Saved visit: {visitor.id}")
    url = (
        f"{campaign.product_link}?visit_hash={id_}"
        if campaign.type == CampaignType.CPA
        else f"https://v.bitads.ai/campaigns/{campaign_id}?id={id_}"
    )
    return RedirectResponse(url=url)


@app.get("/fingerprint")
async def fingerprint():
    return HTMLResponse(content=FINGERPRINT_HTML_CONTENT)


FINGERPRINT_HTML_CONTENT = """
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


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=Environ.PROXY_PORT,
        ssl_certfile="cert.pem",
        ssl_keyfile="key.pem",
    )
