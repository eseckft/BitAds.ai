from datetime import date, datetime, timedelta
from typing import List

from sqlalchemy import text, select
from sqlalchemy.orm import Session

from common.miner.db.entities.active import VisitorActivity
from common.miner.schemas import VisitorActivitySchema


class VisitorActivityRepository:
    def __init__(
        self,
        session: Session,
        recent_activity_days: int,
        recent_activity_count: int,
        recent_activity_limit: int,
    ):
        self.recent_activity_limit = recent_activity_limit
        self.recent_activity_days = recent_activity_days
        self.recent_activity_count = recent_activity_count
        self.session = session

    async def insert_or_update(self, ip: str, activity_date: date):
        stmt = text(
            """
            INSERT INTO visitor_activity (ip, created_at, count)
            VALUES (:ip, :created_at, 1)
            ON CONFLICT(ip, created_at) DO UPDATE SET
            count = visitor_activity.count + 1;
        """
        )
        self.session.execute(stmt, {"ip": ip, "created_at": activity_date})

    async def get_recent_activity(
        self, recent_activity_count: int, limit: int
    ) -> List[VisitorActivitySchema]:
        recent_activity_count = recent_activity_count or self.recent_activity_count
        limit = limit or self.recent_activity_limit
        recent_date = datetime.utcnow().date() - timedelta(
            days=self.recent_activity_days
        )
        # Include the 'created_at' field with an alias 'date'
        stmt = (
            select(VisitorActivity, VisitorActivity.created_at.label("date"))
            .where(
                VisitorActivity.created_at >= recent_date,
                VisitorActivity.count >= recent_activity_count,
            )
            .order_by(VisitorActivity.count.desc())
            .limit(limit)
        )

        result = self.session.execute(stmt)

        return [
            VisitorActivitySchema.model_validate(
                {
                    **o[0].__dict__,  # the VisitorActivity model instance
                    "date": o.date,  # the aliased 'created_at' column
                }
            )
            for o in result.all()
        ]

    async def clean_old_data(self):
        cutoff_date = datetime.utcnow().date() - timedelta(
            days=self.recent_activity_days
        )
        self.session.execute(
            text("DELETE FROM visitor_activity WHERE created_at < :cutoff_date"),
            {"cutoff_date": cutoff_date},
        )
