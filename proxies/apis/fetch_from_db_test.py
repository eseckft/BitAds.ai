import pickle
from typing import Dict, List, Optional, Any, Literal

import sqlalchemy
from fastapi import HTTPException, Request, APIRouter
from sqlalchemy import text

from common.db.database import DatabaseManager

router = APIRouter()


def deserialize(value: Any) -> Any:
    """Attempt to deserialize pickled data or handle other binary formats."""
    try:
        # Check if the value is bytes (common for pickled data)
        if isinstance(value, bytes):
            try:
                return pickle.loads(value)
            except Exception:
                return f"Failed to deserialize pickled data"
        return value
    except Exception as e:
        return f"Error: {str(e)}"


@router.get("/fetch_from_db")
async def fetch_from_db(
    db: Literal["main", "history", "active"], table: str, request: Request
) -> List[Dict[str, Optional[Any]]]:
    """Retrieve data from the specified table and return it."""
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

    # Deserialize data and handle errors
    data = []
    for row in rows:
        row_dict = {}
        for col_name, value in zip(columns, row):
            row_dict[col_name] = deserialize(value)
        data.append(row_dict)

    return data