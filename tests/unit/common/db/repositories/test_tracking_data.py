import os
import unittest
from datetime import datetime, timedelta

from sqlite3 import IntegrityError

from common.helpers import const
from sqlalchemy import func, select

from common.validator.db.entities.active import TrackingData
from common.db.database import DatabaseManager
from common.db.repositories.tracking_data import (
    add_data,
    get_data,
    get_uncompleted_data,
    add_or_update,
    get_new_data,
    update_status,
    increment_counts,
    update_visit_duration,
    is_visitor_unique,
    get_max_date_excluding_hotkey,
    get_tracking_data_after,
)
from common.schemas.visit import VisitStatus
from common.validator.db.entities.active import Base as VABase
from common.db.entities import Base as MBase
from common.validator.schemas import ValidatorTrackingData

from tests.helpers.factories.tracking_data_factory import TrackingDataFactory
from tests.helpers.factories.validator_tracking_data_factory import (
    ValidatorTrackingDataFactory,
)
from tests.helpers.object_manipulation import object_as_dict


class TestTrackingDataRepositories(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        os.environ["DB_URL_TEMPLATE"] = "sqlite:///:memory:"
        self.database_manager = DatabaseManager(
            neuron_type="test_neuron", subtensor_network="test_network"
        )
        self._create_test_db()

    def _create_test_db(self) -> None:
        VABase.metadata.create_all(self.database_manager.active_db)
        MBase.metadata.create_all(self.database_manager.main_db)

    def test_add_tracking_data_with_valid_data_then_happy_path(self) -> None:
        unique_deadline = datetime.now() + timedelta(days=1)
        with self.database_manager.get_session("active") as session:
            expected_result = ValidatorTrackingDataFactory.build()
            add_data(session, expected_result, unique_deadline)
        actual_result = (
            session.query(TrackingData).filter_by(id=expected_result.id).first()
        )
        self.assertEqual(actual_result.__dict__["id"], expected_result.id)

    def test_add_tracking_data_with_invalid_data_then_sad_path(
        self,
    ) -> None:
        unique_deadline = datetime.now() + timedelta(days=1)
        with self.assertRaises(Exception) as context:
            with self.database_manager.get_session("active") as session:
                expected_result = ValidatorTrackingDataFactory.build()
                expected_result.id = 12

                add_data(session, expected_result, unique_deadline)
                exception = context.exception
                self.assertEqual(exception, IntegrityError)

    def test_add_tracking_data_with_no_data_then_sad_path(self) -> None:
        unique_deadline = datetime.now() + timedelta(days=1)
        with self.assertRaises(Exception) as context:
            with self.database_manager.get_session("active") as session:
                expected_result = ValidatorTrackingDataFactory.build()
                for field in expected_result.model_dump().keys():
                    expected_result.__dict__[field] = None
                    add_data(session, expected_result, unique_deadline)
                    exception = context.exception
                    self.assertEqual(exception, IntegrityError)

    def test_add_or_update_with_new_valid_data_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as session:
            expected_result = ValidatorTrackingDataFactory.build()
            expected_result.__dict__["status"] = VisitStatus.new
            add_or_update(session, expected_result)
        actual_result = ValidatorTrackingData.model_validate(
            session.query(TrackingData).filter_by(id=expected_result.id).first()
        )
        actual_result.__dict__["updated_at"] = None
        expected_result.__dict__["updated_at"] = None

        self.assertEqual(expected_result.__dict__, actual_result.__dict__)

    def test_add_or_update_with_already_created_valid_data_then_happy_path(
        self,
    ) -> None:
        with self.database_manager.get_session("active") as session:
            test_data = TrackingDataFactory.build()
            updated_data = ValidatorTrackingDataFactory.build()
            updated_data.__dict__["id"] = object_as_dict(test_data)["id"]

            session.add(test_data)
            session.commit()

            add_or_update(session, updated_data)

            actual_result = (
                session.query(TrackingData).filter_by(id=test_data.id).first()
            )
            del actual_result.__dict__["_sa_instance_state"]
            self.assertEqual(updated_data.__dict__, actual_result.__dict__)

    def test_get_data_with_valid_ids_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as session:
            expected_result = TrackingDataFactory.build()

            session.add(expected_result)
            session.commit()

            actual_result = ValidatorTrackingData.model_validate(
                get_data(session, expected_result.id)
            )

            del expected_result.__dict__["_sa_instance_state"]
            self.assertEqual(expected_result.__dict__, actual_result.__dict__)

    def test_get_data_with_invalid_ids_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as session:
            expected_result = TrackingDataFactory.build()

            session.add(expected_result)
            session.commit()

            actual_result = get_data(session, "test_id")
            self.assertEqual(None, actual_result)

    def test_get_uncompleted_data_with_valid_data_then_happy_path(self) -> None:
        updated_at_deadline = datetime.now() + timedelta(days=1)
        cpa_deadline = datetime.utcnow() - timedelta(
            seconds=100800 * const.BLOCK_DURATION.total_seconds()
        )

        with self.database_manager.get_session("active") as session:
            for _ in range(10):
                expected_result = TrackingDataFactory.build()
                session.add(expected_result)
                session.commit()

            result_list = []
            for row in (
                session.query(TrackingData)
                .where(
                    TrackingData.updated_at <= updated_at_deadline,
                    TrackingData.status != VisitStatus.completed,
                )
                .all()
            ):
                result_list.append(object_as_dict(row))
            session.commit()

            list_of_data = get_uncompleted_data(session, updated_at_deadline, cpa_deadline)

            actual_result = []
            for row in list_of_data:
                actual_result.append(row.__dict__)

            self.assertEqual(result_list, actual_result)

    def test_get_new_data_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as session:
            for _ in range(10):
                expected_result = TrackingDataFactory.build()
                session.add(expected_result)
                session.commit()

            result_list = []
            for row in (
                session.query(TrackingData)
                .where(TrackingData.status != VisitStatus.completed)
                .all()
            ):
                result_list.append(object_as_dict(row))
            session.commit()

            list_of_data = get_new_data(session)

            actual_result = []
            for row in list_of_data:
                actual_result.append(row.__dict__)

            self.assertEqual(result_list, actual_result)

    def test_update_status_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as session:
            expected_result = TrackingDataFactory.build()
            expected_result.__dict__["status"] = VisitStatus.new

            session.add(expected_result)
            session.commit()

            update_status(session, expected_result.id, VisitStatus.completed)

            actual_result = (
                session.query(TrackingData).filter_by(id=expected_result.id).first()
            )
            self.assertEqual(VisitStatus.completed, actual_result.__dict__["status"])

    def test_update_status_with_invalid_data_then_sad_path(self) -> None:
        with self.database_manager.get_session("active") as session:
            with self.assertRaises(Exception) as context:
                expected_result = TrackingDataFactory.build()
                expected_result.__dict__["status"] = VisitStatus.new

                session.add(expected_result)
                session.commit()

                expected_result.__dict__["id"] = "test_id"
                update_status(session, expected_result.id, VisitStatus.completed)

                self.assertEqual(context.exception, IntegrityError)

    def test_increment_counts_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as session:
            expected_result = TrackingDataFactory.build()
            expected_result.__dict__["image_click"] = 1
            expected_result.__dict__["mouse_movement"] = 2
            expected_result.__dict__["read_more_click"] = 3
            expected_result.__dict__["through_rate_click"] = 4
            session.add(expected_result)
            session.commit()

            increment_counts(session, expected_result.id, 1, 2, 3, 4)

            actual_result = (
                session.query(TrackingData).filter_by(id=expected_result.id).first()
            )
            self.assertEqual(expected_result.__dict__, actual_result.__dict__)

    def test_update_visit_duration_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as session:
            expected_result = TrackingDataFactory.build()
            expected_result.__dict__["visit_duration"] = 0
            session.add(expected_result)
            session.commit()

            update_visit_duration(session, expected_result.id, 10)

            actual_result = (
                session.query(TrackingData).filter_by(id=expected_result.id).first()
            )
            self.assertEqual(actual_result.__dict__["visit_duration"], 10)

    def test_is_visitor_unique_then_happy_path(self) -> None:
        unique_deadline = datetime.now() + timedelta(days=1)
        with self.database_manager.get_session("active") as session:
            test_data1 = TrackingDataFactory.build()

            session.add(test_data1)
            session.commit()

            result = is_visitor_unique(
                session, test_data1.ip_address, test_data1.campaign_id, unique_deadline
            )

            self.assertEqual(result, True)

    def test_get_max_date_excluding_hotkey_with_valid_data_then_heppy_path(
        self,
    ) -> None:
        with self.database_manager.get_session("active") as session:
            for _ in range(10):
                test_data = TrackingDataFactory.build()
                test_data.__dict__["updated_at"] = datetime.now() + timedelta(days=5)
                session.add(test_data)
                session.commit()
            stmt = select(func.max(TrackingData.updated_at)).where(
                TrackingData.validator_hotkey != "hotkey1"
            )
            expected_result = session.execute(stmt).fetchone()
            result = get_max_date_excluding_hotkey(session, "hotkey1")
            self.assertEqual(result, expected_result[0])

    def test_get_max_date_excluding_hotkey(self) -> None:
        with self.database_manager.get_session("active") as session:
            # 1. Setup Test Data
            excluded_hotkey = "hotkey_to_exclude"
            other_hotkeys = ["hotkey1", "hotkey2"]
            entries = []
            for hotkey in other_hotkeys:
                entries.append(
                    TrackingDataFactory.build(
                        validator_hotkey=hotkey,
                        updated_at=datetime.now() - timedelta(days=5),
                    )
                )
                entries.append(
                    TrackingDataFactory.build(
                        validator_hotkey=hotkey, updated_at=datetime.now()
                    )
                )
            entries.append(
                TrackingDataFactory.build(
                    validator_hotkey=excluded_hotkey,
                    updated_at=datetime.now() - timedelta(days=10),
                )
            )
            session.add_all(entries)
            session.commit()

            expected_max_date = max(
                entry.updated_at
                for entry in entries
                if entry.validator_hotkey != excluded_hotkey
            )
            result = get_max_date_excluding_hotkey(session, excluded_hotkey)
            self.assertEqual(result, expected_max_date)

            session.query(TrackingData).filter(
                TrackingData.validator_hotkey != excluded_hotkey
            ).delete()
            session.commit()
            result_none_again = get_max_date_excluding_hotkey(session, excluded_hotkey)
            self.assertIsNone(result_none_again)

    def test_get_tracking_data_after_with_(self) -> None:
        with self.database_manager.get_session("active") as session:
            for _ in range(10):
                test_data = TrackingDataFactory.build()
                test_data.__dict__["updated_at"] = datetime.now() + timedelta(days=5)
                session.add(test_data)
                session.commit()
            result = get_tracking_data_after(session, limit=5)
            self.assertEqual(len(result), 5)

    def tearDown(self) -> None:
        with self.database_manager.get_session("active") as session:
            session.query(TrackingData).delete()


if __name__ == "__main__":
    unittest.main()
