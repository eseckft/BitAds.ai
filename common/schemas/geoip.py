"""
IP address info schemas
"""
from pydantic import BaseModel


class IpAddressInfo(BaseModel):
    """
    Model representing information about an IP address.

    Attributes:
        country_name (str): The name of the country associated with the IP address.
    """

    country_name: str
    country_code: str
