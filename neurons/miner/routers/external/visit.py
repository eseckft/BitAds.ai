from typing import Annotated, Optional

from fastapi import Depends, APIRouter
from fiber.logging_utils import get_logger

from common.miner import dependencies
from common.miner.schemas import VisitorSchema
from common.services.miner.base import MinerService

logger = get_logger(__name__)


router = APIRouter()


@router.get("/visitors/{id}")
async def get_visit_by_id(
    id: str,
    miner_service: Annotated[MinerService, Depends(dependencies.get_miner_service)],
) -> Optional[VisitorSchema]:
    return await miner_service.get_visit_by_id(id)
