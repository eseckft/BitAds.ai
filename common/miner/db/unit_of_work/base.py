from abc import ABC

from common.db.repositories.base import VisitorRepository
from common.db.unit_of_work.base import UnitOfWork


class MinerActiveUnitOfWork(UnitOfWork, ABC):
    visitors: VisitorRepository
