from datetime import timedelta

from bittensor import wallet

from clients.base import BitAdsClient, VersionClient
from clients.bit_ads import SyncBitAdsClient
from clients.user_content import GitHubUserContentVersionClient
from helpers.constants import Const
from services.ping.base import PingService
from services.ping.sync import SyncPingService
from services.storage.base import BaseStorage
from services.storage.file import FileStorage


def create_bitads_client(
    _wallet: wallet, base_url: str = Const.API_BITADS_DOMAIN
) -> BitAdsClient:
    return SyncBitAdsClient(
        base_url,
        hot_key=_wallet.get_hotkey().ss58_address,
        cold_key=_wallet.get_coldkeypub().ss58_address,
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
