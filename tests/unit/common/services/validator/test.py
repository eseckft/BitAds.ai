import unittest
from unittest.mock import MagicMock, patch
from unittest import TestCase

from common.validator.db.repositories import campaign

from common.schemas.aggregated import AggregatedData
from common.services.validator.impl import ValidatorServiceImpl
from common import dependencies as common_dependencies
from common.environ import Environ as CommonEnviron

from common.validator import dependencies
from common.validator.environ import Environ


class TestValidatorServiceImpl(TestCase):

    @unittest.mock.patch('common.db.repositories.campaign.get_active_campaign_ids')
    @unittest.mock.patch('common.db.repositories.miner_ping.get_active_miners_count')
    @unittest.mock.patch('common.db.repositories.completed_visit.get_unique_visits_count')
    @unittest.mock.patch('common.db.repositories.campaign.update_campaign_umax')
    @unittest.mock.patch('common.db.database.DatabaseManager.get_session')
    @unittest.mock.patch('common.services.settings.impl.SettingsContainerImpl',
                         new_callable=unittest.mock.PropertyMock)
    async def test_calculates_umax_correctly_with_active_campaigns_and_miners(self, mock_params, mock_get_session,
                                                                              mock_update_campaign_umax,
                                                                              mock_get_unique_visits_count,
                                                                              mock_get_active_miners_count,
                                                                              mock_get_active_campaign_ids):
        # Arrange
        mock_params.return_value = unittest.mock.Mock(ctr_max=1, wats=1, wuvps=1, wuv=1, wctr=1)
        mock_get_active_campaign_ids.return_value = ['lvwbwpj30tfea', 'lzfdwpj328fea']
        mock_get_active_miners_count.return_value = 10
        mock_get_unique_visits_count.side_effect = [100, 200]

        active_session_mock = unittest.mock.MagicMock()
        main_session_mock = unittest.mock.MagicMock()
        mock_get_session.side_effect = [active_session_mock, main_session_mock]

        database_manager = common_dependencies.get_database_manager(
            "validator", CommonEnviron.SUBTENSOR_NETWORK
        )
        validator_service = dependencies.get_validator_service(database_manager)
        # Act
        result = await validator_service.calculate_and_set_campaign_umax(1000, 2000)

        # Assert
        expected_result = {
            'lvwbwpj30tfea': 10.0,
            'lzfdwpj328fea': 20.0
        }
        self.assertEqual(result, expected_result)
        mock_update_campaign_umax.assert_any_call(active_session_mock, 'lvwbwpj30tfea', 10.0)
        mock_update_campaign_umax.assert_any_call(active_session_mock, 'lzfdwpj328fea', 20.0)

    @unittest.mock.patch('common.db.repositories.campaign.get_active_campaign_ids')
    @unittest.mock.patch('common.db.repositories.miner_ping.get_active_miners_count')
    @unittest.mock.patch('common.db.repositories.completed_visit.get_unique_visits_count')
    @unittest.mock.patch('common.db.repositories.campaign.update_campaign_umax')
    @unittest.mock.patch('common.db.database.DatabaseManager.get_session')
    @unittest.mock.patch('common.services.settings.impl.SettingsContainerImpl',
                         new_callable=unittest.mock.PropertyMock)
    @unittest.mock.patch('common.services.validator.base.ValidatorService.__init__', lambda x: None)
    async def test_handles_same_from_block_and_to_block(self, mock_params, mock_update_campaign_umax,
                                                        mock_get_unique_visits_count, mock_get_active_miners_count,
                                                        mock_get_active_campaign_ids):
        # Arrange
        mock_get_active_campaign_ids.return_value = ['lvwbwpj30tfea']
        mock_get_active_miners_count.return_value = 5
        mock_get_unique_visits_count.return_value = 25
        mock_params.return_value = unittest.mock.Mock()

        database_manager = common_dependencies.get_database_manager(
            "validator", CommonEnviron.SUBTENSOR_NETWORK
        )
        validator_service = dependencies.get_validator_service(database_manager)

        # Act
        result = await validator_service.calculate_and_set_campaign_umax(1000, 1000)

        # Assert
        self.assertEqual(result, {'lvwbwpj30tfea': 5.0})
        mock_update_campaign_umax.assert_called_once_with(unittest.mock.ANY, 'lvwbwpj30tfea', 5.0)
