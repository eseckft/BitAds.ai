"""
Constants used throughout the application related to BitAds API, network identifiers,
time durations, and directories.

Constants:
    API_ERROR_CODES (dict): A dictionary mapping BitAds API error codes to their corresponding error messages.
    API_BITADS_DOMAIN (str): Base domain URL for the BitAds API.
    NETUIDS (dict): A dictionary mapping network names to their unique identifiers.
    BITADS_API_URLS (dict): A dictionary mapping network names to their corresponding BitAds API URLs.
    BLOCK_DURATION (timedelta): Duration of a block in seconds.
    DEFAULT_UVMAX (float): Default value for UVmax.
    RETURN_IN_SITE_DELTA (timedelta): Time duration indicating the delta for return visits to the site
        (uses for return in site deadline).
    ROOT_DIR (str): Root directory path for BitAds campaigns.
    TRACKING_DATA_DELTA (timedelta): Time duration for tracking data delta (uses for updated_at deadline).
"""

from datetime import timedelta

API_ERROR_CODES = {
    100: "Internal Server Error.",
    101: "You must register your account as a Miner or "
    "Validator on the BitAds website to mine or validate on Subnet 16. "
    "Visit https://bitads.ai and register.",
    102: "User Status Not Active.",
    103: "Not Active Campaign.",
    104: "Not Query Parameters.",
    105: "Not All Query Parameters.",
    106: "User is Not a Miner.",
    107: "Campaigns Not Found.",
    108: "COLD KEY is incorrect.",
    109: "HOT KEY or COLD KEY is not defined.",
}

API_BITADS_DOMAIN = "https://prod-s.a.bitads.ai"

NETUIDS = {"finney": 16, "test": 173, "local": 16}

BITADS_API_URLS = {
    "finney": API_BITADS_DOMAIN,
    "local": API_BITADS_DOMAIN,
    "test": "https://dev-s.a.bitads.ai",
}

BLOCK_DURATION = timedelta(seconds=12)

DEFAULT_UVMAX = 300.0

RETURN_IN_SITE_DELTA = timedelta(hours=1)

ROOT_DIR = "./bitads_campaigns"

TRACKING_DATA_DELTA = timedelta(seconds=20)

VERSION_KEY = 1725727158

REWARD_SALE_PERIOD = timedelta(days=30)

PING_PERIOD: timedelta = timedelta(minutes=30)
