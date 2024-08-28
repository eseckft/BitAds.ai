"""
Repository function for inserting or updating user agent activity records in the database.
"""

from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session


def insert_or_update(session: Session, user_agent: str, activity_date: date):
    """
    Inserts or updates user agent activity records in the database.

    Args:
        session (Session): The SQLAlchemy session object.
        user_agent (str): The user agent string.
        activity_date (date): The date of the user agent activity.

    """
    stmt = text(
        """
        INSERT INTO user_agent_activity (user_agent, created_at, count)
        VALUES (:user_agent, :created_at, 1)
        ON CONFLICT(user_agent, created_at) DO UPDATE SET
        count = user_agent_activity.count + 1;
    """
    )
    session.execute(
        stmt, {"user_agent": user_agent, "created_at": activity_date}
    )
