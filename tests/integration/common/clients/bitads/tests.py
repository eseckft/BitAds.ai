import unittest

import neurons
from common.clients.bitads.impl import SyncBitAdsClient
from common.schemas.bitads import PingResponse, GetMinerUniqueIdResponse
import bittensor as bt


class TestSyncBitAdsClient(unittest.TestCase):
    def setUp(self):
        # Create a mock base URL for testing
        self.base_url = "https://dev-s.a.bitads.ai"
        # Create a mock SyncBitAdsClient instance for testing

    def test_subnet_validator_list_miner_do_request_ping(self):
        self.client = SyncBitAdsClient(
            base_url=self.base_url,
            hot_key="5EUu648PHompCLcn9wr2UKKEN3de3yAPeG9acSQSVfTURPV4",
            v=neurons.__version__,
        )
        # Call the subnet_ping method
        response = self.client.subnet_ping()
        bt.logging.info(f"Response: {response}")
        # Assert that the response is not None
        self.assertIsNotNone(response)
        # Assert that the response is of type PingResponse
        self.assertIsInstance(response, PingResponse)
        # Assert that the response indicates success
        self.assertTrue(len(response.validators) > 0)

    def test_subnet_miner_list_validator_do_request_ping(self):
        self.client = SyncBitAdsClient(
            base_url=self.base_url,
            hot_key="5EUu648PHompCLcn9wr2UKKEN3de3yAPeG9acSQSVfTURPV4",
            v=neurons.__version__,
        )
        # Call the subnet_ping method
        response = self.client.subnet_ping()
        bt.logging.info(f"Response: {response}")
        # Assert that the response is not None
        self.assertIsNotNone(response)
        # Assert that the response is of type PingResponse
        self.assertIsInstance(response, PingResponse)
        # Assert that the response indicates success
        self.assertTrue(len(response.miners) > 0)

    def test_get_miner_unique_url(self):
        headers = {
            "v": neurons.__version__,
            "User-Agent": "PostmanRuntime/7.39.0",
            "hot_key": "5H97Vr4Xo3zYSncTau4heVCiDUPGv8H3WyD7k6VHC4jNDhnY",
        }
        self.client = SyncBitAdsClient(base_url=self.base_url, **headers)
        response = self.client.get_miner_unique_id("lty9sdtvcg55s")
        self.assertIsNotNone(response)
        self.assertIsInstance(response, GetMinerUniqueIdResponse)


if __name__ == "__main__":
    unittest.main()
