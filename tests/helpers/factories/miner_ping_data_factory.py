from typing import List

import factory

from common.validator.db.entities.active import MinerPing
from common.validator.schemas import MinerPingSchema


class MinerPingDataFactory(factory.Factory):
    class Meta:
        model = MinerPing

    @classmethod
    def create_batch_with_overrides(cls, **kwargs) -> List[MinerPing]:
        """
        Creates a batch of Campaign objects, allowing overrides for specific fields.
        """
        return [cls.build(overrides=kwargs) for _ in range(kwargs.get("size", 1))]

    hot_key = factory.Faker('password', length=45, special_chars=False, digits=True, upper_case=False,
                                     lower_case=True)
    block = factory.Faker('random_int', min=0, max=10000)
    created_at = factory.Faker("date_time_between", start_date="-1y", end_date="now")
