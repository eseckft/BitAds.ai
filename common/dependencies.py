from typing import Annotated

import bittensor as bt
from fastapi import Depends

import template
from common.clients.bitads.base import BitAdsClient
from common.clients.bitads.impl import SyncBitAdsClient

from common.db.database import Database, DatabaseManager
from common.environ import Environ
from common.helpers import const
from common.services.bitads.base import BitAdsService
from common.services.bitads.impl import BitAdsServiceImpl
from common.services.campaign.base import CampaignService
from common.services.campaign.impl import CampaignServiceImpl
from common.services.geoip.base import GeoIpService
from common.services.geoip.impl import GeoIpServiceImpl
from common.services.storage.base import BaseStorage
from common.services.storage.file import FileStorage
from common.services.two_factor.base import TwoFactorService
from common.services.two_factor.impl import TwoFactorServiceImpl


def get_main_db(db_url: str) -> Database:
    """
    Initializes and returns the main database connection object.

    Args:
        db_url (str): URL string specifying the database connection details.

    Returns:
        Database: Initialized Database object connected to the specified DB URL.

    Raises:
        None

    Notes:
        This function is used to obtain the main database connection, typically used as a dependency in FastAPI.
    """
    return Database(db_url)


def get_geo_ip_service() -> GeoIpService:
    """
    Creates and returns a GeoIP service instance.

    Returns:
        GeoIpService: Initialized GeoIpService implementation using Environ.GEO2_LITE_DB_PATH.

    Raises:
        None

    Notes:
        This function initializes GeoIpServiceImpl with the path to the GeoIP Lite database.
    """
    return GeoIpServiceImpl(Environ.GEO2_LITE_DB_PATH)


def get_database_manager(neuron_type: str, subtensor_network: str) -> DatabaseManager:
    """
    Creates and returns a DatabaseManager instance configured with the specified neuron type and Subtensor network.

    Args:
        neuron_type (str): Type or category of the neuron.
        subtensor_network (str): Subtensor network identifier.

    Returns:
        DatabaseManager: Initialized DatabaseManager instance configured for the specified neuron type and network.

    Raises:
        None

    Notes:
        This function initializes a DatabaseManager instance for managing database connections based on the provided parameters.
    """
    return DatabaseManager(neuron_type, subtensor_network)


def get_bitads_service(
    database_manager: Annotated[DatabaseManager, Depends(get_database_manager)]
) -> BitAdsService:
    return BitAdsServiceImpl(database_manager)


def create_bitads_client(
    wallet: bt.wallet, base_url: str = const.API_BITADS_DOMAIN
) -> BitAdsClient:
    """
    Creates a BitAds client instance configured with the provided wallet and base URL.

    Args:
        wallet (bt.wallet): Wallet object used to obtain the hotkey for authentication.
        base_url (str, optional): Base URL of the BitAds API. Defaults to const.API_BITADS_DOMAIN.

    Returns:
        BitAdsClient: Initialized BitAds client instance.

    Raises:
        None

    Notes:
        The function uses the wallet's hotkey address obtained via `wallet.get_hotkey().ss58_address`.
        It initializes a SyncBitAdsClient with the provided base URL, hotkey, and template version.
    """
    return create_bitads_client_from_hotkey(wallet.get_hotkey().ss58_address, base_url)


def create_bitads_client_from_hotkey(
    hotkey: str, base_url: str = const.API_BITADS_DOMAIN
) -> BitAdsClient:
    """
    Creates a BitAds client instance configured with the provided wallet and base URL.

    Args:
        wallet (bt.wallet): Wallet object used to obtain the hotkey for authentication.
        base_url (str, optional): Base URL of the BitAds API. Defaults to const.API_BITADS_DOMAIN.

    Returns:
        BitAdsClient: Initialized BitAds client instance.

    Raises:
        None

    Notes:
        The function uses the wallet's hotkey address obtained via `wallet.get_hotkey().ss58_address`.
        It initializes a SyncBitAdsClient with the provided base URL, hotkey, and template version.
    """
    return SyncBitAdsClient(
        base_url,
        hot_key=hotkey,
        v=template.__version__,
    )


def get_subtensor(network: str) -> bt.subtensor:
    """
    Initializes and returns a Subtensor client instance for the specified network.

    Args:
        network (str): Network identifier string.

    Returns:
        bt.subtensor: Initialized Subtensor client instance for the specified network.

    Raises:
        None

    Notes:
        This function initializes a Subtensor client with the provided network string.
    """
    return bt.subtensor(network)


def get_wallet(name: str, hotkey: str) -> bt.wallet:
    """
    Creates and returns a wallet object initialized with the provided name and hotkey.

    Args:
        name (str): Name or identifier of the wallet.
        hotkey (str): Hotkey address associated with the wallet.

    Returns:
        bt.wallet: Initialized wallet object with the specified name and hotkey.

    Raises:
        None

    Notes:
        This function initializes a wallet object using the BitTensor library with the provided parameters.
    """
    return bt.wallet(name, hotkey)


def get_storage(neuron_type: str, wallet: bt.wallet) -> BaseStorage:
    """
    Creates and returns a storage service instance based on the neuron type and wallet.

    Args:
        neuron_type (str): Type or category of the neuron.
        wallet (bt.wallet): Wallet object used for obtaining the hotkey.

    Returns:
        BaseStorage: Initialized storage service instance.

    Raises:
        None

    Notes:
        This function initializes a FileStorage instance with the neuron type and the wallet's hotkey address.
    """
    return FileStorage(neuron_type, wallet.get_hotkey().ss58_address)


def get_campaign_service(database_manager: DatabaseManager) -> CampaignService:
    return CampaignServiceImpl(database_manager)


def get_two_factor_service(database_manager: DatabaseManager) -> TwoFactorService:
    return TwoFactorServiceImpl(database_manager)
