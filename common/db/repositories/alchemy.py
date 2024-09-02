from typing import TypeVar, Type, Optional, List

from sqlalchemy import Select, select, and_, exists
from sqlalchemy.orm import Session

from common.db.repositories.base import BaseRepository, Model, ID

Entity = TypeVar("Entity")


class BaseSQLAlchemyRepository(BaseRepository):
    def __init__(
        self,
        session: Session,
        entity_cls: Type[Entity],
        model_cls: Type[Model],
    ):
        self.model_cls = model_cls
        self.entity_cls = entity_cls
        self.session = session

    async def create(self, model_instance: Model) -> Model:
        entity = self.entity_cls(**model_instance.model_dump())
        self.session.add(entity)
        return model_instance

    async def get(self, id_: ID) -> Optional[Model]:
        entity = self.session.get(self.entity_cls, id_)
        return self.model_cls.model_validate(entity) if entity else None

    def _construct_list_stmt(self, **filters) -> Select:
        stmt = select(self.entity_cls)
        where_clauses = []
        for c, v in filters.items():
            if not hasattr(self.entity_cls, c):
                raise ValueError(f"Invalid column name {c}")
            where_clauses.append(getattr(self.entity_cls, c) == v)

        if where_clauses:
            stmt = stmt.where(and_(*where_clauses))

        return stmt

    async def list(
        self,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **filters,
    ) -> List[Model]:
        stmt = self._construct_list_stmt(**filters)
        if order_by:
            if not hasattr(self.entity_cls, order_by):
                raise ValueError(f"Invalid column name {order_by}")
            stmt = stmt.order_by(getattr(self.entity_cls, order_by))
        if limit:
            stmt = stmt.limit(limit)
            if offset:
                stmt = stmt.offset(offset)
        result = self.session.execute(stmt)
        return [
            self.model_cls.model_validate(s) for s in result.scalars().all()
        ]

    async def exists(self, id_: ID) -> bool:
        stmt = select(exists().where(self.entity_cls.id == id))
        result = self.session.execute(stmt)
        return result.scalar()
