import json
from os import environ


class Environ:
    """
    Configuration class for environment variables used in the Validator application.

    Attributes:
        MAIN_DB_URL (str): URL for the main database. Defaults to 'sqlite+aiosqlite:///main.db'.
        GEO2_LITE_DB_PATH (str): File path for GeoLite2 country database. Defaults to 'GeoLite2-Country.mmdb'.
        DB_URL_TEMPLATE (str): Template string for generating database URLs based on name and network.
                               Defaults to 'sqlite:///{name}_{network}.db'.
        SUBTENSOR_NETWORK (str): Identifier for the Subtensor network. Defaults to 'finney'.
        WALLET_NAME (str, optional): Name or identifier of the wallet. Defaults to None.
        WALLET_HOTKEY (str, optional): Hotkey address associated with the wallet. Defaults to None.
        VALIDATORS (list): List of validators parsed from environment variables as a JSON array.
                           Defaults to an empty list ([]).
        MINERS (list): List of miners parsed from environment variables as a JSON array.
                       Defaults to an empty list ([]).
    """
    MAIN_DB_URL: str = environ.get("MAIN_DB_URL", "sqlite+aiosqlite:///main.db")
    GEO2_LITE_DB_PATH: str = environ.get("GEO2_LITE_DB_PATH", "GeoLite2-Country.mmdb")
    DB_URL_TEMPLATE: str = environ.get("DB_URL_TEMPLATE", "sqlite:///databases/{name}_{network}.db")
    SUBTENSOR_NETWORK: str = environ.get("SUBTENSOR_NETWORK", "finney")
    WALLET_NAME: str = environ.get("WALLET_NAME")
    WALLET_HOTKEY: str = environ.get("WALLET_HOTKEY")
    VALIDATORS: list = json.loads(environ.get("VALIDATORS", "[]"))
    MINERS: list = json.loads(environ.get("MINERS", "[]"))
    NEURON_TYPE = environ.get("NEURON_TYPE", "neuron")
