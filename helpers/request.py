from typing import List, Any, Dict

import requests

from helpers import md5_utils
from helpers.constants.const import Const
from helpers.constants.hint import Hint


def print_errors(errors: List[Any] = None):
    errors = errors or []
    for error in errors:
        if error == 200:
            continue
        Hint(
            Hint.COLOR_RED,
            Const.LOG_TYPE_BITADS,
            Const.API_ERROR_CODES.get(
                error, "Unknown code error {}".format(error)
            ),
            0,
        )


def process_error(ex: Exception):
    # noinspection PyTypeChecker
    error_message = {
        requests.exceptions.HTTPError: "HTTP Error.",
        requests.exceptions.ConnectionError: "Error Connecting.",
        requests.exceptions.Timeout: "Timeout Error.",
        requests.exceptions.RequestException: "OOps: Something Else.",
        ValueError: "Invalid JSON received.",
    }.get(type(ex), "Unknown exception")
    Hint(Hint.COLOR_RED, Const.LOG_TYPE_BITADS, error_message)


class Request:
    def ping(self, hot_key, cold_key):
        print(
            "request hash example: ",
            md5_utils.calculate_md5_for_files_in_folders(
                Const.FOLDERS_TO_CHECK
            ),
        )

        url = Const.API_BITADS_DOMAIN + "subnetPing"
        response_data: Dict[str, Any] = {}
        try:
            response = requests.get(
                url, headers={"hot_key": hot_key, "cold_key": cold_key}
            )
            response_data = response.json()
            print_errors(response_data.get("errors"))
        except requests.exceptions.HTTPError as errh:
            Hint(
                Hint.COLOR_RED,
                Const.LOG_TYPE_BITADS,
                "Http Error. " + str(errh),
            )
        return response_data

    def get_task(self, hot_key, cold_key):
        url = Const.API_BITADS_DOMAIN + "getTask"

        try:
            response = requests.get(
                url, headers={"hot_key": hot_key, "cold_key": cold_key}
            )
            response_data = response.json()

            print_errors(response_data.get("errors"))
            return response_data
        except Exception as e:
            process_error(e)

        return False

    #
    def get_miner_unique_id(self, campaign_id, hot_key, cold_key):
        url = f"{Const.API_BITADS_DOMAIN}getGenerateMinerCampaignUrl?{campaign_id}"

        try:
            response = requests.get(
                url, headers={"hot_key": hot_key, "cold_key": cold_key}
            )
            response.raise_for_status()
            response_data = response.json()

            return (
                response_data
                if response_data.get("errors")
                else print_errors(response_data["errors"])
            )
        except Exception as e:
            process_error(e)

    def getV(self):
        url = "https://raw.githubusercontent.com/eseckft/BitAds.ai/master/info/version.txt"
        response = requests.get(url)
        return response.text
