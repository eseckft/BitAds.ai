from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, distinct, func
from sqlalchemy.orm import Session

from common.validator.db.entities.active import MinerPing
from common.validator.schemas import MinerPingSchema


class MinerPingRepository:
    def __init__(self, session: Session):
        self.session = session

    async def add_miner_ping(self, hot_key: str, block: int):
        new_ping = MinerPing(hot_key=hot_key, block=block)
        self.session.add(new_ping)
        self.session.commit()
        return MinerPingSchema.model_validate(new_ping)

    async def get_miner_pings(
        self,
        hot_key: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[MinerPingSchema]:
        stmt = select(MinerPing)

        if hot_key:
            stmt = stmt.where(MinerPing.hot_key == hot_key)
        if start_time:
            stmt = stmt.where(MinerPing.created_at >= start_time)
        if end_time:
            stmt = stmt.where(MinerPing.created_at <= end_time)

        result = self.session.execute(stmt)
        return [
            MinerPingSchema.model_validate(p) for p in result.scalars().all()
        ]

    async def get_active_miners_count(
        self, from_block: int, to_block: int
    ) -> int:
        result = self.session.execute(
            select(func.count(distinct(MinerPing.hot_key))).where(
                MinerPing.block.between(from_block, to_block)
            )
        )
        return result.scalar()
