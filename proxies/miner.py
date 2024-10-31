import uuid
from typing import Annotated, Optional

import uvicorn
from fastapi import Request, Depends, Header, status, Path, HTTPException
from fastapi.responses import RedirectResponse
from fiber.logging_utils import get_logger
from fiber.miner import server
from fiber.miner.endpoints.subnet import factory_router as get_subnet_router

from common import dependencies as common_dependencies, utils
from common.miner import dependencies
from common.miner.environ import Environ
from common.miner.schemas import VisitorSchema
from common.schemas.bitads import Campaign
from common.schemas.campaign import CampaignType
from common.services.campaign.base import CampaignService
from common.services.geoip.base import GeoIpService
from common.services.miner.base import MinerService
from proxies.apis.fetch_from_db_test import router as test_router
from proxies.apis.get_database import router as database_router
from proxies.apis.logging import router as logs_router
from proxies.apis.two_factor import router as two_factor_router
from proxies.apis.version import router as version_router

# Configure the application
app = server.factory_app()
app.version = "0.5.0"

# Include all routers in a modular and readable way
routers = [
    get_subnet_router(),
    version_router,
    test_router,
    logs_router,
    database_router,
    two_factor_router,
]
for router in routers:
    app.include_router(router)

# Initialize logger with the appropriate configuration
logger = get_logger(__name__)


# Error handling with clear error response
@app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
async def internal_exception_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error at {request.url.path}: {exc}", exc_info=True)
    return RedirectResponse(url="/error", status_code=status.HTTP_302_FOUND)


# Handler function to fetch visit by ID, with annotated return type
@app.get("/visitors/{id}", response_model=Optional[VisitorSchema])
async def get_visit_by_id(
    id: str,
    miner_service: Annotated[MinerService, Depends(dependencies.get_miner_service)],
) -> Optional[VisitorSchema]:
    visit = await miner_service.get_visit_by_id(id)
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found"
        )
    return visit


# Main route to fetch campaign data, structured with helper functions for readability
@app.get("/{campaign_id}/{campaign_item}")
async def fetch_request_data_and_redirect(
    request: Request,
    campaign_id: str,
    campaign_item: Annotated[
        str,
        Path(
            pattern=r"^[a-zA-Z0-9]{13}$",
            title="Campaign Item",
            description="Must be exactly 13 alphanumeric characters",
        ),
    ],
    geoip_service: Annotated[
        GeoIpService, Depends(common_dependencies.get_geo_ip_service)
    ],
    campaign_service: Annotated[
        CampaignService, Depends(common_dependencies.get_campaign_service)
    ],
    miner_service: Annotated[MinerService, Depends(dependencies.get_miner_service)],
    user_agent: Annotated[str, Header()],
    referer: Annotated[Optional[str], Header()] = None,
) -> RedirectResponse:
    # Helper function to get campaign and validate its existence
    campaign = await campaign_service.get_campaign_by_id(campaign_id)
    if not campaign:
        logger.error(f"Campaign with ID {campaign_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    # Generate a unique visit ID
    visit_id = str(uuid.uuid4())

    # Process IP information and visitor details
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    ipaddr_info = geoip_service.get_ip_info(ip)
    visitor = await create_visitor_schema(
        id_=visit_id,
        referer=referer,
        ip=request.client.host,
        campaign_id=campaign_id,
        user_agent=user_agent,
        campaign_item=campaign_item,
        miner_service=miner_service,
        geoip_info=ipaddr_info,
    )

    # Save visitor and log result
    await miner_service.add_visit(visitor)
    logger.info(f"Saved visit with ID: {visitor.id}")

    # Generate and return the appropriate redirection URL
    redirect_url = generate_redirect_url(campaign, visit_id, campaign_id)
    return RedirectResponse(url=redirect_url)


# Helper function to create a VisitorSchema object for the visit
async def create_visitor_schema(
    id_: str,
    referer: Optional[str],
    ip: str,
    campaign_id: str,
    user_agent: str,
    campaign_item: str,
    miner_service: MinerService,
    geoip_info,
) -> VisitorSchema:
    hotkey, block = await miner_service.get_hotkey_and_block()
    device = utils.determine_device(user_agent)
    country = geoip_info.country_name if geoip_info else None
    country_code = geoip_info.country_code if geoip_info else None
    return VisitorSchema(
        id=id_,
        referer=referer,
        ip_address=ip,
        campaign_id=campaign_id,
        user_agent=user_agent,
        campaign_item=campaign_item,
        miner_hotkey=hotkey,
        miner_block=block,
        at=False,
        device=device,
        country=country,
        country_code=country_code,
    )


# Helper function to generate the redirect URL
def generate_redirect_url(campaign: Campaign, visit_id: str, campaign_id: str) -> str:
    if campaign.type == CampaignType.CPA:
        return f"{campaign.product_link}?visit_hash={visit_id}"
    else:
        return f"https://v.bitads.ai/campaigns/{campaign_id}?id={visit_id}"


# Entry point for the application
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=Environ.PROXY_PORT,
        ssl_certfile="cert.pem",
        ssl_keyfile="key.pem",
    )
