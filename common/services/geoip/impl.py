from typing import Optional

import geoip2.database
import geoip2.errors

from common.schemas.geoip import IpAddressInfo
from common.services.geoip.base import GeoIpService


class GeoIpServiceImpl(GeoIpService):
    """Implementation of the GeoIpService using the geoip2 library.

    This class provides a concrete implementation of the GeoIpService
    abstract base class, retrieving geographical information about an
    IP address using a GeoIP2 database.

    Attributes:
        database_path (str): Path to the GeoIP2 database file.
    """

    def __init__(self, database_path: str):
        """Initializes the GeoIpServiceImpl with the path to the GeoIP2 database.

        Args:
            database_path (str): Path to the GeoIP2 database file.
        """
        self.database_path = database_path

    def get_ip_info(self, ip: str) -> Optional[IpAddressInfo]:
        """Retrieves information about the specified IP address.

        This method uses the GeoIP2 database to get geographical information
        for the provided IP address. If the IP address is not found in the
        database, it returns None.

        Args:
            ip (str): The IP address to retrieve information for.

        Returns:
            Optional[IpAddressInfo]: An instance of `IpAddressInfo` containing
            information about the IP address, or `None` if the information
            could not be retrieved.
        """
        with geoip2.database.Reader(self.database_path) as reader:
            try:
                response = reader.country(ip)
            except geoip2.errors.AddressNotFoundError:
                return None
            else:
                return IpAddressInfo(
                    country_name=response.country.name,
                    country_code=response.country.iso_code,
                )
