"""
Campaign common schemas
"""
from enum import IntEnum


class CampaignType(IntEnum):
    """
    Enumeration representing different types of campaigns.

    Attributes:
        REGULAR (int): Regular campaign type with a value of 1.
        CPA (int): CPA (Cost Per Action) campaign type with a value of 2.
    """
    REGULAR = 0
    CPA = 1
