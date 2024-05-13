from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from common.validator.db.unit_of_work.base import ValidatorActiveUnitOfWork
from common.validator.db.unit_of_work.impl import ValidatorActiveUnitOfWorkImpl
from common.validator.environ import Environ
from common.validator.services.track_data.base import TrackingDataService
from common.validator.services.track_data.impl import TrackingDataServiceImpl
from neurons.validator.core import CoreValidator


def get_core_validator() -> CoreValidator:
    return CoreValidator()


def get_active_engine():
    return create_async_engine(Environ.ACTIVE_DB_URL)


def get_active_sessionmaker(active_engine=Depends(get_active_engine)):
    return async_sessionmaker(active_engine)


def get_active_unit_of_work(
    active_sessionmaker=Depends(get_active_sessionmaker),
) -> ValidatorActiveUnitOfWork:
    return ValidatorActiveUnitOfWorkImpl(active_sessionmaker)


def get_tracking_data_service(
    unit_of_work=Depends(get_active_unit_of_work),
) -> TrackingDataService:
    return TrackingDataServiceImpl(unit_of_work)
