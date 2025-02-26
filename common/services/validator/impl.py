from collections import defaultdict, Counter
from datetime import datetime, timedelta
from functools import reduce
from operator import add
from typing import Dict, Optional, List, Tuple

from common import formula, utils
from common.db.database import DatabaseManager
from common.db.repositories import (
    campaign,
    miner_ping,
    miner_assignment, miners_metadata,
)
from common.db.repositories.bitads_data import (
    get_aggregated_data,
    get_miners_reputation,
)
from common.db.repositories.campaign import get_active_campaigns
from common.helpers import const
from common.schemas.aggregated import AggregationSchema, AggregatedData
from common.schemas.bitads import Campaign
from common.schemas.campaign import CampaignType
from common.schemas.metadata import MinersMetadataSchema
from common.services.settings.impl import SettingsContainerImpl
from common.services.validator.base import ValidatorService
from common.validator.environ import Environ
from common.validator.schemas import (
    CampaignSchema,
)


class ValidatorServiceImpl(SettingsContainerImpl, ValidatorService):
    """Implementation of ValidatorService interface providing validator-related functionalities.

    This service integrates with databases and repositories to calculate ratings,
    synchronize campaigns, process actions, and manage tracking data for validators.

    Attributes:
        database_manager (DatabaseManager): Database manager instance for database interactions.
        ndigits (int): Number of digits for rounding scores.

    Methods:
        calculate_ratings(from_block: Optional[int] = None, to_block: Optional[int] = None) -> Dict[str, float]:
            Calculates ratings based on block range.

        sync_active_campaigns(current_block: int, active_campaigns: List[Campaign]) -> None:
            Synchronizes active campaigns based on the current block.

        send_action(id_: str, action: Action, amount: float = 0.0) -> None:
            Sends an action with optional amount.

        calculate_and_set_campaign_umax(from_block: int, to_block: int) -> Dict[str, float]:
            Calculates and sets campaign uMax values based on block range.

        get_visits_to_complete(page_number: int = 1, page_size: int = 500) -> List[ValidatorTrackingData]:
            Retrieves visits to complete based on pagination parameters.

        complete_visits(completed_visits: List[CompletedVisitSchema]) -> None:
            Marks visits as completed based on provided data.
    """

    def __init__(self, database_manager: DatabaseManager, ndigits: int = 5):
        """Initializes ValidatorServiceImpl with database manager and rounding digits.

        Args:
            database_manager (DatabaseManager): Database manager instance for database interactions.
            ndigits (int, optional): Number of digits for rounding scores. Defaults to 5.
        """
        super().__init__()
        self.database_manager = database_manager
        self.ndigits = ndigits

    async def calculate_ratings(
        self, from_block: Optional[int] = None, to_block: Optional[int] = None
    ) -> Dict[str, float]:
        """Calculates ratings based on block range.

        Args:
            from_block (int, optional): Starting block number. Defaults to None.
            to_block (int, optional): Ending block number. Defaults to None.

        Returns:
            Dict[str, float]: A dictionary mapping validator IDs to rating scores.

        Raises:
            ValueError: If no active campaigns are found within the specified block range.
        """
        cpa_from_block = to_block - utils.timedelta_to_blocks(const.REWARD_SALE_PERIOD)
        campaigns = self._get_active_campaigns(cpa_from_block, to_block)
        if not campaigns:
            raise ValueError("No active campaigns found")
        # region CPA-part
        cpa_campaign_to_id = {c.id: c for c in campaigns if CampaignType.CPA == c.type}
        now = datetime.utcnow()
        sale_from = now - const.REWARD_SALE_PERIOD
        reputation_from = now - utils.blocks_to_timedelta(self.settings.mr_blocks)
        scores = []
        for campaign_id, c in cpa_campaign_to_id.items():
            cpa_aggregated_data = self._get_aggregated_data(
                campaign_id,
                sale_from=sale_from,
                sale_to=now,
            )
            miners_reputation = self._get_miners_reputation(
                campaign_id, sale_from=reputation_from, sale_to=now
            )
            scores.append(
                self._calculate_cpa_miner_scores(
                    cpa_aggregated_data, [campaign_id], miners_reputation
                )
            )
        # endregion

        cpa_miner_scores = dict(reduce(add, (Counter(dict(x)) for x in scores)))
        cpa_miner_scores = {k: v / len(scores) for k, v in cpa_miner_scores.items()}

        final_scores = self._normalize_scores(cpa_miner_scores)

        return final_scores

    async def sync_active_campaigns(
        self, current_block: int, active_campaigns: List[Campaign]
    ) -> None:
        """Synchronizes active campaigns based on the current block.

        Args:
            current_block (int): The current block number.
            active_campaigns (List[Campaign]): List of active campaigns to synchronize.
        """
        active_campaign_ids = {c.product_unique_id for c in active_campaigns}
        with self.database_manager.get_session("active") as session:
            local_campaign_ids = campaign.get_active_campaign_ids(session)
            # update existing campaigns
            for local_campaign_id in local_campaign_ids:
                status = local_campaign_id in active_campaign_ids
                campaign.update_campaign_status(session, local_campaign_id, status)
            # add new campaigns if needed
            for active_campaign in active_campaigns:
                cpa_blocks = utils.timedelta_to_blocks(
                    timedelta(days=active_campaign.product_refund_period_duration)
                )
                campaign.add_or_create_campaign(
                    session,
                    active_campaign.product_unique_id,
                    current_block,
                    active_campaign.type,
                    cpa_blocks,
                )

    async def add_miner_ping(
        self, current_block: int, unique_id_to_hotkey: Dict[str, Tuple[str, str]]
    ):
        with self.database_manager.get_session("active") as session:
            for unique_id, hotkey_campaign in unique_id_to_hotkey.items():
                hotkey, campaign_id = hotkey_campaign
                miner_ping.add_miner_ping(session, hotkey, current_block)
                miner_assignment.create_or_update_miner_assignment(
                    session, unique_id, hotkey, campaign_id
                )

    async def get_miners_metadata(self) -> Dict[str, MinersMetadataSchema]:
        with self.database_manager.get_session("active") as session:
            metadatas = miners_metadata.get_miners_metadata(session)
            return {m.hotkey: m for m in metadatas}

    async def add_miner_metadata(self, metadata: MinersMetadataSchema) -> None:
        with self.database_manager.get_session("active") as session:
            miners_metadata.add_or_update(session, metadata)

    def _calculate_miner_scores(
        self, aggregated_data: AggregatedData, campaigns: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculates miner scores based on aggregated data and campaign uMax values.

        Args:
            aggregated_data (AggregatedData): Aggregated data for calculation.
            campaigns (Dict[str, float]): Dictionary mapping campaign IDs to uMax values.

        Returns:
            Dict[str, float]: Dictionary mapping miner hotkeys to calculated scores.
        """
        if not campaigns:
            return {}
        miner_scores = defaultdict(float)
        num_active_campaigns = len(campaigns)

        for campaign_id, miners_data in aggregated_data.data.items():
            campaign_umax = campaigns.get(campaign_id) or const.DEFAULT_UVMAX
            for miner_hotkey, aggregation in miners_data.items():
                rating = self._calculate_rating(aggregation, campaign_umax)
                miner_scores[miner_hotkey] += rating / num_active_campaigns

        return miner_scores

    def _calculate_cpa_miner_scores(
        self,
        aggregated_data: AggregatedData,
        campaign_ids: List[str],
        miners_reputation: Dict[str, int],
    ) -> Dict[str, float]:
        """Calculates CPA miner scores based on aggregated data, campaign IDs, and miners' reputation.

        Args:
            aggregated_data (AggregatedData): Aggregated data for calculation.
            campaign_ids (List[str]): List of campaign IDs for CPA campaigns.
            miners_reputation (Dict[str, int]): Dictionary mapping miner hotkeys to reputation scores.

        Returns:
            Dict[str, float]: Dictionary mapping miner hotkeys to calculated CPA scores.
        """
        if not campaign_ids:
            return {}
        miner_scores = defaultdict(float)
        num_active_campaigns = len(campaign_ids)

        for campaign_id in campaign_ids:
            miners_data = aggregated_data.data.get(campaign_id, {})
            for miner_hotkey, reputation in miners_reputation.items():
                aggregation = miners_data.get(miner_hotkey, AggregationSchema())
                rating = self._calculate_cpa_rating(
                    aggregation, reputation, miner_hotkey
                )
                miner_scores[miner_hotkey] += rating / num_active_campaigns

        return miner_scores

    def _calculate_rating(self, aggregation: AggregationSchema, UVmax: int) -> float:
        """Calculates rating based on aggregation data and uMax value.

        Args:
            aggregation (AggregationSchema): Aggregation schema for calculation.
            UVmax (int): uMax value for normalization.

        Returns:
            float: Calculated rating score.
        """
        return formula.process_aggregation(
            aggregation,
            CTRmax=self._params.ctr_max,
            Wots=self._params.wats,
            Wuvps=self._params.wuvps,
            Wuv=self._params.wuv,
            Wctr=self._params.wctr,
            UVmax=UVmax,
            ndigits=self.ndigits,
        )

    def _calculate_cpa_rating(
        self, aggregation: AggregationSchema, MR: float, miner_hotkey: str
    ) -> float:
        """Calculates CPA rating based on aggregation data and miner's reputation.

        Args:
            aggregation (AggregationSchema): Aggregation schema for calculation.
            MR (float): Miner's reputation score.

        Returns:
            float: Calculated CPA rating score.
        """
        return formula.process_cpa(
            aggregation,
            *self.settings.conversion_rate_limits,
            MR=MR,
            SALESmax=self._params.sales_max,
            MRmax=self._params.mr_max,
            CRmax=self._params.cr_max,
            Wsales=self._params.w_sales,
            Wcr=self._params.w_cr,
            Wmr=self._params.w_mr,
            ndigits=self.ndigits,
            miner_hotkey=miner_hotkey,
        )

    def _normalize_scores(self, miner_scores: Dict[str, float]) -> Dict[str, float]:
        """Normalizes miner scores to be within range [0, 1].

        Args:
            miner_scores (Dict[str, float]): Dictionary mapping miner hotkeys to scores.

        Returns:
            Dict[str, float]: Normalized dictionary mapping miner hotkeys to scores.
        """
        return {
            miner_hotkey: min(max(round(score, self.ndigits), 0), 1)
            for miner_hotkey, score in miner_scores.items()
        }

    def _get_aggregated_data(
        self,
        *campaign_ids,
        sale_from: Optional[datetime] = None,
        sale_to: Optional[datetime] = None,
        from_block: Optional[int] = None,
        to_block: Optional[int] = None,
    ) -> AggregatedData:
        """Retrieves aggregated data for specified block range and campaign IDs.

        Args:
            from_block (int, optional): Starting block number. Defaults to None.
            to_block (int, optional): Ending block number. Defaults to None.
            *campaign_ids: Variable length list of campaign IDs.

        Returns:
            AggregatedData: Aggregated data schema containing aggregated data.
        """
        with self.database_manager.get_session("active") as session:
            return get_aggregated_data(
                session,
                *campaign_ids,
                from_block=from_block,
                to_block=to_block,
                from_date=sale_from,
                to_date=sale_to,
            )

    def _get_active_campaigns(
        self, from_block: Optional[int] = None, to_block: Optional[int] = None
    ) -> List[CampaignSchema]:
        """Retrieves active campaigns within the specified block range.

        Args:
            from_block (int, optional): Starting block number. Defaults to None.
            to_block (int, optional): Ending block number. Defaults to None.

        Returns:
            List[CampaignSchema]: List of active campaign schemas.
        """
        with self.database_manager.get_session("active") as session:
            return get_active_campaigns(session, from_block, to_block)

    def _get_miners_reputation(
        self,
        *campaign_ids,
        sale_from: Optional[datetime] = None,
        sale_to: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """Retrieves miners' reputation scores for specified block range and campaign IDs.

        Args:
            from_block (int, optional): Starting block number. Defaults to None.
            to_block (int, optional): Ending block number. Defaults to None.
            *campaign_ids: Variable length list of campaign IDs.

        Returns:
            Dict[str, int]: Dictionary mapping miner hotkeys to reputation scores.
        """
        with self.database_manager.get_session("active") as session:
            return get_miners_reputation(
                session, *campaign_ids, from_date=sale_from, to_date=sale_to
            )
