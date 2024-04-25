from datetime import timedelta
from typing import Tuple


class Const:
    API_BITADS_DOMAIN = "https://api.bitads.ai"
    GITHUB_USER_CONTENT_DOMAIN = "https://raw.githubusercontent.com"

    ROOT_DIR = "./bitads_campaigns"

    FOLDERS_TO_CHECK: Tuple[str] = (
        "./helpers",
        "./neurons",
    )
    VALIDATOR = "validator"
    MINER = "miner"

    # TODO: region move_to_config
    MINER_MINUTES_TIMEOUT_PING = timedelta(minutes=30)

    VALIDATOR_MINUTES_TIMEOUT_PING = timedelta(minutes=30)
    VALIDATOR_MINUTES_PROCESS_CAMPAIGN = timedelta(minutes=30)
    # endregion

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
