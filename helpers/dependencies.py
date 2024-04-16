from datetime import timedelta

from bittensor import wallet

from clients.base import BitAdsClient, VersionClient
from clients.bit_ads import SyncBitAdsClient
from clients.user_content import GitHubUserContentVersionClient
from helpers.constants import Const
from helpers.logging import LogLevel, logger
from services.ping.base import PingService
from services.ping.sync import SyncPingService
from services.storage.base import BaseStorage
from services.storage.file import FileStorage
from helpers.constants.colors import red


def create_bitads_client(
    _wallet: wallet, base_url: str = Const.API_BITADS_DOMAIN
) -> BitAdsClient:
    temp_hot_key = _wallet.get_hotkey().ss58_address
    temp_cold_key = 'pass'
    # temp_cold_key = FileStorage.get_cold_key(temp_hot_key)

    # while not temp_cold_key:
    #     if not temp_cold_key:
    #         logger.info(
    #             LogLevel.LOCAL,
    #             red(
    #                 "Please note that you will be required to enter your password only once to verify the ownership of your coldkey. This is a necessary step to ensure secure access and to enable full interaction with the BitAds API. Your password is not stored and will not be requested again for future sessions."
    #             ),
    #         )
    #         temp_cold_key = _wallet.coldkey.ss58_address
    #         FileStorage.save_cold_key(temp_hot_key, temp_cold_key)
    #
    #         if temp_cold_key:
    #             break
    #         else:
    #             temp_cold_key = False

    return SyncBitAdsClient(
        base_url,
        hot_key=temp_hot_key,
        cold_key=temp_cold_key,
    )


def create_storage(neuron_type: str, _wallet: wallet) -> BaseStorage:
    return FileStorage(neuron_type, _wallet.get_hotkey().ss58_address)


def create_version_client(
    base_url: str = Const.GITHUB_USER_CONTENT_DOMAIN,
) -> VersionClient:
    return GitHubUserContentVersionClient(base_url)


def create_ping_service(
    bitads_client: BitAdsClient,
    version_client: VersionClient,
    timeout_ping: timedelta,
) -> PingService:
    return SyncPingService(bitads_client, version_client, timeout_ping)
