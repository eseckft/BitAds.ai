from common.db.unit_of_work.alchemy import SQLAlchemyUnitOfWork
from common.validator.db.repositories.tracking_data import (
    SQLAlchemyTrackingDataRepository,
)
from common.validator.db.unit_of_work.base import ValidatorActiveUnitOfWork


class ValidatorActiveUnitOfWorkImpl(
    ValidatorActiveUnitOfWork, SQLAlchemyUnitOfWork
):
    def _init_repos(self):
        self.tracking_data = SQLAlchemyTrackingDataRepository(self._session)
