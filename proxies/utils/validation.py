from typing import Annotated, Optional

from bitads_security.checkers import check_hash
from fastapi import Header, Query, HTTPException, status


def validate_hash(
    x_unique_id: Annotated[Optional[str], Header()] = "",
    x_signature: Annotated[Optional[str], Header()] = "",
    campaign_id: str = "",
    body: dict = None,
    sep: Annotated[str, Query(include_in_schema=False)] = "",
) -> None:
    if not check_hash(x_unique_id, x_signature, campaign_id, body, sep):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
