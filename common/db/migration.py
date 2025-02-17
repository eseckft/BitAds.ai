from datetime import datetime, timedelta
from sqlalchemy import inspect, exists, asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import TypeVar, Type

from common.validator.environ import Environ

BATCH_SIZE = 1000

T = TypeVar("T")


def map_entity_fields(source, target):
    """
    Maps all fields from the source entity to the target entity where fields match.
    """
    source_mapper = inspect(source)

    # Iterate over source fields and set them on the target
    for column in source_mapper.mapper.column_attrs:
        field_name = column.key
        if hasattr(target, field_name):
            setattr(target, field_name, getattr(source, field_name))


def record_exists(history_session: Session, target_entity: Type[T], record: T) -> bool:
    """
    Checks if a record already exists in the historical database.
    """
    return history_session.query(exists().where(target_entity.id == record.id)).scalar()


def transfer_data(
    active_session: Session, history_session: Session, target_entity: Type[T], created_at_from: datetime
):
    while True:
        data_batch = (
            active_session.query(target_entity)
            .where(target_entity.created_at < created_at_from)
            .order_by(asc(target_entity.created_at))
            .limit(BATCH_SIZE)
            .all()
        )
        if not data_batch:
            break

        existing_ids = {row[0] for row in history_session.query(target_entity.id)
                        .filter(target_entity.id.in_([record.id for record in data_batch]))
                        .all()}

        for record in data_batch:
            if record.id not in existing_ids:
                historical_record = target_entity()
                map_entity_fields(record, historical_record)

                try:
                    history_session.add(historical_record)
                    history_session.flush()  # Ensures data is inserted before commit
                except IntegrityError:
                    history_session.rollback()
                    print(f"Duplicate detected for ID: {record.id}, skipping.")

        history_session.commit()

        for record in data_batch:
            existing_record = active_session.query(target_entity).filter_by(id=record.id).first()
            if existing_record:
                active_session.delete(existing_record)

        active_session.commit()