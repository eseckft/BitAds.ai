import os
import hashlib
import requests

from helpers.constants.hint import Hint
from helpers.constants.const import Const


class Request:
    folders_to_check = ["./helpers", "./neurons"]

    def print_errors(self, errors):
        if len(errors) != 0:
            for error in errors:
                if error != 200:
                    Hint(
                        Hint.COLOR_RED,
                        Const.LOG_TYPE_BITADS,
                        Const.API_ERROR_CODES.get(
                            error, "Unknown code error {}".format(error)
                        ),
                        0,
                    )

    def ping(self, hot_key, cold_key):
        print(
            "request hash example: ",
            self.calculate_md5_for_files_in_folders(self.folders_to_check),
        )

        url = Const.API_BITADS_DOMAIN + "subnetPing"
        response_data = {}
        try:
            response = requests.get(
                url, headers={"hot_key": hot_key, "cold_key": cold_key}
            )
            response_data = response.json()
            if len(response_data["errors"]) != 0:
                for error in response_data["errors"]:
                    if error != 200:
                        Hint(
                            Hint.COLOR_RED,
                            Const.LOG_TYPE_BITADS,
                            Const.API_ERROR_CODES.get(
                                error, "Unknown code error {}".format(error)
                            ),
                        )

        except requests.exceptions.HTTPError as errh:
            Hint(
                Hint.COLOR_RED,
                Const.LOG_TYPE_BITADS,
                "Http Error. " + str(errh),
            )

        return response_data

    def getTask(self, hot_key, cold_key):
        url = Const.API_BITADS_DOMAIN + "getTask"

        try:
            response = requests.get(
                url, headers={"hot_key": hot_key, "cold_key": cold_key}
            )
            response_data = response.json()

            if len(response_data["errors"]) != 0:
                for error in response_data["errors"]:
                    if error != 200:
                        Hint(
                            Hint.COLOR_RED,
                            Const.LOG_TYPE_BITADS,
                            Const.API_ERROR_CODES.get(
                                error, "Unknown code error {}".format(error)
                            ),
                        )

            return response_data

        except requests.exceptions.HTTPError as errh:
            Hint(Hint.COLOR_RED, Const.LOG_TYPE_BITADS, "Http Error.")
        except requests.exceptions.ConnectionError as errc:
            Hint(Hint.COLOR_RED, Const.LOG_TYPE_BITADS, "Error Connecting.")
        except requests.exceptions.Timeout as errt:
            Hint(Hint.COLOR_RED, Const.LOG_TYPE_BITADS, "Timeout Error.")
        except requests.exceptions.RequestException as err:
            Hint(
                Hint.COLOR_RED, Const.LOG_TYPE_BITADS, "OOps: Something Else."
            )
        except ValueError:
            Hint(
                Hint.COLOR_RED, Const.LOG_TYPE_BITADS, "Invalid JSON received."
            )

        return False

    #
    def getMinerUniqueId(self, campaignId, hot_key, cold_key):
        url = (
            Const.API_BITADS_DOMAIN
            + "getGenerateMinerCampaignUrl?"
            + campaignId
        )

        try:
            response = requests.get(
                url, headers={"hot_key": hot_key, "cold_key": cold_key}
            )
            response.raise_for_status()
            response_data = response.json()

            if len(response_data["errors"]) != 0:
                for error in response_data["errors"]:
                    if error != 200:
                        Hint(
                            Hint.COLOR_RED,
                            Const.LOG_TYPE_BITADS,
                            Const.API_ERROR_CODES.get(
                                error, "Unknown code error {}".format(error)
                            ),
                        )
            else:
                return response_data

        except requests.exceptions.HTTPError as errh:
            Hint(Hint.COLOR_RED, Const.LOG_TYPE_BITADS, "Http Error.")
        except requests.exceptions.ConnectionError as errc:
            Hint(Hint.COLOR_RED, Const.LOG_TYPE_BITADS, "Error Connecting.")
        except requests.exceptions.Timeout as errt:
            Hint(Hint.COLOR_RED, Const.LOG_TYPE_BITADS, "Timeout Error.")
        except requests.exceptions.RequestException as err:
            Hint(
                Hint.COLOR_RED, Const.LOG_TYPE_BITADS, "OOps: Something Else."
            )
        except ValueError:
            Hint(
                Hint.COLOR_RED, Const.LOG_TYPE_BITADS, "Invalid JSON received."
            )

        return False

    def getV(self):
        url = "https://raw.githubusercontent.com/eseckft/BitAds.ai/master/info/version.txt"
        response = requests.get(url)
        return response.text

    def md5(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def calculate_md5_for_files_in_folders(self, folders):
        md5 = ""

        for folder in folders:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    md5_hash = self.md5(file_path)
                    md5 = md5 + md5_hash

        hash_md5 = hashlib.md5()
        hash_md5.update(md5.encode("utf-8"))
        return hash_md5.hexdigest()
