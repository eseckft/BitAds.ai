from enum import IntEnum
from typing import List, Any

import requests
from bittensor.btlogging import logger

from helpers.constants import colorize, Color, Const
from helpers.constants.colors import colorize, Color
from schemas.bit_ads import Campaign


class LogLevel(IntEnum):
    BITADS = 21
    LOCAL = 22
    MINER = 23
    VALIDATOR = 24


@lambda _: _()  # IIFE function call
def _configure_logger():
    for level in LogLevel:
        logger.level(level.name, level.value)


def log_campaign_info(campaign: Campaign):
    logger.log(LogLevel.BITADS.name, "")
    logger.log(
        LogLevel.BITADS.name,
        colorize(Color.CYAN, "    --------------------------"),
    )
    logger.log(LogLevel.BITADS.name, "")
    logger.log(
        LogLevel.BITADS.name,
        colorize(
            Color.CYAN,
            f"    Campaign unique id: {campaign.product_unique_id}",
        ),
    )
    logger.log(
        LogLevel.BITADS.name,
        colorize(
            Color.CYAN,
            f"    Campaign title: {campaign.product_title}",
        ),
    )
    logger.log(LogLevel.BITADS.name, "")
    logger.log(
        LogLevel.BITADS.name,
        colorize(Color.CYAN, "    --------------------------"),
    )
    logger.log(
        LogLevel.BITADS.name,
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
    logger.log(LogLevel.BITADS.name, colorize(Color.RED, error_message))


def log_errors(errors: List[Any] = None):
    errors = errors or []
    for error in errors:
        if error == 200:
            continue
        logger.log(
            LogLevel.BITADS.name,
            colorize(
                Color.RED,
                Const.API_ERROR_CODES.get(
                    error, "Unknown code error {}".format(error)
                ),
            ),
        )
