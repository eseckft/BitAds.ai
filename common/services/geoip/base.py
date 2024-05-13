from abc import ABC, abstractmethod
from typing import Optional

from common.schemas.geoip import IpAddressInfo


class GeoIpService(ABC):
    """Abstract base class for a GeoIP service.

    This class defines the interface for a service that provides geographical
    information based on an IP address. Subclasses must implement the
    `get_ip_info` method to retrieve the IP address information.

    Methods:
        get_ip_info(ip: str) -> Optional[IpAddressInfo]:
            Retrieves information about the specified IP address.
    """

    @abstractmethod
    def get_ip_info(self, ip: str) -> Optional[IpAddressInfo]:
        """Retrieves information about the specified IP address.

        Args:
            ip (str): The IP address to retrieve information for.

        Returns:
            Optional[IpAddressInfo]: An instance of `IpAddressInfo` containing
            information about the IP address, or `None` if the information
            could not be retrieved.
        """
        pass
