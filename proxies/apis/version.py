import sqlite3
from typing import Dict

import aiohttp
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/version")
async def version(request: Request) -> Dict[str, str]:
    """Retrieve version information"""

    return {
        "version": request.app.version,
        "sqlite_version": sqlite3.sqlite_version,
        "aiohttp_version": aiohttp.__version__
    }
