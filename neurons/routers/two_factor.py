from fastapi import APIRouter, Depends, Request

from common.schemas.bitads import TwoFactorRequest
from common.services.two_factor.base import TwoFactorService
from proxies.utils.validation import validate_hash

router = APIRouter()


@router.post("/2fa", dependencies=[Depends(validate_hash)])
async def two_factor(
    body: TwoFactorRequest, request: Request
) -> None:
    two_factor_service: TwoFactorService = request.app.state.two_factor_service

    await two_factor_service.add_from_request(body)
