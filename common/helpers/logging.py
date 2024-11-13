"""
Utility functions and classes for logging and colorizing text.

Functions:
    log_error(ex: Exception): Logs errors based on the exception type.
    log_errors(errors: List[int] = None): Logs multiple errors based on their error codes.
Classes:
    Color (Enum): Enumerates color options using ANSI escape codes from colorama.
    LogLevel: Defines constants for different logging levels.
"""

import functools
import logging
from enum import Enum
from typing import List

import bittensor as bt
import requests
from colorama import Style
from colorama.ansi import Fore

from common.helpers import const


class Color(Enum):
    """
    Enumeration of colors using ANSI escape codes from colorama.

    Attributes:
        RED: Red color.
        GREEN: Green color.
        YELLOW: Yellow color.
        BLUE: Blue color.
        MAGENTA: Magenta color.
        CYAN: Cyan color.
    """

    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN


def colorize(color: Color, text: str) -> str:
    """
    Applies the specified color to the given text.

    Args:
        color (Color): The color enumeration value.
        text (str): The text to be colorized.

    Returns:
        str: The colorized text.
    """
    return f"{color.value}{text}{Style.RESET_ALL}"


red = functools.partial(colorize, Color.RED)
green = functools.partial(colorize, Color.GREEN)
yellow = functools.partial(colorize, Color.YELLOW)
blue = functools.partial(colorize, Color.BLUE)
magenta = functools.partial(colorize, Color.MAGENTA)
cyan = functools.partial(colorize, Color.CYAN)


class LogLevel:
    """
    Constants representing different logging levels.

    Attributes:
        BITADS (str): BitAds related logging.
        LOCAL (str): Local logging.
        MINER (str): Miner related logging.
        VALIDATOR (str): Validator related logging.
    """

    BITADS = "BITADS"
    LOCAL = "LOCAL"
    MINER = "MINER"
    VALIDATOR = "VALIDATOR"


def log_error(ex: Exception) -> None:
    """
    Logs an error message based on the type of exception.

    Args:
        ex (Exception): The exception object.
    """
    # noinspection PyTypeChecker
    error_message = {
        requests.exceptions.HTTPError: "HTTP Error.",
        requests.exceptions.ConnectionError: "Error Connecting.",
        requests.exceptions.Timeout: "Timeout Error.",
        requests.exceptions.RequestException: "OOps: Something Else.",
        ValueError: "Invalid JSON received.",
    }.get(type(ex), "Unknown exception")
    bt.logging.error(prefix=LogLevel.BITADS, msg=red(error_message))


def log_errors(errors: List[int] = None) -> None:
    """
    Logs multiple error messages based on their error codes.

    Args:
        errors (List[int], optional): List of error codes to log.
    """
    errors = errors or []
    for error in errors:
        if error == 200:
            continue
        bt.logging.error(
            prefix=LogLevel.BITADS,
            msg=red(
                const.API_ERROR_CODES.get(
                    error, f"Unknown code error {error}"
                ),
            ),
        )


def log_startup(neuron_type: str):
    for color in (Color.BLUE, Color.YELLOW):
        bt.logging.info(
            prefix=LogLevel.LOCAL,
            msg=colorize(color, f"{neuron_type} running..."),
        )


class BittensorLoggingFilter(logging.Filter):

    def filter(self, record):
        return all(f not in record.getMessage() for f in ("TimeoutError", "ClientConnectorError", "ClientOSError"))
