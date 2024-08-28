from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session


class UserAgentActivityRepository:
    def __init__(self, session: Session):
        self.session = session

    async def insert_or_update(self, user_agent: str, activity_date: date):
        stmt = text(
            """
            INSERT INTO user_agent_activity (user_agent, created_at, count)
            VALUES (:user_agent, :created_at, 1)
            ON CONFLICT(user_agent, created_at) DO UPDATE SET
            count = user_agent_activity.count + 1;
        """
        )
        self.session.execute(
            stmt, {"user_agent": user_agent, "created_at": activity_date}
        )
