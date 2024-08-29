"""
Repository functions for interacting with MinerPing entity in the database.

These functions provide operations such as adding a new miner ping, retrieving miner pings,
and counting active miners within a block range.

Functions:
    add_miner_ping(session: Session, hot_key: str, block: int) -> MinerPingSchema:
        Adds a new miner ping entry to the database.

    get_miner_pings(session: Session, hot_key: Optional[str] = None, start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None) -> List[MinerPingSchema]:
        Retrieves miner pings based on optional filtering criteria.

    get_active_miners_count(session: Session, from_block: int, to_block: int) -> int:
        Counts active miners based on block range.

"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, func, distinct
from sqlalchemy.orm import Session

from common.validator.db.entities.active import MinerPing
from common.validator.schemas import MinerPingSchema


def add_miner_ping(
    session: Session, hot_key: str, block: int
) -> MinerPingSchema:
    """
    Adds a new miner ping entry to the database.

    Args:
        session (Session): The SQLAlchemy session object.
        hot_key (str): The hot key of the miner.
        block (int): The block number associated with the ping.

    Returns:
        MinerPingSchema: The validated schema representation of the added miner ping.

    """
    new_ping = MinerPing(hot_key=hot_key, block=block)
    session.add(new_ping)
    session.commit()
    return MinerPingSchema.model_validate(new_ping)


def get_miner_pings(
    session: Session,
    hot_key: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> List[MinerPingSchema]:
    """
    Retrieves miner pings from the database based on optional filtering criteria.

    Args:
        session (Session): The SQLAlchemy session object.
        hot_key (str, optional): The hot key of the miner (default: None).
        start_time (datetime, optional): The start time threshold for created_at (default: None).
        end_time (datetime, optional): The end time threshold for created_at (default: None).

    Returns:
        List[MinerPingSchema]: A list of validated schema representations of the retrieved miner pings.

    """
    stmt = select(MinerPing)

    if hot_key:
        stmt = stmt.where(MinerPing.hot_key == hot_key)
    if start_time:
        stmt = stmt.where(MinerPing.created_at >= start_time)
    if end_time:
        stmt = stmt.where(MinerPing.created_at <= end_time)

    result = session.execute(stmt)
    return [MinerPingSchema.model_validate(p) for p in result.scalars().all()]


def get_active_miners_count(
    session: Session, from_block: int, to_block: int
) -> int:
    """
    Counts active miners based on block range.

    Args:
        session (Session): The SQLAlchemy session object.
        from_block (int): The starting block number (inclusive).
        to_block (int): The ending block number (inclusive).

    Returns:
        int: The count of active miners within the specified block range.

    """
    result = session.execute(
        select(func.count(distinct(MinerPing.hot_key))).where(
            MinerPing.block.between(from_block, to_block)
        )
    )
    return result.scalar()
