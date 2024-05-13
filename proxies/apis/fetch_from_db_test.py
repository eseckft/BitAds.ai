from typing import Dict, Literal, List, Optional, Any

import sqlalchemy.exc
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import text

from common.db.database import DatabaseManager

router = APIRouter()


@router.get("/fetch_from_db")
async def version(
    db: Literal["main", "history", "active"], table: str, request: Request
) -> List[Dict[str, Optional[Any]]]:
    """Retrieve version information"""
    database: DatabaseManager = request.app.state.database_manager
    if not database:
        raise HTTPException(404, "DB not found")

    query = text(f"SELECT * FROM {table} ORDER BY created_at")

    try:
        with database.get_session(db) as session:
            result = session.execute(query)
            rows = result.fetchall()
            columns = result.keys()
    except sqlalchemy.exc.SQLAlchemyError:
        raise HTTPException(404, f"Table not found in database {db}")

    return [dict(zip(columns, row)) for row in rows]
