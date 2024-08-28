import random

import factory
from datetime import datetime, timezone

from common.schemas.device import Device
from common.schemas.visit import VisitStatus
from common.validator.db.entities.active import TrackingData


class TrackingDataFactory(factory.Factory):
    class Meta:
        model = TrackingData

    @classmethod
    def create_batch_with_overrides(cls, **kwargs) -> TrackingData:
        """
        Creates a batch of ValidatorTrackingData objects, allowing overrides for specific fields.
        """
        return cls.build(overrides=kwargs)

    id = factory.Faker('password', length=6, special_chars=False, digits=True, upper_case=False,
                       lower_case=True)
    user_agent = factory.Faker('user_agent')
    ip_address = factory.Faker('ipv4')
    country = factory.Faker('country_code')
    campaign_id = factory.Faker('password', length=12, special_chars=False, digits=True, upper_case=False,
                                lower_case=True)
    validator_block = factory.Faker('random_int', min=0, max=10000)
    validator_hotkey = factory.Faker('password', length=45, special_chars=False, digits=True, upper_case=False,
                                     lower_case=True)
    at = factory.Faker('boolean')
    refund = factory.Faker("random_int", min=0, max=3)
    sales = factory.Faker("random_int", min=refund, max=10)
    sale_amount = factory.Faker("pydecimal", left_digits=sales, right_digits=2, positive=True)

    device = factory.LazyFunction(lambda: random.choice(list(Device)).value)
    status = factory.Faker('random_element', elements=[status for status in VisitStatus])
    count_image_click = factory.Faker('random_int', min=0, max=5)
    count_mouse_movement = factory.Faker('random_int', min=0, max=100)
    count_read_more_click = factory.Faker('random_int', min=0, max=3)
    count_through_rate_click = factory.Faker('random_int', min=0, max=2)

    visit_duration = factory.Faker("random_int", min=0, max=360)
    is_unique = factory.Faker('boolean')
    created_at = factory.LazyAttribute(lambda _: datetime.now(timezone.utc))
    updated_at = factory.LazyAttribute(lambda _: datetime.now(timezone.utc))
