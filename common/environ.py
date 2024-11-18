import json
from os import environ


class Environ:
    """
    Configuration class for environment variables used in the Validator application.
    """

    GEO2_LITE_DB_PATH: str = environ.get("GEO2_LITE_DB_PATH", "GeoLite2-Country.mmdb")
    DB_URL_TEMPLATE: str = environ.get(
        "DB_URL_TEMPLATE", "sqlite:///{name}_{network}.db"
    )
    WALLET_NAME: str = environ.get("WALLET_NAME", "default")
    HOTKEY_NAME: str = environ.get("HOTKEY_NAME", "default")
    NETUID: int = int(environ["NETUID"])
    SUBTENSOR_NETWORK: str = environ.get("SUBTENSOR_NETWORK")
    SUBTENSOR_ADDRESS: str = environ.get("SUBTENSOR_ADDRESS")
    VALIDATORS: list = json.loads(environ.get("VALIDATORS", "[]"))
    MINERS: list = json.loads(environ.get("MINERS", "[]"))
    NEURON_TYPE: str = environ.get("NEURON_TYPE", "neuron")
    PROXY_PORT: int = int(environ.get("PROXY_PORT", 443))
