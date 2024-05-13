from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    @abstractmethod
    def __aenter__(self):
        pass

    @abstractmethod
    def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass
