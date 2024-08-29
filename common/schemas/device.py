"""
Device common schemas
"""
from enum import IntEnum


class Device(IntEnum):
    """
    Enumeration representing different types of devices.

    Attributes:
        PC (int): Represents a personal computer.
        MOBILE (int): Represents a mobile device.

    Note:
        Each device type is associated with an integer value:
        - PC: 1
        - MOBILE: 2
    """

    PC = 1
    MOBILE = 2
