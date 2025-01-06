import json
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Annotated, Optional, List

import uvicorn
from fastapi import (
    FastAPI,
    Request,
    Depends,
    Header,
    status,
    Path,
)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from common import dependencies as common_dependencies, utils
from common.environ import Environ as CommonEnviron
from common.helpers import const
from common.miner import dependencies
from common.miner.environ import Environ
from common.miner.schemas import VisitorSchema
from common.schemas.campaign import CampaignType
from common.services.geoip.base import GeoIpService
from proxies.apis.fetch_from_db_test import router as test_router
from proxies.apis.get_database import router as database_router
from proxies.apis.logging import router as logs_router
from proxies.apis.two_factor import router as two_factor_router
from proxies.apis.version import router as version_router

database_manager = common_dependencies.get_database_manager(
    "miner", CommonEnviron.SUBTENSOR_NETWORK
)
campaign_service = common_dependencies.get_campaign_service(database_manager)
miner_service = dependencies.get_miner_service(database_manager)
two_factor_service = common_dependencies.get_two_factor_service(
    database_manager
)


# noinspection PyUnresolvedReferences
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database_manager = database_manager
    app.state.two_factor_service = two_factor_service
    app.state.campaign_service = campaign_service
    yield


app = FastAPI(version="0.7.2", lifespan=lifespan)

app.mount(
    "/statics", StaticFiles(directory="statics", html=True), name="statics"
)

app.include_router(version_router)
app.include_router(test_router)
app.include_router(logs_router)
app.include_router(database_router)
app.include_router(two_factor_router)


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
async def internal_exception_handler(request: Request, exc: Exception):
    log.error(exc, exc_info=True)
    return RedirectResponse(request.url)


@app.get("/visitors/by_campaign_item")
async def get_visits_by_campaign_item(
    campaign_item: str,
) -> List[VisitorSchema]:
    return await miner_service.get_visits_by_campaign_item(campaign_item)


@app.get("/visitors/{id}")
async def get_visit_by_id(id: str) -> Optional[VisitorSchema]:
    return await miner_service.get_visit_by_id(id)


@app.get("/{campaign_id}/{campaign_item}")
async def fetch_request_data_and_redirect(
    campaign_id: str,
    campaign_item: Annotated[
        str,
        Path(
            regex=r"^[a-zA-Z0-9]{13}$",  # Alphanumeric characters, exactly 13
            title="Campaign Item",
            description="Must be exactly 13 alphanumeric characters",
        ),
    ],
    request: Request,
    geoip_service: Annotated[
        GeoIpService, Depends(common_dependencies.get_geo_ip_service)
    ],
    user_agent: Annotated[str, Header()],
    referer: Annotated[Optional[str], Header()] = None,
):
    campaign = await campaign_service.get_campaign_by_id(campaign_id)
    if not campaign or not campaign.countries_approved_for_product_sales:
        logging.warning(
            f"Campaign by id {campaign_id} not found. Maybe another miner can"
        )
        raise KeyError  # In case when miner neuron not fetched campaigns
    id_ = str(uuid.uuid4())
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    ipaddr_info = geoip_service.get_ip_info(ip)
    if ipaddr_info and ipaddr_info.country_code not in json.loads(
        campaign.countries_approved_for_product_sales
    ):
        return RedirectResponse(
            "/statics/403",
        )
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
    if const.TEST_REDIRECT != campaign_item:
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
