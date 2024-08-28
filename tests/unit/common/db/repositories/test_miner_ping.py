import os
import random
import unittest
from datetime import datetime
from sqlite3 import IntegrityError

from parameterized import parameterized
from sqlalchemy.exc import PendingRollbackError

from common.validator.db.entities.active import MinerPing
from common.db.database import DatabaseManager
from common.db.repositories.miner_ping import add_miner_ping, get_miner_pings, get_active_miners_count
from common.services.validator.impl import ValidatorServiceImpl
from common.validator.db.entities.active import Base as VABase
from common.db.entities import Base as MBase


class TestMinerPingRepositories(unittest.TestCase):

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
        ("cmrbkkfbfqwohgrlwlxtxmdixkmllubibriottdcndoge", 1),
        ("6RHMpmOU46fXlyj9c6iCVEvGPoUIrwzSDutuqwihYoqSP", 2),
        ("KGXM3o8Qe2lkYyo1i5lfkaEKFJWbiblpg81S2K7uUBICD", 3),
    ])
    def test_add_miner_ping_with_valid_data_then_happy_path(self, hotkey, block) -> None:
        with self.database_manager.get_session("active") as session:
            expected_result = add_miner_ping(session, hotkey, block)
            hotkey_query = session.query(MinerPing).filter_by(hot_key=hotkey).where(MinerPing.hot_key == hotkey).all()
            block_query = session.query(MinerPing).filter_by(hot_key=hotkey).where(MinerPing.hot_key == hotkey).all()
            hot_key_in_db = list(hotkey_query)[0].hot_key
            block_in_db = list(block_query)[0].block
            self.assertEqual(expected_result.hot_key, hot_key_in_db)
            self.assertEqual(expected_result.block, block_in_db)

    @parameterized.expand([
        ("", 1, None),
        ("6RHMpmOU46fXlyj9c6iCVEvGPoUIrwzSDutuqwihYoqSP", None, IntegrityError),
        ("KGXM3o8Qe2lkYyo1i5lfkaEKFJWbiblpg81S2K7uUBICD", 3, None),
        (None, 4, PendingRollbackError),
        (None, None, PendingRollbackError),
    ])
    def test_add_miner_ping_with_no_data_then_sad_path(self, hotkey, block, expected_result) -> None:
        with self.database_manager.active_sessionmaker() as session:
            if expected_result is not None:
                with self.assertRaises(Exception) as context:
                    add_miner_ping(session, hotkey, block)
                    exception = context.exception
                    self.assertEqual(exception, expected_result)
            else:
                test_result = add_miner_ping(session, hotkey, block)
                hotkey_query = session.query(MinerPing).filter_by(hot_key=hotkey).where(
                    MinerPing.hot_key == hotkey).all()
                hot_key_in_db = list(hotkey_query)[0].hot_key
                self.assertEqual(test_result.hot_key, hot_key_in_db)

    @parameterized.expand([
        (1, 1, TypeError),
        (1, "1312", TypeError),
        (1, 1.123123, TypeError),
        (1, [1.123123], TypeError),
        (1, True, TypeError),
        ([1], True, TypeError),
        (["312333"], True, TypeError),
        (["312333"], 1, TypeError),
        ("311321323", 1, TypeError),
        (1.123123, 1, TypeError),
        ("1.123123", 1, TypeError),
    ])
    def test_add_miner_ping_with_invalid_data_then_sad_path(self, hotkey, block, expected_result) -> None:
        with self.assertRaises(Exception) as context:
            with self.database_manager.get_session("active") as session:
                if expected_result is not None:
                    add_miner_ping(session, hotkey, block)
                    exception = context.exception
                    self.assertEqual(exception, expected_result)

    @parameterized.expand([
        ("6RHMpmOU46fXlyj9c6iCVEvGPoUIrwzSDutuqwihYoqSP", None, None),
        ("6RHMpmOU46fXlyj9c6iCVEvGPoUIrwzSDutuqwihYoqSP", None, datetime.now()),
        ("ABC6RHMpmOU46fXlyj9c6iCVEvGPoUIrwzSDutuqwihYoqSP", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), None),
    ])
    def test_get_miner_pings_with_valid_data_then_happy_path(self, hotkey, start_time, end_time) -> None:
        with self.database_manager.get_session("active") as session:
            new_ping = MinerPing(hot_key=hotkey, block=1)
            session.add(new_ping)
            add_miner_ping(session, hotkey, 1)
            test_result = get_miner_pings(session, hotkey, start_time, end_time)[0].hot_key
            self.assertEqual(test_result, hotkey)

    @parameterized.expand([
        ([
            "6RHMpmOU46fXlyj9c6iCVEvGPoUIrwzSDutuqwihYoqSP",
            "pwCYfMgvqFd1fAEro1noDNr87ehI5i2JaoTTgPquuWa18",
            "TtyC4YLg0xcu6WEBm0r0XdddTcBlcAaZUy6htcmSsqGPV",
            "Oj19GjRfH0ps5IYjZmDAwJlae9nN0dANzLH2T3lO6XRic",
            "erFOypwiOTEWUxQa1bEmaaA1HSvQDzrcU3SrN9gHc4Uv2"
        ], []),
    ])
    def test_get_miner_pings_with_only_hotkey_then_happy_path(self, hotkeys: [str], expected_result) -> None:
        with self.database_manager.get_session("active") as session:
            block = 1
            for i in range(len(hotkeys)):
                block += 1
                add_miner_ping(session, hotkeys[i], block)
            actual_result = get_miner_pings(session, random.choice(hotkeys), None, None).__getitem__(0).hot_key
            self.assertTrue([True if actual_result in hotkeys else False])

    @parameterized.expand([
        (None, None, None, []),
        (None, None, datetime.now(), []),
        (None, datetime.now(), None, []),
        (None, datetime.now(), datetime.now(), []),
        ("6RHMpmOU46fXlyj9c6iCVEvGPoUIrwzSDutuqwihYoqSP", None, None, []),
        ("6RHMpmOU46fXlyj9c6iCVEvGPoUIrwzSDutuqwihYoqSP", datetime.now(), None, []),
        ("6RHMpmOU46fXlyj9c6iCVEvGPoUIrwzSDutuqwihYoqSP", None, datetime.now(), []),
        ("6RHMpmOU46fXlyj9c6iCVEvGPoUIrwzSDutuqwihYoqSP", datetime.now(), datetime.now(), []),
        ("6RHMpmOU46fXlyj9c6iCVEvGPoUIrwzSDutuqwihYoqSP", datetime.now(), datetime.now(), []),
    ])
    def test_get_miner_pings_with_no_data_then_happy_path(self, hotkey, start_time, end_time, expected_result) -> None:
        with self.database_manager.get_session("active") as session:

            test_result = get_miner_pings(session, hotkey, start_time, end_time)

            self.assertEqual(expected_result, test_result)

    def test_get_miner_pings_with_invalid_data_then_sad_path(self) -> None:
        pass

    @parameterized.expand([
        ([
            "6RHMpmOU46fXlyj9c6iCVEvGPoUIrwzSDutuqwihYoqSP",
            "pwCYfMgvqFd1fAEro1noDNr87ehI5i2JaoTTgPquuWa18",
            "TtyC4YLg0xcu6WEBm0r0XdddTcBlcAaZUy6htcmSsqGPV",
            "Oj19GjRfH0ps5IYjZmDAwJlae9nN0dANzLH2T3lO6XRic",
            "erFOypwiOTEWUxQa1bEmaaA1HSvQDzrcU3SrN9gHc4Uv2",
            "MnMZLOf0kcLR4ztkozsLVoh6yifBfssjmGbRsTPr0913y",
            "9vM4bLWrl0x9ny9x9TfGObXS8IiIj2O2RTZHRzgobrgaP",
            "ckcBeW0xolCrP1EAPxkiQI8QQWjkgGdNxLDbuQrw1Sx3d",
            "03WOxsM60Ijm8g6qXCdcz5UM81fVaUGBE4sQjIXhZhgaR",
            "6pkemdVb9i9v7mtItOcQKwJY5RRtep3AO37wMVI0DJWTI",
        ], 10, 10)
    ])
    def test_get_active_miners_count_with_valid_data_then_happy_path(self, hotkeys: [str], block, expected_result) -> None:
        with self.database_manager.get_session("active") as session:
            for i in range(block):
                add_miner_ping(session, hotkeys[i], i)

            test_result = get_active_miners_count(session, 0, block)
            self.assertEqual(expected_result, test_result)

    def test_get_active_miners_count_with_no_data_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as session:
            test_result = get_active_miners_count(session, 0, 0)
            self.assertEqual(0, test_result)

    def tearDown(self) -> None:
        with self.database_manager.get_session("active") as session:
            session.query(MinerPing).delete()


if __name__ == '__main__':
    unittest.main()
