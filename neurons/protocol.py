from datetime import datetime
from typing import Optional, List, Literal, Any, Set

import bittensor as bt
from pydantic.main import IncEx

from common.miner.environ import Environ
from common.miner.schemas import VisitorSchema, VisitorActivitySchema
from common.schemas.bitads import Campaign, BitAdsDataSchema, GetMinerUniqueIdResponse
from common.validator.schemas import ValidatorTrackingData

_exclude = frozenset(("computed_body_hash",))


class BaseSynapse(bt.Synapse):
    # FIXME: bittensor issue, incorrect dump for synapse
    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "json",  # FIXME: fix is here
        include: IncEx = None,
        exclude: IncEx = _exclude,  # FIXME: and here
        context: dict[str, Any] | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        serialize_as_any: bool = False
    ) -> dict[str, Any]:
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any,
        )


class Ping(BaseSynapse):
    active_campaigns: List[Campaign] = []
    submitted_tasks: Optional[List[GetMinerUniqueIdResponse]] = []
    script_version: Optional[str] = None
    result: Optional[bool] = False


class UncompletedVisit(BaseSynapse):
    uncompleted_visit_ids: Set[str]
    completed_visits: Optional[List[VisitorSchema]] = []


class CompleteVisit(BaseSynapse):
    uncompleted_visits: List[ValidatorTrackingData]
    completed_visits: Optional[List[VisitorSchema]] = []


class RecentActivity(BaseSynapse):
    count: int = Environ.RECENT_ACTIVITY_COUNT
    limit: int = Environ.LIMIT_RECENT_ACTIVITY

    activity: Optional[List[VisitorActivitySchema]] = []


class SyncVisits(BaseSynapse):
    limit: int = 500
    offset: Optional[datetime] = None
    visits: Optional[Set[VisitorSchema]] = set()


class SyncTrackingData(BaseSynapse):
    limit: int = 500
    offset: Optional[datetime] = None
    tracking_data: Optional[Set[ValidatorTrackingData]] = set()
    bitads_data: Optional[Set[BitAdsDataSchema]] = set()
