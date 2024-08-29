"""
Common visits schemas
"""
from enum import IntEnum


class VisitStatus(IntEnum):
    """
    Enumeration representing the status of a visit.

    Attributes:
        new (int): Represents a new visit.
        synced (int): Represents a visit that has been synced.
        completed (int): Represents a completed visit.
    """

    new = 1
    synced = 2
    completed = 3
