from typing import List

from sqlalchemy import desc
from sqlalchemy.orm import Session

from common.db.entities import TwoFactorCodes
from common.schemas.bitads import TwoFactorSchema


def add_code(session: Session, code: TwoFactorSchema) -> None:
    entity = TwoFactorCodes(**code.model_dump())
    session.add(entity)


def get_last_codes(session: Session, limit: int = 5) -> List[TwoFactorSchema]:
    codes = (
        session.query(TwoFactorCodes)
        .order_by(desc(TwoFactorCodes.created_at))
        .limit(limit)
        .all()
    )

    return [TwoFactorSchema.model_validate(code) for code in codes]
