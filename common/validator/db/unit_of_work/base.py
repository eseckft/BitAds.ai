from abc import ABC

from common.db.repositories.base import TrackingDataRepository
from common.db.unit_of_work.base import UnitOfWork


class ValidatorActiveUnitOfWork(UnitOfWork, ABC):
    tracking_data: TrackingDataRepository
