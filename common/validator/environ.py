from datetime import timedelta
from os import environ

from common.helpers import const


class Environ:
    """
    Configuration class for environment variables used in the Validator application.

    Attributes:
        ACTIVE_DB_URL (str): The URL for the active database. Defaults to 'sqlite+aiosqlite:///validator_active.db'.
        HISTORY_DB_URL (str): The URL for the history database. Defaults to 'sqlite+aiosqlite:///validator_history.db'.
        PROXY_PORT (int): The port number for the proxy server. Defaults to 443.
        PING_PERIOD (timedelta): The period between miner pings, as a timedelta. Defaults to 30 minutes.
        PING_MINERS_N (int): The number of miners to ping. Defaults to 25.
        CALCULATE_UMAX_BLOCK_N (int): Number of blocks to consider when calculating UMAX. Defaults to 80.
        CALCULATE_UMAX_HOURS (timedelta): Number of hours to consider when calculating UMAX, as a timedelta.
                                          Defaults to 48 hours.
        CALCULATE_UMAX_BLOCKS (int): Number of blocks corresponding to CALCULATE_UMAX_HOURS, based on block duration.
        REFUND_DAYS (timedelta): Number of days for refund eligibility, as a timedelta. Defaults to 14 days.
        CPA_BLOCKS (int): Number of blocks corresponding to REFUND_DAYS, based on block duration.
        MR_DAYS (timedelta): Number of days to retain data for miner reputation evaluation, as a timedelta. Defaults to 30 days.
        MR_BLOCKS (int): Number of blocks corresponding to MR_DAYS, based on block duration.
        EVALUATE_MINERS_BLOCK_N (int): Number of blocks to consider when evaluating miners. Defaults to 100.
    """

    ACTIVE_DB_URL: str = environ.get(
        "VALIDATOR_ACTIVE_DB_URL", "sqlite+aiosqlite:///validator_active.db"
    )
    HISTORY_DB_URL: str = environ.get(
        "VALIDATOR_HISTORY_DB_URL", "sqlite+aiosqlite:///validator_history.db"
    )
    PROXY_PORT: int = int(environ.get("VALIDATOR_PROXY_PORT", 8443))
    PING_PERIOD: timedelta = timedelta(
        minutes=int(environ.get("PING_PERIOD", 30))
    )
    PING_MINERS_N: int = int(environ.get("PING_MINERS_N", 25))
    CALCULATE_UMAX_BLOCK_N: int = int(
        environ.get("CALCULATE_UMAX_BLOCK_N", 80)
    )
    CALCULATE_UMAX_HOURS: timedelta = timedelta(
        hours=int(environ.get("CALCULATE_UMAX_HOURS", 48))
    )
    CALCULATE_UMAX_BLOCKS: int = int(
        CALCULATE_UMAX_HOURS.total_seconds()
        / const.BLOCK_DURATION.total_seconds()
    )
    REFUND_DAYS: timedelta = timedelta(
        days=int(environ.get("REFUND_DAYS", 14))
    )
    CPA_BLOCKS: int = int(
        REFUND_DAYS.total_seconds() / const.BLOCK_DURATION.total_seconds()
    )
    MR_DAYS: timedelta = timedelta(days=int(environ.get("MR_DAYS", 30)))
    MR_BLOCKS: int = int(
        MR_DAYS.total_seconds() / const.BLOCK_DURATION.total_seconds()
    )
    EVALUATE_MINERS_BLOCK_N: int = int(
        environ.get("EVALUATE_MINERS_BLOCK_N", 100)
    )
