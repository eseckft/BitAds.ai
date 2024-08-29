"""
Miner Environment Variables
"""
from datetime import timedelta
from os import environ


class Environ:
    """
    Configuration class for environment variables used in the miner application.

    Attributes:
        ACTIVE_DB_URL (str): URL for the active database. Defaults to "sqlite+aiosqlite:///miner_active.db".
        HISTORY_DB_URL (str): URL for the history database. Defaults to "sqlite+aiosqlite:///miner_history.db".
        PROXY_PORT (int): Port number for the proxy server. Defaults to 443.

        RECENT_ACTIVITY_DAYS (str): Number of days considered for recent activity. Defaults to "14".
        RECENT_ACTIVITY_COUNT (str): Maximum number of recent activities to retrieve. Defaults to "50".
        LIMIT_RECENT_ACTIVITY (str): Limit for recent activity retrieval. Defaults to "50".

        CLEAR_RECENT_ACTIVITY_PERIOD (timedelta): Period for clearing recent activity data. Defaults to 60 minutes.
        PING_PERIOD (timedelta): Period for sending ping signals. Defaults to 30 minutes.
        SYNC_VISITS_PERIOD (timedelta): Period for synchronizing visits. Defaults to 12 seconds.
    """

    ACTIVE_DB_URL: str = environ.get(
        "MINER_ACTIVE_DB_URL", "sqlite+aiosqlite:///miner_active.db"
    )
    HISTORY_DB_URL: str = environ.get(
        "MINER_HISTORY_DB_URL", "sqlite+aiosqlite:///miner_history.db"
    )
    PROXY_PORT: int = int(environ.get("MINER_PROXY_PORT", 443))

    RECENT_ACTIVITY_DAYS: int = int(environ.get("RECENT_ACTIVITY_DAYS", 14))
    RECENT_ACTIVITY_COUNT: int = int(environ.get("RECENT_ACTIVITY_COUNT", 50))
    LIMIT_RECENT_ACTIVITY: int = int(environ.get("LIMIT_RECENT_ACTIVITY", 50))

    CLEAR_RECENT_ACTIVITY_PERIOD: timedelta = timedelta(
        minutes=int(environ.get("CLEAR_RECENT_ACTIVITY_PERIOD", 60))
    )
    PING_PERIOD: timedelta = timedelta(
        minutes=int(environ.get("PING_PERIOD", 30))
    )
    SYNC_VISITS_PERIOD: timedelta = timedelta(
        seconds=int(environ.get("SYNC_VISITS_PERIOD", 12))
    )
