import os
import unittest

from parameterized import parameterized
from sqlalchemy import insert

from common.db.database import DatabaseManager
from common.db.repositories.completed_visit import get_aggregated_data
from common.schemas.aggregated import AggregatedData
from common.services.validator.impl import ValidatorServiceImpl
from common.miner.db.entities.active import Base as VABase
from common.db.entities import Base as MBase, CompletedVisit
from tests.helpers.factories.completed_visit_factory import create_completed_visit


class TestCompletedVisitRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
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
        (0, 10),
    ])
    def test_get_aggregated_data_with_valid_data_then_happy_path(self, from_block, to_block) -> None:
        with self.database_manager.get_session("main") as session:
            for i in range(to_block):
                visit = create_completed_visit(session)
                visit.complete_block = i
                session.add(visit)
                session.commit()

        actual_result = get_aggregated_data(session, from_block, to_block)
        expected_result = session.query(CompletedVisit).filter(
            CompletedVisit.complete_block.between(from_block, to_block)).all()
        print(expected_result[0])
        print(actual_result.data)
        self.assertEqual(True, False)  # TODO refactor this test. Add the assertion for the aggregated data

    def test_get_aggregated_data_with_no_data_then_happy_path(self) -> None:
        with self.database_manager.get_session("main") as session:
            actual_result = get_aggregated_data(session)
            self.assertIsInstance(actual_result, AggregatedData)
            self.assertEqual(actual_result, AggregatedData(data={}))

    def test_get_aggregated_data_with_invalid_data_then_sad_path(self) -> None:
        pass

    def test_get_unique_visits_count_with_valid_data_then_happy_path(self) -> None:
        pass

    def test_get_unique_visits_count_with_no_data_then_sad_path(self) -> None:
        pass

    def test_get_unique_visits_count_with_invalid_data_then_sad_path(self) -> None:
        pass

    def test_add_visitor_with_valid_data_then_happy_path(self) -> None:
        pass

    def test_add_visitor_with_no_data_then_sad_path(self) -> None:
        pass

    def test_add_visitor_with_invalid_data_then_sad_path(self) -> None:
        pass

    def test_is_visit_exists_with_valid_data_then_happy_path(self) -> None:
        pass

    def test_is_visit_exists_with_no_data_then_sad_path(self) -> None:
        pass

    def test_is_visit_exists_with_invalid_data_then_sad_path(self) -> None:
        pass

    def tearDown(self) -> None:
        with self.database_manager.get_session("main") as session:
            session.query(CompletedVisit).delete()


if __name__ == '__main__':
    unittest.main()
