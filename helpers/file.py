import os
import json
from helpers.constants.hint import Hint
from helpers.constants.const import Const
from helpers.constants.main import Main


class File:
    TYPE_VALIDATOR = "validator"
    TYPE_MINER = "miner"

    DIR_ROOT = "./bitads_campaigns"

    def create_dirs(self, type):
        directories = [
            self.DIR_ROOT,
            f"{self.DIR_ROOT}/{type}",
            f"{self.DIR_ROOT}/{type}/{Main.wallet_hotkey}",
            f"{self.DIR_ROOT}/{type}/{Main.wallet_hotkey}/campaign_id",
            f"{self.DIR_ROOT}/{type}/{Main.wallet_hotkey}/unique_link",
        ]

        if type == self.TYPE_VALIDATOR:
            directories.extend(
                [
                    f"{self.DIR_ROOT}/{type}/{Main.wallet_hotkey}/unique_link_score",
                    f"{self.DIR_ROOT}/{type}/{Main.wallet_hotkey}/unique_link_stats",
                ]
            )

        for path in directories:
            if not os.path.exists(path):
                os.makedirs(path)
                Hint(
                    Hint.COLOR_MAGENTA,
                    Const.LOG_TYPE_LOCAL,
                    f"Created directory: {path}",
                )

    def saveCampaign(self, wallet_address, type, task):
        path = (
            self.DIR_ROOT
            + "/"
            + type
            + "/"
            + wallet_address
            + "/campaign_id/"
            + task["product_unique_id"]
            + ".json"
        )
        with open(path, "w") as file:
            json.dump(task, file, indent=4)
            Hint(
                Hint.COLOR_YELLOW,
                Const.LOG_TYPE_LOCAL,
                "Save campaign to: " + path,
            )

    def removeCampaign(self, wallet_address, type, campaignId):
        path = (
            self.DIR_ROOT
            + "/"
            + type
            + "/"
            + wallet_address
            + "/campaign_id/"
            + campaignId
            + "_"
            + wallet_address
            + ".json"
        )
        if os.path.exists(path):
            os.remove(path)
            Hint(
                Hint.COLOR_YELLOW,
                Const.LOG_TYPE_LOCAL,
                "Remove campaign file: " + path,
            )

    def saveMinerUniqueUrl(self, owner, wallet_address, type, data):
        path = (
            self.DIR_ROOT
            + "/"
            + type
            + "/"
            + owner
            + "/unique_link/"
            + data["product_unique_id"]
            + "_"
            + wallet_address
            + ".json"
        )
        with open(path, "w") as file:
            json.dump(data, file, indent=4)
            Hint(
                Hint.COLOR_YELLOW,
                Const.LOG_TYPE_LOCAL,
                "Save campaign unique url to: " + path,
            )

    def saveMinerUniqueUrlStats(self, owner, uniqueUrl, type, data):
        path = (
            self.DIR_ROOT
            + "/"
            + type
            + "/"
            + owner
            + "/unique_link_stats/"
            + data["product_unique_id"]
            + "_"
            + uniqueUrl
            + ".json"
        )
        with open(path, "w") as file:
            json.dump(data, file, indent=4)
            Hint(
                Hint.COLOR_YELLOW,
                Const.LOG_TYPE_LOCAL,
                "Save campaign unique url statistics to: " + path,
            )

    def saveMinerUniqueUrlScore(self, owner, uniqueId, uniqueUrl, type, data):
        path = (
            self.DIR_ROOT
            + "/"
            + type
            + "/"
            + owner
            + "/unique_link_score/"
            + uniqueId
            + "_"
            + uniqueUrl
            + ".json"
        )
        with open(path, "w") as file:
            json.dump(data, file, indent=4)
            Hint(
                Hint.COLOR_YELLOW,
                Const.LOG_TYPE_LOCAL,
                "Save campaign unique url score to: " + path,
            )

    def unique_link_exists(self, owner, wallet_address, type, campaignId):
        path = (
            self.DIR_ROOT
            + "/"
            + type
            + "/"
            + owner
            + "/unique_link/"
            + campaignId
            + "_"
            + wallet_address
            + ".json"
        )
        if not os.path.exists(path):
            return False

        return True

    def getUniqueUrl(self, owner, wallet_address, type, campaignId):
        path = (
            self.DIR_ROOT
            + "/"
            + type
            + "/"
            + owner
            + "/unique_link/"
            + campaignId
            + "_"
            + wallet_address
            + ".json"
        )
        data = {}
        if os.path.exists(path):
            with open(path, "r") as file:
                data = json.load(file)

        return data

    @staticmethod
    def save_cc():
        path = f"./tmp/{Main.wallet_hotkey}.txt"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            json.dump(Main.wallet_coldkey, file, indent=4)

    @staticmethod
    def get_cc():
        try:
            with open(f"./tmp/{Main.wallet_hotkey}.txt", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return False
