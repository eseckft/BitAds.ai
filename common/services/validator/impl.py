from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional, Set, List

from common import formula, utils
from common.db.database import DatabaseManager
from common.db.repositories import (
    campaign,
    tracking_data,
    miner_ping,
    completed_visit,
    miner_assignment,
)
from common.db.repositories.bitads_data import (
    get_aggregated_data,
    get_miners_reputation,
)
from common.db.repositories.campaign import get_active_campaigns
from common.db.repositories.completed_visit import (
    get_unique_visits_count,
)
from common.helpers import const
from common.schemas.aggregated import AggregationSchema, AggregatedData
from common.schemas.bitads import Campaign, BitAdsDataSchema
from common.schemas.campaign import CampaignType
from common.schemas.completed_visit import CompletedVisitSchema
from common.schemas.visit import VisitStatus
from common.services.settings.impl import SettingsContainerImpl
from common.services.validator.base import ValidatorService
from common.validator.environ import Environ
from common.validator.schemas import (
    Action,
    ValidatorTrackingData,
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

        add_tracking_data(data: ValidatorTrackingData) -> None:
            Adds tracking data for a validator.

        add_tracking_datas(tracking_datas: Set[ValidatorTrackingData]) -> None:
            Adds multiple tracking data entries for validators.

        get_last_update_tracking_data(exclude_hotkey: str) -> Optional[datetime]:
            Retrieves the last update timestamp of tracking data for a specified hotkey.

        get_tracking_data_after(after: datetime = None, limit: int = 500) -> Set[ValidatorTrackingData]:
            Retrieves tracking data entries after a specified date.

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
        cpa_from_block = to_block - self._params.cpa_blocks
        campaigns = self._get_active_campaigns(cpa_from_block, to_block)
        if not campaigns:
            raise ValueError("No active campaigns found")
        # region Non CPA-part
        regular_from_block = to_block - Environ.CALCULATE_UMAX_BLOCKS
        campaign_to_umax = {
            c.id: c.umax
            for c in campaigns
            if CampaignType.REGULAR == c.type
            and c.last_active_block >= regular_from_block
        }
        aggregated_data = self._get_aggregated_data(
            *campaign_to_umax.keys(),
            from_block=regular_from_block,
            to_block=to_block,
        )
        miner_scores = self._calculate_miner_scores(aggregated_data, campaign_to_umax)
        # endregion
        # region CPA-part
        cpa_campaign_ids = [c.id for c in campaigns if CampaignType.CPA == c.type]
        now = datetime.utcnow()
        sale_from = now - timedelta(
            seconds=self.settings.mr_blocks * const.BLOCK_DURATION.total_seconds()
        )
        sale_to = now - timedelta(
            seconds=self.settings.cpa_blocks * const.BLOCK_DURATION.total_seconds()
        )
        cpa_aggregated_data = self._get_aggregated_data(
            *cpa_campaign_ids,
            sale_from=sale_from,
            sale_to=sale_to,
        )  # TODO: include only visits between sale_to and now
        reputation_from = sale_from
        miners_reputation = self._get_miners_reputation(
            *cpa_campaign_ids, sale_from=reputation_from, sale_to=now
        )
        cpa_miner_scores = self._calculate_cpa_miner_scores(
            cpa_aggregated_data, cpa_campaign_ids, miners_reputation
        )
        # endregion

        scores = utils.combine_dicts_with_avg(miner_scores, cpa_miner_scores)

        final_scores = self._normalize_scores(scores)

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
                campaign.add_or_create_campaign(
                    session,
                    active_campaign.product_unique_id,
                    current_block,
                    active_campaign.type,
                )

    async def send_action(
        self, id_: str, action: Action, amount: float = 0.0
    ) -> Optional[ValidatorTrackingData]:
        """Sends an action with optional amount.

        Args:
            id_ (str): Identifier for the action.
            action (Action): Action type to send.
            amount (float, optional): Optional amount for the action. Defaults to 0.0.
        """
        with self.database_manager.get_session("active") as session:
            visit = tracking_data.get_data(session, id_)
            if not visit:
                return

            if (
                action == Action.through_rate_click
                and not visit.is_unique
                and (visit.created_at - datetime.utcnow())
                < timedelta(seconds=self._params.ctr_clicks_seconds)
            ):
                return
            kwargs = {}
            if action in {Action.sale}:
                kwargs["sale_amount"] = amount
            if action == Action.update_visit_duration:
                duration = datetime.utcnow() - visit.created_at
                kwargs["visit_duration"] = int(duration.total_seconds())
            else:
                kwargs[action] = 1
            return tracking_data.increment_counts(session, id_, **kwargs)

    async def add_tracking_data(
        self, data: ValidatorTrackingData, bitads_data: BitAdsDataSchema = None
    ) -> Optional[ValidatorTrackingData]:
        """Adds tracking data for a validator.

        Args:
            data (ValidatorTrackingData): Tracking data to add.

        Raises:
            KeyError: If tracking data with the same ID already exists.
        """
        with self.database_manager.get_session("active") as session:
            existed_data = tracking_data.get_data(session, data.id)
            if existed_data:
                sales = data.sales if data.sales else existed_data.sales
                refund = data.refund if data.refund else existed_data.refund
                sales_amount = data.sale_amount
                if bitads_data.refund_info and data.sales:
                    sales_amount -= round(
                        sum(float(i.price) for i in bitads_data.refund_info.items),
                        self.ndigits,
                    )
                if bitads_data.order_info and data.refund:
                    sales_amount += round(
                        sum(float(i.price) for i in bitads_data.order_info.items),
                        self.ndigits,
                    )
                return tracking_data.update_order_amounts(
                    session, data.id, sales, refund, sales_amount
                )

            now = datetime.utcnow()
            unique_deadline = now - timedelta(hours=self._params.unique_visits_duration)
            return tracking_data.add_data(session, data, unique_deadline)

    async def add_tracking_datas(
        self, tracking_datas: Set[ValidatorTrackingData]
    ) -> None:
        """Adds multiple tracking data entries for validators.

        Args:
            tracking_datas (Set[ValidatorTrackingData]): Set of tracking data entries to add.
        """
        with self.database_manager.get_session("active") as session:
            for td in tracking_datas:
                tracking_data.add_or_update(session, td)

    async def get_last_update_tracking_data(
        self, exclude_hotkey: str
    ) -> Optional[datetime]:
        """Retrieves the last update timestamp of tracking data for a specified hotkey.

        Args:
            exclude_hotkey (str): Hotkey to exclude from the timestamp retrieval.

        Returns:
            Optional[datetime]: Last update timestamp of tracking data, or None if not found.
        """
        with self.database_manager.get_session("active") as session:
            return tracking_data.get_max_date_excluding_hotkey(session, exclude_hotkey)

    async def get_tracking_data_after(
        self, after: datetime = None, limit: int = 500
    ) -> Set[ValidatorTrackingData]:
        """Retrieves tracking data entries after a specified date.

        Args:
            after (datetime, optional): Retrieve data after this date. Defaults to None.
            limit (int): Maximum number of entries to retrieve. Defaults to 500.

        Returns:
            Set[ValidatorTrackingData]: Set of tracking data entries retrieved.
        """
        with self.database_manager.get_session("active") as session:
            return tracking_data.get_tracking_data_after(session, after, limit)

    async def calculate_and_set_campaign_umax(
        self, from_block: int, to_block: int
    ) -> Dict[str, float]:
        """Calculates and sets campaign uMax values based on block range.

        Args:
            from_block (int): Starting block number.
            to_block (int): Ending block number.

        Returns:
            Dict[str, float]: A dictionary mapping campaign IDs to calculated uMax values.
        """
        result = {}
        with self.database_manager.get_session(
            "active"
        ) as active_session, self.database_manager.get_session("main") as main_session:
            active_campaign_ids = campaign.get_active_campaign_ids(active_session)
            active_miners_count = miner_ping.get_active_miners_count(
                active_session, from_block, to_block
            )

            for campaign_id in active_campaign_ids:
                uv_count = get_unique_visits_count(
                    main_session, campaign_id, from_block, to_block
                )  # FIXME: after returning of nonCPA campaigns
                umax = uv_count / active_miners_count if active_miners_count else 0
                result[campaign_id] = umax
                campaign.update_campaign_umax(active_session, campaign_id, umax)
        return result

    async def get_visits_to_complete(
        self, page_number: int = 1, page_size: int = 500
    ) -> List[ValidatorTrackingData]:
        """Retrieves visits to complete based on pagination parameters.

        Args:
            page_number (int, optional): Page number of results to retrieve. Defaults to 1.
            page_size (int, optional): Number of results per page. Defaults to 500.

        Returns:
            List[ValidatorTrackingData]: List of tracking data entries representing visits to complete.
        """
        limit = page_size
        offset = (page_number - 1) * page_size
        updated_at_deadline = datetime.utcnow() - const.TRACKING_DATA_DELTA
        cpa_deadline = datetime.utcnow() - timedelta(
            seconds=self._params.cpa_blocks * const.BLOCK_DURATION.total_seconds()
        )
        with self.database_manager.get_session("active") as session:
            return tracking_data.get_uncompleted_data(
                session, updated_at_deadline, cpa_deadline, limit, offset
            )

    async def complete_visits(
        self, completed_visits: List[CompletedVisitSchema]
    ) -> None:
        """Marks visits as completed based on provided data.

        Args:
            completed_visits (List[CompletedVisitSchema]): List of completed visit schemas.
        """
        with self.database_manager.get_session(
            "active"
        ) as active_session, self.database_manager.get_session("main") as main_session:
            for cv in completed_visits:
                tracking_data.update_status(
                    active_session, cv.id, VisitStatus.completed
                )
                if completed_visit.is_visit_exists(main_session, cv.id):
                    continue
                completed_visit.add_visitor(main_session, cv)

    async def add_miner_ping(
        self, current_block: int, unique_id_to_hotkey: Dict[str, str]
    ):
        with self.database_manager.get_session("active") as session:
            for unique_id, hotkey in unique_id_to_hotkey.items():
                miner_ping.add_miner_ping(session, hotkey, current_block)
                miner_assignment.create_or_update_miner_assignment(
                    session, unique_id, hotkey
                )

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
