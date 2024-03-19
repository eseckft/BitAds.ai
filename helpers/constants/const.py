from typing import Tuple


class Const:
    API_BITADS_DOMAIN = "https://api.bitads.ai/"

    LOG_TYPE_BITADS = "BITADS"
    LOG_TYPE_LOCAL = "LOCAL"
    LOG_TYPE_MINER = "MINER"
    LOG_TYPE_VALIDATOR = "VALIDATOR"

    FOLDERS_TO_CHECK: Tuple[str] = (
        "./helpers",
        "./neurons",
    )

    # TODO: region move_to_config
    MINER_MINUTES_TIMEOUT_PING = 10

    VALIDATOR_MINUTES_TIMEOUT_PING = 10
    VALIDATOR_MINUTES_PROCESS_CAMPAIGN = 10
    # endregion

    API_ERROR_CODES = {
        100: "Internal Server Error.",
        101: "User Not Found.",
        102: "User Status Not Active.",
        103: "Not Active Campaign.",
        104: "Not Query Parameters.",
        105: "Not All Query Parameters.",
        106: "User is Not a Miner.",
        107: "Campaigns Not Found.",
        108: "COLD KEY is incorrect.",
        109: "HOT KEY or COLD KEY is not defined.",
    }
