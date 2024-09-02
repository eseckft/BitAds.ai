import os
import unittest
from sqlite3 import IntegrityError

from typing import Set, List
import random

import pydantic
from pydantic import TypeAdapter
from pydantic.v1.json import pydantic_encoder

from common.db.database import DatabaseManager
from common.db.repositories.campaign import get_active_campaign_ids, update_campaign_status, add_or_create_campaign, \
    update_campaign_umax, get_active_campaigns
from common.schemas.campaign import CampaignType
from common.validator.db.entities.active import Campaign
from common.validator.db.entities.active import Base as VABase
from common.db.entities import Base as MBase
from common.validator.schemas import CampaignSchema
from tests.helpers.factories.campaign_data_factory import CampaignDataFactory
from tests.helpers.object_manipulation import object_as_dict


class TestCampaignRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:

        os.environ["DB_URL_TEMPLATE"] = "sqlite:///:memory:"
        self.database_manager = DatabaseManager(
            neuron_type="test_neuron", subtensor_network="test_network"
        )
        self._create_test_db()

    def _create_test_db(self) -> None:
        VABase.metadata.create_all(self.database_manager.active_db)
        MBase.metadata.create_all(self.database_manager.main_db)

    def tearDown(self) -> None:
        with self.database_manager.get_session("active") as session:
            session.query(Campaign).delete()

    def test_get_active_campaign_ids_with_active_campaigns(self) -> None:
        with self.database_manager.get_session("active") as session:
            for _ in range(6):
                campaigns_data = CampaignDataFactory.build()
                session.add(campaigns_data)
                session.commit()

            actual_result = get_active_campaign_ids(session)

            expected_result = session.query(Campaign).filter(Campaign.status == True).all()
            print([x.__dict__['id'] for x in expected_result])
            self.assertIsInstance(actual_result, Set)
            self.assertEqual([x.__dict__['id'] for x in expected_result].sort(), list(actual_result).sort())

    def test_get_active_campaign_ids_with_no_active_campaigns(self) -> None:
        with self.database_manager.get_session("active") as session:
            actual_result = get_active_campaign_ids(session)
            self.assertIsInstance(actual_result, Set)
            self.assertEqual([], list(actual_result))

    def test_add_or_create_campaign_with_valid_data_if_campaign_does_not_exist_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as session:
            campaigns_data = CampaignDataFactory.build(status=True, last_active_block=1, umax=0.0)
            add_or_create_campaign(session, campaigns_data.__dict__['id'], campaigns_data.__dict__['last_active_block'],
                                   campaigns_data.__dict__['type'])
            session.commit()

            expected_result = [x.__dict__ for x in
                               list(map(CampaignSchema.model_validate, session.query(Campaign).filter(Campaign.id == campaigns_data.__dict__['id']).all()))]

            self.assertEqual(expected_result[0]['id'], campaigns_data.__dict__['id'])

    def test_add_or_create_campaign_with_valid_data_if_campaign_exists_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as session:
            block_num = random.randint(0, 1000)
            campaigns_data = CampaignDataFactory.build(status=True, last_active_block=block_num, umax=0.0)
            session.add(campaigns_data)
            session.commit()
            actual_result = object_as_dict(campaigns_data)

            add_or_create_campaign(session, actual_result['id'], block_num, actual_result['type'])
            session.commit()
            expected_result = list(map(CampaignSchema.model_validate, session.query(Campaign).filter(Campaign.id == actual_result['id']).all()))
            self.assertEqual(actual_result, expected_result[0].__dict__)

    def test_add_or_create_campaign_with_invalid_data_then_sad_path(self) -> None:
        with self.database_manager.get_session("active") as session:
            with self.assertRaises(Exception) as context:
                block_num = random.randint(0, 1000)
                # incorrect last_active_block type
                campaigns_data = CampaignDataFactory.build(status=True, last_active_block=str(block_num), umax=0.0)
                add_or_create_campaign(session, campaigns_data['id'], campaigns_data['last_active_block'],
                                       campaigns_data['type'])
                self.assertEqual(context.exception, IntegrityError)
            with self.assertRaises(Exception) as context:
                block_num = random.randint(0, 1000)
                # incorrect id type
                campaigns_data = CampaignDataFactory.build(status=True, last_active_block=block_num, umax=0.0)
                add_or_create_campaign(session, None, campaigns_data['last_active_block'],
                                       campaigns_data['type'])
                self.assertEqual(context.exception, IntegrityError)
            with self.assertRaises(Exception) as context:
                block_num = random.randint(0, 1000)
                # incorrect type type
                campaigns_data = CampaignDataFactory.build(status=True, last_active_block=block_num, umax=0.0)
                add_or_create_campaign(session, campaigns_data['id'], campaigns_data['last_active_block'],
                                       str(campaigns_data['type']))
                self.assertEqual(context.exception, IntegrityError)

    def test_update_campaign_status_campaign_with_valid_data_then_happy_path(self) -> None:
        with self.database_manager.get_session("active") as session:
            block_num = random.randint(0, 1000)
            campaigns_data = CampaignDataFactory.build(status=True, last_active_block=block_num, umax=0.0)
            session.add(campaigns_data)
            session.commit()

            update_campaign_status(session, object_as_dict(campaigns_data)['id'], False)
            expected_result = session.query(Campaign).filter(Campaign.id == campaigns_data.__dict__['id']).all()

            self.assertEqual(expected_result[0].status, False)

    def test_update_campaign_status_with_invalid_data_then_sad_path(self):
        with self.database_manager.get_session("active") as session:
            with self.assertRaises(Exception) as context:
                block_num = random.randint(0, 1000)
                campaigns_data = CampaignDataFactory.build(status=True, last_active_block=block_num, umax=0.0)
                session.add(campaigns_data)
                session.commit()

                update_campaign_status(session, None, False)
                self.assertEqual(context.exception, IntegrityError)

            with self.assertRaises(Exception) as context:
                block_num = random.randint(0, 1000)
                campaigns_data = CampaignDataFactory.build(status=True, last_active_block=block_num, umax=0.0)
                session.add(campaigns_data)
                session.commit()

                update_campaign_status(session, campaigns_data.__dict__['id'], None)
                self.assertEqual(context.exception, IntegrityError)

    def test_add_or_create_campaign_existing_campaign(self):
        with self.database_manager.get_session("active") as session:
            block_num = random.randint(0, 1000)
            campaigns_data = CampaignDataFactory.build(status=True, last_active_block=block_num, umax=0.0)
            session.add(campaigns_data)
            session.commit()
            actual_result = object_as_dict(campaigns_data)

            update_campaign_umax(session, actual_result['id'], umax=83912.83)
            session.commit()
            expected_result = list(map(CampaignSchema.model_validate, session.query(Campaign).filter(Campaign.id == actual_result['id']).all()))
            self.assertNotEqual(actual_result['umax'], expected_result[0].__dict__['umax'])

    def test_add_or_create_campaign_existing_campaign_with_invalid_data_then_sad_path(self):
        with self.database_manager.get_session("active") as session:
            with self.assertRaises(Exception) as context:
                block_num = random.randint(0, 1000)
                campaigns_data = CampaignDataFactory.build(status=True, last_active_block=block_num, umax=0.0)
                session.add(campaigns_data)
                session.commit()

                update_campaign_umax(session, None, umax=83912.83)
                self.assertEqual(context.exception, IntegrityError)

            with self.assertRaises(Exception) as context:
                block_num = random.randint(0, 1000)
                campaigns_data = CampaignDataFactory.build(status=True, last_active_block=block_num, umax=0.0)
                session.add(campaigns_data)
                session.commit()

                update_campaign_umax(session, campaigns_data.__dict__['id'], umax=None)
                self.assertEqual(context.exception, IntegrityError)

    def test_get_active_campaigns_with_valid_data_then_happy_path(self):
        with self.database_manager.get_session("active") as session:
            for _ in range(10):
                block_num = random.randint(0, 1000)
                campaigns_data = CampaignDataFactory.build(last_active_block=block_num)
                session.add(campaigns_data)
                session.commit()
            for _ in range(10):
                block_num = random.randint(1000, 2000)
                campaigns_data = CampaignDataFactory.build(last_active_block=block_num)
                session.add(campaigns_data)
                session.commit()

            actual_result = get_active_campaigns(session, 1, 1000)

            expected_result = list(map(CampaignSchema.model_validate, session.query(Campaign).filter(
                Campaign.last_active_block >= 1, Campaign.last_active_block <= 1000).all()))

            self.assertEqual(expected_result, actual_result)

            actual_result = get_active_campaigns(session, 1000, 2000)

            expected_result = list(map(CampaignSchema.model_validate, session.query(Campaign).filter(
                Campaign.last_active_block >= 1000, Campaign.last_active_block <= 2000).all()))

            self.assertEqual(expected_result, actual_result)

            actual_result = get_active_campaigns(session)

            expected_result = list(map(CampaignSchema.model_validate, session.query(Campaign).where(True).all()))

            self.assertEqual(expected_result, actual_result)



if __name__ == "__main__":
    unittest.main()
