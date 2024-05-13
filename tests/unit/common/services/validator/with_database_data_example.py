import os
import unittest
import random
from datetime import datetime, timedelta

from sqlalchemy import select

from common.db.repositories.tracking_data import add_data
from common.schemas.visit import VisitStatus
from common.validator.db.entities.active import Campaign, TrackingData, MinerPing
from common.validator.db.entities.active import Base as VABase
from common.db.entities import Base as MBase, CompletedVisit

from common.db.database import DatabaseManager
from common.services.validator.impl import ValidatorServiceImpl
from common.validator.schemas import CampaignSchema, ValidatorTrackingData
from common.schemas.bitads import Campaign as BitAds_Campaign
from tests.helpers.factories.campaign_data_factory import CampaignDataFactory, BitAdsCampaignEntityFactory
from tests.helpers.factories.completed_visit_factory import CompletedVisitFactory
from tests.helpers.factories.miner_ping_data_factory import MinerPingDataFactory
from tests.helpers.factories.tracking_data_factory import TrackingDataFactory
from tests.helpers.factories.validator_tracking_data_factory import ValidatorTrackingDataFactory


class TestValidatorServiceImpl(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        # This line tells DatabaseManager to use im memory db
        os.environ["DB_URL_TEMPLATE"] = "sqlite:///:memory:"
        self.database_manager = DatabaseManager(
            neuron_type="test_neuron", subtensor_network="test_network"
        )
        self.service = ValidatorServiceImpl(self.database_manager)

        self._create_test_db()

    def _create_test_db(self) -> None:
        VABase.metadata.create_all(self.database_manager.active_db)
        MBase.metadata.create_all(self.database_manager.main_db)

    def tearDown(self) -> None:
        with (self.database_manager.get_session("active") as active_session,
              self.database_manager.get_session("main") as main_session):
            active_session.query(Campaign).delete()
            active_session.query(TrackingData).delete()
            active_session.query(MinerPing).delete()
            main_session.query(CompletedVisit).delete()

    async def test_calculate_ratings(self) -> None:
        from_block = 0
        to_block = 10000

        with (self.database_manager.get_session("active") as active_session,
              self.database_manager.get_session("main") as main_session):
            for _ in range(6):
                umax = random.uniform(0.1, 10.0)
                campaign_data = CampaignDataFactory.build(umax=umax)
                miner_data = MinerPingDataFactory.build()
                completed_visits_data = CompletedVisitFactory.build(campaign_id=campaign_data.id,
                                                                    created_at=campaign_data.created_at,
                                                                    miner_hotkey=miner_data.hot_key,
                                                                    miner_block=miner_data.block)
                main_session.add(completed_visits_data)
                main_session.commit()
                active_session.add(campaign_data)
                active_session.commit()

            print(list(map(CampaignSchema.model_validate, active_session.query(Campaign).all())))

            result = await self.service.calculate_ratings(from_block, to_block)
            print(result)
            self.assertEqual(True, False)
            

    async def test_calculate_ratings_without_active_campaigns(self) -> None:
        from_block = None
        to_block = 100

        result = await self.service.calculate_ratings(from_block, to_block)
        with self.assertRaises(Exception) as context:
            self.assertEqual(result, context.exception)


    async def test_calculate_ratings_with_negative_umax(self) -> None:
        from_block = 5
        to_block = 6

        result = await self.service.calculate_ratings(from_block, to_block)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})

    async def test_calculate_ratings_with_float_umax(self) -> None:
        from_block = 3
        to_block = 4

        result = await self.service.calculate_ratings(from_block, to_block)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})

    async def test_calculate_ratings_with_str_umax(self) -> None:
        from_block = 7
        to_block = 8

        result = await self.service.calculate_ratings(from_block, to_block)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})

    async def test_sync_active_campaigns_with_valid_data_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as active_session:
            campaigns_data = [BitAdsCampaignEntityFactory.build() for _ in range(3)]
            print(campaigns_data)

            await self.service.sync_active_campaigns(1, campaigns_data)

            #TODO: Create the assertion for changes in bd
            self.assertEqual(True, True)
            #campaigns_list = list(map(active_session.query(Campaign).all()))
            #print([campaign.__dict__ for campaign in campaigns_list])

            #await self.service.sync_active_campaigns(campaigns_data.__dict__['last_active_block'], campaigns_list)

    async def test_send_action_then_happy_path(self) -> None:
        ...

    async def test_add_tracking_data_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as active_session:
            tracking_data = ValidatorTrackingDataFactory.build()
            print(tracking_data)
            await self.service.add_tracking_data(tracking_data)

            actual_data = ValidatorTrackingData.model_validate(
                active_session.query(TrackingData).filter_by(id=tracking_data.id).first())
            print(actual_data)
            self.assertEqual(tracking_data, actual_data)

    async def test_add_tracking_datas_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as active_session:
            tracking_data = {ValidatorTrackingDataFactory.build() for _ in range(3)}

            await self.service.add_tracking_datas(tracking_data)

            actual_data = set(
                map(ValidatorTrackingData.model_validate, active_session.query(TrackingData).filter_by().all()))
            #FIXME: find the solution to filter the query by specific tracking data ids
            self.assertEqual(tracking_data, actual_data)

    async def test_get_last_update_tracking_data_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as session:
            excluded_hotkey = "hotkey_to_exclude"
            other_hotkeys = ["hotkey1", "hotkey2"]
            entries = []
            for hotkey in other_hotkeys:
                entries.append(
                    TrackingDataFactory.build(validator_hotkey=hotkey,
                                              updated_at=datetime.now() - timedelta(days=5)))
                entries.append(TrackingDataFactory.build(validator_hotkey=hotkey, updated_at=datetime.now()))
            entries.append(TrackingDataFactory.build(validator_hotkey=excluded_hotkey,
                                                     updated_at=datetime.now() - timedelta(days=10)))
            session.add_all(entries)
            session.commit()

            expected_max_date = max(
                entry.updated_at
                for entry in entries
                if entry.validator_hotkey != excluded_hotkey
            )
            result = await self.service.get_last_update_tracking_data(excluded_hotkey)
            self.assertEqual(result, expected_max_date)

            session.query(TrackingData).filter(
                TrackingData.validator_hotkey != excluded_hotkey).delete()
            session.commit()
            result_none_again = await self.service.get_last_update_tracking_data(excluded_hotkey)
            self.assertIsNone(result_none_again)

    async def test_get_tracking_data_after_then_happy_path(self) -> None:
        with self.database_manager.get_session('active') as active_session:
            limit = 10
            for _ in range(20):
                tracking_data = ValidatorTrackingDataFactory.build()
                add_data(active_session, tracking_data, datetime.now())
                active_session.commit()

            actual_data = await self.service.get_tracking_data_after(limit=limit)
            self.assertEqual(len(actual_data), 10)

            limit = 5

            actual_data = await self.service.get_tracking_data_after(limit=limit)
            self.assertEqual(len(actual_data), 5)

            actual_data = await self.service.get_tracking_data_after()
            self.assertEqual(len(actual_data), 20)

    async def test_calculate_and_set_campaign_umax_then_happy_path(self) -> None:
        with (self.database_manager.get_session("active") as active_session,
              self.database_manager.get_session("main") as main_session):
            from_block = 0
            to_block = 10_000
            for _ in range(20):
                campaigns_data = CampaignDataFactory.build()
                miner_data = MinerPingDataFactory.build()
                completed_visits_data = CompletedVisitFactory.build(campaign_id=campaigns_data.id,
                                                                    created_at=campaigns_data.created_at,
                                                                    miner_hotkey=miner_data.hot_key,
                                                                    miner_block=miner_data.block)

                active_session.add(campaigns_data)
                active_session.add(miner_data)
                active_session.commit()
                main_session.add(completed_visits_data)
                main_session.commit()

            actual_result = await self.service.calculate_and_set_campaign_umax(from_block, to_block)
            print(actual_result)
            # TODO: add the calculation of the umax on the test side

    async def test_get_visits_to_complete_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as active_session:
            for _ in range(5):
                tracking_data1 = TrackingDataFactory.build(status=VisitStatus.new)

                active_session.add(tracking_data1)
                active_session.commit()
            for _ in range(5):
                tracking_data2 = TrackingDataFactory.build(status=VisitStatus.completed)
                active_session.add(tracking_data2)
                active_session.commit()

            actual_data = await self.service.get_visits_to_complete()
            print(actual_data)

            stmt = (
                select(TrackingData)
                .where(TrackingData.status != VisitStatus.completed)
                .order_by(TrackingData.created_at)
            )
            result = active_session.execute(stmt).__dict__
            print(result)
    async def test_complete_visits_then_happy_path(self) -> None:
        ...


if __name__ == "__main__":
    unittest.main()
