import random
import sqlite3
from typing import Dict, Any

import aiohttp
from fastapi import APIRouter, Request, status

from common.environ import Environ
from common.helpers import const
from common.schemas.bitads import Campaign
from common.services.campaign.base import CampaignService

router = APIRouter()


async def verify_redirect(campaign_service: CampaignService):
    try:
        campaigns = await campaign_service.get_active_campaigns()
        campaign: Campaign = random.choice(campaigns)
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
            async with session.get(
                f"https://localhost/{campaign.product_unique_id}/{const.TEST_REDIRECT}",
                ssl=False,
            ) as response:
                return response.status == status.HTTP_200_OK
    except Exception:
        return False


@router.get("/version")
async def version(request: Request) -> Dict[str, Any]:
    """Retrieve version information"""

    result = {
        "version": request.app.version,
        "sqlite_version": sqlite3.sqlite_version,
        "aiohttp_version": aiohttp.__version__,
    }
    if Environ.NEURON_TYPE == "miner":
        result["redirect"] = await verify_redirect(request.app.state.campaign_service)
    return result
