from enum import IntEnum
from typing import List, Any

import requests
from bittensor import logging

from helpers.constants import Const
from helpers.constants.colors import red, cyan, green, yellow
from schemas.bit_ads import Campaign, TaskResponse


logger = logging
logging.set_trace()


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
        # logger.setLevel(level)


def log_campaign_info(campaign: Campaign):
    logger.info(LogLevel.BITADS, "")
    logger.info(
        LogLevel.BITADS,
        cyan("    --------------------------"),
    )
    logger.info(LogLevel.BITADS, "")
    logger.info(
        LogLevel.BITADS,
        cyan(
            f"    Campaign unique id: {campaign.product_unique_id}",
        ),
    )
    logger.info(
        LogLevel.BITADS,
        cyan(
            f"    Campaign title: {campaign.product_title}",
        ),
    )
    logger.info(LogLevel.BITADS, "")
    logger.info(
        LogLevel.BITADS,
        cyan("    --------------------------"),
    )
    logger.info(
        LogLevel.BITADS,
        "Preparation for distribution of the campaign to miners.",
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
    logger.info(LogLevel.BITADS, red(error_message))


def log_errors(errors: List[Any] = None):
    errors = errors or []
    for error in errors:
        if error == 200:
            continue
        logger.info(
            LogLevel.BITADS,
            red(
                Const.API_ERROR_CODES.get(
                    error, "Unknown code error {}".format(error)
                ),
            ),
        )


def log_task(task: TaskResponse):
    if task.campaign:
        logger.info(
            LogLevel.BITADS,
            green(
                f"--> Received campaigns for distribution among miners: {len(task.campaign)}",
            ),
        )
    else:
        logger.info(
            LogLevel.BITADS,
            yellow("--> There are no active campaigns for work."),
        )

    if task.aggregation:
        logger.info(
            LogLevel.BITADS,
            green(
                f"Received tasks for assessing miners: {len(task.aggregation)}",
            ),
        )
    else:
        logger.info(
            LogLevel.BITADS,
            yellow(
                "--> There are no statistical data to establish the miners' rating.",
            ),
        )
