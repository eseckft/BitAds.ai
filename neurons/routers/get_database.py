from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi import Request
from fastapi.responses import FileResponse
from sqlalchemy import Engine

from common.db.database import DatabaseManager

router = APIRouter()


@router.get("/get_database")
async def get_database(
    db: Literal["main", "history", "active"], request: Request
):
    """Retrieve version information"""
    database: DatabaseManager = request.app.state.database_manager
    if not database:
        raise HTTPException(404, "DB not found")

    engine: Engine = getattr(database, f"{db}_db")

    if not engine:
        return HTTPException(404, "DB not found")

    return FileResponse(
        engine.url.database,
        media_type="application/octet-stream",
        filename=engine.url.database,
    )
