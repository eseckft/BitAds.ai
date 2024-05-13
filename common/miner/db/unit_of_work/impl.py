from common.db.unit_of_work.alchemy import SQLAlchemyUnitOfWork
from common.miner.db.repositories.visitors import SQLAlchemyVisitorRepository
from common.miner.db.unit_of_work.base import MinerActiveUnitOfWork


class MinerActiveUnitOfWorkImpl(MinerActiveUnitOfWork, SQLAlchemyUnitOfWork):
    def _init_repos(self):
        self.visitors = SQLAlchemyVisitorRepository(self._session)
