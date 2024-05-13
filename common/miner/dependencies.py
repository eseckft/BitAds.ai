from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from common.miner.db.unit_of_work.base import MinerActiveUnitOfWork
from common.miner.db.unit_of_work.impl import MinerActiveUnitOfWorkImpl
from common.miner.environ import Environ
from common.miner.services.visitors.base import VisitorService
from common.miner.services.visitors.impl import VisitorServiceImpl
from neurons.miner.core import CoreMiner


def get_core_miner() -> CoreMiner:
    return CoreMiner()


def get_active_engine():
    return create_async_engine(Environ.ACTIVE_DB_URL)


def get_active_sessionmaker(active_engine=Depends(get_active_engine)):
    return async_sessionmaker(active_engine)


def get_active_unit_of_work(
    active_sessionmaker=Depends(get_active_sessionmaker),
) -> MinerActiveUnitOfWork:
    return MinerActiveUnitOfWorkImpl(active_sessionmaker)


def get_visitor_service(
    unit_of_work=Depends(get_active_unit_of_work),
) -> VisitorService:
    return VisitorServiceImpl(unit_of_work)
