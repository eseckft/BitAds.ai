import uuid
from typing import Annotated, Optional

from common.schemas.bitads import Campaign

from common.schemas.campaign import CampaignType

from common.miner.schemas import VisitorSchema

from common.services.miner.base import MinerService
from fastapi.responses import RedirectResponse
from fiber.logging_utils import get_logger

from common.services.campaign.base import CampaignService

from common.services.geoip.base import GeoIpService
from common import dependencies as common_dependencies, utils
from common.miner import dependencies
from fastapi import Path, Depends, Header, HTTPException, status, Request, APIRouter

logger = get_logger(__name__)


router = APIRouter()


# Main route to fetch campaign data, structured with helper functions for readability
@router.get("/{campaign_id}/{campaign_item}")
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
