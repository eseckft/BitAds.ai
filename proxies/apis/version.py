from typing import Dict

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/version")
async def version(request: Request) -> Dict[str, str]:
    """Retrieve version information"""

    return {"version": request.app.version}
