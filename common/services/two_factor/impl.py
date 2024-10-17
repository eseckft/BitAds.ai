from typing import List

from common.db.database import DatabaseManager
from common.db.repositories import two_factor
from common.schemas.bitads import TwoFactorSchema, TwoFactorRequest
from common.services.two_factor.base import TwoFactorService


class TwoFactorServiceImpl(TwoFactorService):
    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager

    async def add_from_request(self, request: TwoFactorRequest):
        model = TwoFactorSchema(
            ip_address=str(request.ip_address),
            user_agent=request.user_agent,
            hotkey=request.hotkey,
            code=request.code
        )
        with self.database_manager.get_session("main") as session:
            two_factor.add_code(session, model)

    async def get_last_codes(self, limit: int = 5) -> List[TwoFactorSchema]:
        with self.database_manager.get_session("main") as session:
            return two_factor.get_last_codes(session, limit)
