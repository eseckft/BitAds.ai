from typing import TypeVar, Type, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from common.db.entities import Base
from common.db.repositories.base import BaseRepository, Model, ID

Entity = TypeVar("Entity", bound=Base)


class BaseSQLAlchemyRepository(BaseRepository):
    def __init__(
        self,
        session: AsyncSession,
        entity_cls: Type[Entity],
        model_cls: Type[Model],
    ):
        self.model_cls = model_cls
        self.entity_cls = entity_cls
        self.session = session

    async def create(self, model_instance: Model) -> Model:
        entity = self.entity_cls(**model_instance.dict())
        self.session.add(entity)
        return model_instance

    async def get(self, id_: ID) -> Optional[Model]:
        entity = await self.session.get(self.entity_cls, id_)
        return self.model_cls.from_orm(entity) if entity else None
