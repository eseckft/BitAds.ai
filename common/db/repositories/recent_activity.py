"""
Repository function for inserting or updating visitor activity records in the database.
"""

from datetime import date, datetime, timedelta
from typing import List

from sqlalchemy import text, select
from sqlalchemy.orm import Session

from common.miner.db.entities.active import VisitorActivity
from common.miner.schemas import VisitorActivitySchema


def insert_or_update(session: Session, ip: str, activity_date: date):
    """
    Inserts or updates visitor activity records in the database.

    Args:
        session (Session): The SQLAlchemy session object.
        ip (str): The IP address of the visitor.
        activity_date (date): The date of the visitor activity.

    """
    stmt = text(
        """
        INSERT INTO visitor_activity (ip, created_at, count)
        VALUES (:ip, :created_at, 1)
        ON CONFLICT(ip, created_at) DO UPDATE SET
        count = visitor_activity.count + 1;
    """
    )
    session.execute(stmt, {"ip": ip, "created_at": activity_date})


def clean_old_data(session: Session, recent_activity_days: int):
    cutoff_date = datetime.utcnow().date() - timedelta(
        days=recent_activity_days
    )
    session.execute(
        text("DELETE FROM visitor_activity WHERE created_at < :cutoff_date"),
        {"cutoff_date": cutoff_date},
    )


def get_recent_activity(
    session: Session,
    recent_activity_count: int,
    limit: int,
    recent_activity_days: int,
) -> List[VisitorActivitySchema]:
    recent_activity_count = recent_activity_count
    limit = limit
    recent_date = datetime.utcnow().date() - timedelta(
        days=recent_activity_days
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

    result = session.execute(stmt)

    return [
        VisitorActivitySchema.model_validate(
            {
                **o[0].__dict__,  # the VisitorActivity model instance
                "date": o.date,  # the aliased 'created_at' column
            }
        )
        for o in result.all()
    ]
