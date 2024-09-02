import os
import random
import unittest
from datetime import datetime
from unittest.mock import MagicMock

from faker import Faker

from parameterized import parameterized

from build.lib.common.validator.db.entities.active import MinerPing
from common.db.database import DatabaseManager
from common.db.repositories.visitor import add_visitor, get_visitor, update_status, get_new_visits, is_visitor_unique, \
    is_return_in_site
from common.miner.db.entities.active import Visitor
from common.miner.schemas import VisitorSchema
from common.services.validator.impl import ValidatorServiceImpl
from common.validator.db.entities.active import Base as VABase
from common.db.entities import Base as MBase

faker = Faker()
Faker.seed(datetime.now().timestamp())


class TestVisitorRepositories(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        os.environ["DB_URL_TEMPLATE"] = "sqlite:///:memory:"
        self.database_manager = DatabaseManager(
            neuron_type="test_neuron", subtensor_network="test_network"
        )
        self.service = ValidatorServiceImpl(self.database_manager)
        self._create_test_db()

    def _create_test_db(self) -> None:
        VABase.metadata.create_all(self.database_manager.active_db)
        MBase.metadata.create_all(self.database_manager.main_db)

    @parameterized.expand([
        ((str(faker.unique.random_int(min=111111, max=999999)), faker.ipv4(), faker.user_agent(),
          faker.password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True),
          faker.password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True),
          faker.password(length=45, special_chars=False, digits=True, upper_case=True, lower_case=True),
          random.choice((True, False))), datetime.now(), datetime.now()),
    ])
    def test_add_visitor_with_valid_data_then_happy_path(self, visitor: VisitorSchema, return_in_site_from: datetime,
                                                         unique_deadline: datetime):
        with self.database_manager.get_session("active") as session:
            add_visitor(session, visitor, return_in_site_from, unique_deadline)
            session.add.assert_called_with(Visitor(**visitor.model_dump()))
        self.assertEqual(False, True)

    @parameterized.expand([
        (Visitor(str(faker.unique.random_int(min=111111, max=999999)), faker.ipv4(), faker.user_agent(),
                 faker.password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True),
                 faker.password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True),
                 faker.password(length=45, special_chars=False, digits=True, upper_case=True, lower_case=True),
                 random.choice((True, False))))
    ])
    def test_get_visitor_by_ip_with_valid_data_then_happy_path(self, data: Visitor):
        with self.database_manager.get_session("active") as session:
            session.query(Visitor).add(data)
            session.commit()

            visitor = get_visitor(session, data.ip_address)
            self.assertEqual(visitor.ip_address, data.ip_address)

    def test_update_status_with_valid_data_then_happy_path(self):
        pass

    def test_get_new_visits_with_valid_data_then_happy_path(self):
        pass

    def test_get_new_visits_with_no_data_then_happy_path(self):
        pass

    def test_get_new_visits_with_invalid_data_then_happy_path(self):
        pass

    def test_is_visitor_unique_with_valid_data_then_happy_path(self):
        pass

    def test_is_visitor_unique_with_no_data_then_happy_path(self):
        pass

    def test_is_visitor_unique_with_invalid_data_then_happy_path(self):
        pass

    def test_is_return_in_site_with_valid_data_then_happy_path(self):
        pass

    def test_is_return_in_site_with_no_data_then_happy_path(self):
        pass

    def test_is_return_in_site_with_invalid_data_then_happy_path(self):
        pass

    def tearDown(self):
        with self.database_manager.get_session("active") as session:
            session.query(Visitor).delete()


if __name__ == '__main__':
    unittest.main()
