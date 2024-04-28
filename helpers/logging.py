from enum import IntEnum
from typing import List, Any

import bittensor as bt
import requests

from helpers.constants import Const
from helpers.constants.colors import red, cyan, green, yellow
from schemas.bit_ads import Campaign, TaskResponse

bt.logging.on()


class _LogLevel(IntEnum):
    BITADS = 21
    LOCAL = 22
    MINER = 23
    VALIDATOR = 24


# class LogLevel:
#     BITADS = 21
#     LOCAL = 22
#     MINER = 23
#     VALIDATOR = 24


class LogLevel:
    BITADS = "BITADS"
    LOCAL = "LOCAL"
    MINER = "MINER"
    VALIDATOR = "VALIDATOR"


# @lambda _: _()  # IIFE function call
# def _configure_logger():
#     for level in _LogLevel:
#         logging.addLevelName(level.value, level.name)
#     pass
# logging.addLevelName(level.value, level.name)
# bt.logging.setLevel(level)


def log_campaign_info(campaign: Campaign):
    bt.logging.info(prefix=LogLevel.BITADS, msg="")
    bt.logging.info(
        prefix=LogLevel.BITADS,
        msg=cyan("    --------------------------"),
    )
    bt.logging.info(prefix=LogLevel.BITADS, msg="")
    bt.logging.info(
        prefix=LogLevel.BITADS,
        msg=cyan(
            f"    Campaign unique id: {campaign.product_unique_id}",
        ),
    )
    bt.logging.info(
        prefix=LogLevel.BITADS,
        msg=cyan(
            f"    Campaign title: {campaign.product_title}",
        ),
    )
    bt.logging.info(prefix=LogLevel.BITADS, msg="")
    bt.logging.info(
        prefix=LogLevel.BITADS,
        msg=cyan("    --------------------------"),
    )
    bt.logging.info(
        prefix=LogLevel.BITADS,
        msg="Preparation for distribution of the campaign to miners.",
    )


def log_error(ex: Exception):
    # noinspection PyTypeChecker
    error_message = {
        requests.exceptions.HTTPError: "HTTP Error.",
        requests.exceptions.ConnectionError: "Error Connecting.",
        requests.exceptions.Timeout: "Timeout Error.",
        requests.exceptions.RequestException: "OOps: Something Else.",
        ValueError: "Invalid JSON received.",
    }.get(type(ex), "Unknown exception")
    bt.logging.error(prefix=LogLevel.BITADS, msg=red(error_message))


def log_errors(errors: List[Any] = None):
    errors = errors or []
    for error in errors:
        if error == 200:
            continue
        bt.logging.error(
            prefix=LogLevel.BITADS,
            msg=red(
                Const.API_ERROR_CODES.get(
                    error, "Unknown code error {}".format(error)
                ),
            ),
        )


def log_task(task: TaskResponse):
    if task.campaign:
        bt.logging.info(
            prefix=LogLevel.BITADS,
            msg=green(
                f"--> Received campaigns for distribution among miners: {len(task.campaign)}",
            ),
        )
    else:
        bt.logging.info(
            prefix=LogLevel.BITADS,
            msg=yellow("--> There are no active campaigns for work."),
        )

    if task.aggregation:
        bt.logging.info(
            prefix=LogLevel.BITADS,
            msg=green(
                f"Received tasks for assessing miners",
            ),
        )
    else:
        bt.logging.info(
            prefix=LogLevel.BITADS,
            msg=yellow(
                "--> There are no statistical data to establish the miners' rating.",
            ),
        )
