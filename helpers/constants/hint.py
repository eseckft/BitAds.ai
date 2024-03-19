from datetime import datetime
from helpers.constants.const import Const


class Hint:
    M = {
        1: "Miner running...",
        2: "Please note that you will be required to enter your password only once to verify the ownership of your coldkey. This is a necessary step to ensure secure access and to enable full interaction with the BitAds API. Your password is not stored and will not be requested again for future sessions.",
        3: "An error occurred, please try again.",
    }

    V = {
        1: "Validator running...",
        2: "Please note that you will be required to enter your password only once to verify the ownership of your coldkey. This is a necessary step to ensure secure access and to enable full interaction with the BitAds API. Your password is not stored and will not be requested again for future sessions.",
        3: "An error occurred, please try again.",
    }

    LOG_TEXTS = {
        1: "Miner running...",
        3: "Initiating ping to the server to update the activity timestamp.",
        4: "Ping successful. Activity timestamp updated.",
        2: "Validator running...",
        5: "I'm making a request to the server to get a campaign allocation task for miners.",
        6: "Received a task to distribute the campaign to miners.",
        7: "Received a task to evaluate the miner.",
        8: "Received campaigns for distribution among miners: ",
        9: "Received tasks for assessing miners: ",
        10: "The miner submitted his unique link to the campaign. ",
        11: "Didn't get a response from the miner. I will try next time. ",
        12: "The miner already has a unique link for this campaign. Pinging. ",
    }

    COLOR_RED = "\033[91m"
    COLOR_GREEN = "\033[92m"
    COLOR_YELLOW = "\033[93m"
    COLOR_BLUE = "\033[94m"
    COLOR_MAGENTA = "\033[95m"
    COLOR_CYAN = "\033[96m"
    COLOR_WHITE = "\033[97m"
    COLOR_RESET = "\033[0m"

    # in - 1, out - 2, none = 0
    def __init__(self, color, title, text, request_type=0):
        time_value = datetime.now().strftime("%Y-%m-%m %H:%M:%S.%f")[:-3]
        centered_title = title.center(16)

        text = self.get_request_type_string(request_type, text)
        text = self.set_color_string(color, text)

        print(time_value + " | " + centered_title + " | " + text)

    @staticmethod
    def get_request_type_string(request_type, text):
        if request_type == 1:
            text = "--> " + text
        elif request_type == 2:
            text = "<-- " + text
        else:
            text = "--- " + text

        return text

    @staticmethod
    def set_color_string(color, text):
        return color + text + Hint.COLOR_RESET

    @staticmethod
    def print_campaign_info(campaign):
        Hint(Hint.COLOR_CYAN, Const.LOG_TYPE_BITADS, "    ")
        Hint(
            Hint.COLOR_CYAN,
            Const.LOG_TYPE_BITADS,
            "    --------------------------",
        )
        Hint(Hint.COLOR_CYAN, Const.LOG_TYPE_BITADS, "    ")
        Hint(
            Hint.COLOR_CYAN,
            Const.LOG_TYPE_BITADS,
            "    Campaign unique id: " + campaign["product_unique_id"],
        )
        Hint(
            Hint.COLOR_CYAN,
            Const.LOG_TYPE_BITADS,
            "    Campaign title: " + campaign["product_title"],
        )
        Hint(Hint.COLOR_CYAN, Const.LOG_TYPE_BITADS, "    ")
        Hint(
            Hint.COLOR_CYAN,
            Const.LOG_TYPE_BITADS,
            "    --------------------------",
        )
        Hint(
            Hint.COLOR_WHITE,
            Const.LOG_TYPE_BITADS,
            "Preparation for distribution of the campaign to miners.",
        )
