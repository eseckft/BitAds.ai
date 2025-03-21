from abc import ABC, abstractmethod
from typing import Any


class MetagraphService(ABC):
    @abstractmethod
    async def get_axon_data(self, hotkey: str, ip_address: str = None, coldkey: str = None) -> dict:
        pass

    @abstractmethod
    async def hotkey_to_uid(self) -> list[dict[str, Any]]:
        pass
