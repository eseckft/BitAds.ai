import os
import unittest

from common.db.database import DatabaseManager
from common.db.repositories.campaigns import get_active_campaigns_with_u_maxes
from common.services.validator.impl import ValidatorServiceImpl
from common.validator.db.entities.active import Campaign
from common.validator.db.entities.active import Base as VABase
from common.db.entities import Base as MBase
from common.db.repositories import campaign


class TestCampaignsRepository(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        # This line tells DatabaseManager to use im memory db
        os.environ["DB_URL_TEMPLATE"] = "sqlite:///:memory:"
        self.database_manager = DatabaseManager(
            neuron_type="test_neuron", subtensor_network="test_network"
        )
        self.service = ValidatorServiceImpl(self.database_manager)

    def tearDown(self) -> None:
        # TODO refactor this teardown due to WinError 32: Access is denied
        mkdir = os.path.dirname(__file__)
        for f in os.listdir(mkdir):
            if not f.endswith(".db"):
                continue
            os.remove(os.path.join(mkdir, f))

    def _insert_test_data(self, data: dict[str, int]) -> None:  # Add the parameters for the test
        VABase.metadata.create_all(self.database_manager.active_db)
        MBase.metadata.create_all(self.database_manager.main_db)
        with self.database_manager.get_session("active") as session:
            for key in data:
                campaign.add_or_create_campaign(session, key, data[key])
        self.service.calculate_and_set_campaign_umax(1, 2)

    def test_get_active_campaigns_with_u_maxes_instances(self):
        self._insert_test_data({"c1": 1, "c2": 2, "c3": 3})

        with self.database_manager.get_session("active") as session:
            result = get_active_campaigns_with_u_maxes(session)

        self.assertIsInstance(result, dict)

    def test_get_active_campaigns_with_u_maxes_with_no_blocks(self):
        self._insert_test_data({"c1": 1, "c2": 2, "c3": 3})

        with self.database_manager.get_session("active") as session:
            result = get_active_campaigns_with_u_maxes(session, None, None)

        self.assertIsInstance(result, dict)


if __name__ == '__main__':
    unittest.main()
