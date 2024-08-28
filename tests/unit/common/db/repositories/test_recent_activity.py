import os
import unittest
from datetime import datetime

from _sqlite3 import IntegrityError
from parameterized import parameterized

from common.db.database import DatabaseManager
from common.db.repositories.recent_activity import insert_or_update
from common.miner.db.entities.active import VisitorActivity
from common.services.validator.impl import ValidatorServiceImpl
from common.miner.db.entities.active import Base as VABase
from common.db.entities import Base as MBase


class TestRecentActivityRepositories(unittest.IsolatedAsyncioTestCase):
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
        ("192.168.42.32", datetime.now().strftime("%Y-%m-%d")),
        ("192.168.52.13", datetime.now().strftime("%Y-%m-%d")),

    ])
    def test_insert_or_update_with_valida_data_then_happy_path(self, ip, timestamp):
        with self.database_manager.get_session("active") as session:
            insert_or_update(session, ip, timestamp)

        ip_query = session.query(VisitorActivity).filter_by(ip=ip).where(VisitorActivity.ip == ip).all()
        timestamp_query = session.query(VisitorActivity).filter_by(created_at=timestamp).where(
            VisitorActivity.created_at == timestamp).all()
        ip_in_db = list(ip_query)[0].ip
        timestamp_in_db = list(timestamp_query)[0].created_at.strftime("%Y-%m-%d")

        self.assertEqual(ip_in_db, ip)
        self.assertEqual(timestamp_in_db, timestamp)

    @parameterized.expand([
        ("192.168.42.32", datetime.now().strftime("%Y-%m-%d")),
        ("192.168.52.13", datetime.now().strftime("%Y-%m-%d")),

    ])
    def test_insert_or_update_with_valida_data_then_happy_path(self, ip, timestamp):
        with self.database_manager.get_session("active") as session:
            insert_or_update(session, ip, timestamp)

        ip_query = session.query(VisitorActivity).filter_by(ip=ip).where(VisitorActivity.ip == ip).all()
        timestamp_query = session.query(VisitorActivity).filter_by(created_at=timestamp).where(
            VisitorActivity.created_at == timestamp).all()
        ip_in_db = list(ip_query)[0].ip
        timestamp_in_db = list(timestamp_query)[0].created_at.strftime("%Y-%m-%d")

        self.assertIsInstance(ip_in_db, str)
        self.assertIsInstance(timestamp_in_db, str)

    @parameterized.expand([
        ("", datetime.now().date()),
        ("192.168.42.32", None),
        (None, datetime.now().date()),
        (None, None)
    ])
    def test_insert_or_update_with_invalid_data_then_sad_path(self, ip, timestamp):
        with self.assertRaises(Exception) as context:
            with self.database_manager.get_session("active") as session:
                insert_or_update(session, ip, timestamp)
            error = context.exception
            self.assertEqual(error, IntegrityError)

    @parameterized.expand([
        (None, None),
        (None, datetime.now().date()),
        ("192.168.42.32", None),
    ])
    def test_insert_or_update_with_no_data_then_sad_path(self, ip, timestamp):
        with self.assertRaises(Exception) as context:
            with self.database_manager.get_session("active") as session:
                insert_or_update(session, ip, timestamp)
            error = context.exception
            self.assertEqual(error, IntegrityError)
            
    def tearDown(self) -> None:
        with self.database_manager.get_session("active") as session:
            session.query(VisitorActivity).delete()


if __name__ == '__main__':
    unittest.main()
