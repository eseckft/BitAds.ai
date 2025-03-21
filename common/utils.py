import os
import re
import socket
import time
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Callable, Any

import bittensor as bt
from common.helpers import const

from common.miner.schemas import VisitorSchema
from common.schemas.bitads import SystemLoad
from common.schemas.device import Device
from common.validator.schemas import ValidatorTrackingData


def execute_periodically(period: timedelta):
    """
    Decorator to execute a coroutine function periodically based on the specified period.

    Args:
        period (timedelta): The time interval between each execution of the decorated function.

    Returns:
        Callable: Decorated coroutine function.
    """
    def decorator(func):
        last_operation_date: Optional[datetime] = None

        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_operation_date
            if (
                not last_operation_date
                or datetime.now() - last_operation_date > period
            ):
                result = await func(*args, **kwargs)
                last_operation_date = datetime.now()
                return result
            else:
                bt.logging.debug(
                    f"Skipping {func.__name__}, period has not yet passed."
                )
                return None

        return wrapper

    return decorator


def determine_device(user_agent: str) -> Device:
    """
    Determines the device type based on the user agent string.

    Args:
        user_agent (str): User agent string extracted from HTTP headers.

    Returns:
        Device: The device type (PC or MOBILE) based on the user agent.
    """
    return (
        Device.MOBILE
        if re.search(r"Mobi|Android", user_agent, re.I)
        else Device.PC
    )


def get_load_average():
    """
    Retrieves the system load average as a tuple of three floating-point numbers (1-minute, 5-minute, 15-minute).

    Returns:
        tuple: System load average over the past 1 minute, 5 minutes, and 15 minutes.
    """
    return os.getloadavg()


def get_load_average_json():
    """
    Retrieves the system load average along with hostname and returns as a JSON serializable object.

    Returns:
        SystemLoad: System load information including timestamp, hostname, and load averages.
    """
    load1, load5, load15 = get_load_average()
    hostname = socket.gethostname()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return SystemLoad(
        timestamp=timestamp,
        hostname=hostname,
        load_average={"1min": load1, "5min": load5, "15min": load15},
    )


def verify_visit(
    miner_data: VisitorSchema, validator_data: ValidatorTrackingData
) -> bool:
    """
    Verifies if a visitor's data matches the validator's tracking data for a valid visit.

    Args:
        miner_data (VisitorSchema): Visitor data from the miner.
        validator_data (ValidatorTrackingData): Validator's tracking data for comparison.

    Returns:
        bool: True if the visit is valid (all data matches), False otherwise.
    """
    return (
        miner_data.user_agent == validator_data.user_agent
        and miner_data.campaign_id
        == (validator_data.campaign_id or miner_data.campaign_id)
        and miner_data.device == validator_data.device
        and miner_data.country == validator_data.country
        and miner_data.ip_address == validator_data.ip_address
        and 0 < miner_data.miner_block <= validator_data.validator_block
    )


def combine_dicts_with_avg(*dicts: Dict[str, float]) -> Dict[str, float]:
    """
    Combines multiple dictionaries by calculating the average value for each key.

    Args:
        *dicts (Dict[str, float]): Variable number of dictionaries to be combined.

    Returns:
        Dict[str, float]: Combined dictionary with keys and their average values.
    """
    combined_dict = defaultdict(float)
    count_dict = defaultdict(int)

    # Iterate over all dictionaries
    for d in dicts:
        for key, value in d.items():
            combined_dict[key] += value
            count_dict[key] += 1

    # Calculate the average for each key
    for key in combined_dict:
        combined_dict[key] /= count_dict[key]

    return combined_dict


def blocks_to_timedelta(blocks: int) -> timedelta:
    return timedelta(seconds=blocks * const.BLOCK_DURATION.total_seconds())


def timedelta_to_blocks(td: timedelta) -> int:
    return td.total_seconds() // const.BLOCK_DURATION.total_seconds()


def cache_result(expiration: timedelta):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache: dict[str, tuple[Any, float]] = {}

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Create a cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            current_time = time.time()

            # Check if we have a valid cached result
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < expiration.total_seconds():
                    return result

            # If no valid cache, execute the function
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            return result

        return wrapper

    return decorator