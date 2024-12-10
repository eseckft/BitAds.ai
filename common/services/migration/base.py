from abc import ABC, abstractmethod
from datetime import datetime

from common.db.database import DatabaseManager


class MigrationService(ABC):
    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager

    @abstractmethod
    async def migrate(self, created_at_from: datetime):
        pass
