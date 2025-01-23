from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from common.schemas.metadata import MinersMetadataSchema
from common.validator.db.entities.active import MinersMetadata


def add_or_update(
    session: Session,
    metadata: MinersMetadataSchema,
):
    # Try to find the existing entity by its ID
    entity = session.get(MinersMetadata, metadata.hotkey)

    # If the entity exists, update its attributes
    if entity:
        for key, value in dict(metadata).items():
            # Set the attribute on the entity
            setattr(entity, key, value)
    else:
        # Create a new entity if it doesn't exist
        entity = MinersMetadata(**dict(metadata))
        session.add(entity)
    return MinersMetadataSchema.model_validate(entity)


def get_miners_metadata(session: Session) -> List[MinersMetadataSchema]:
    stmt = select(MinersMetadata)

    result = session.execute(stmt)
    return [MinersMetadataSchema.model_validate(r) for r in result.scalars().all()]
