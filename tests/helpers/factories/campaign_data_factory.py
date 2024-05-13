import random
from typing import List

import factory
from datetime import datetime, timezone

from common.schemas.visit import VisitStatus
from common.validator.db.entities.active import Campaign, CampaignType
from common.schemas.bitads import Campaign as BitAds_Campaign



class CampaignDataFactory(factory.Factory):
    class Meta:
        model = Campaign

    @classmethod
    def create_batch_with_overrides(cls, **kwargs) -> List[Campaign]:
        """
        Creates a batch of Campaign objects, allowing overrides for specific fields.
        """
        return [cls.build(overrides=kwargs) for _ in range(kwargs.get("size", 1))]

    id = factory.Faker("uuid4")
    status = factory.Faker("boolean")
    last_active_block = factory.Faker("random_int", min=0)
    created_at = factory.LazyAttribute(lambda _: datetime.now())
    updated_at = factory.LazyAttribute(lambda _: datetime.now())
    umax = factory.Faker("pyfloat", positive=True, min_value=0.01, max_value=10.0)
    type = factory.Faker("random_element", elements=list(CampaignType))


class BitAdsCampaignEntityFactory(factory.Factory):
    class Meta:
        model = BitAds_Campaign

    id = factory.Faker("password", length=6, special_chars=False, digits=True, upper_case=False, lower_case=True)
    in_progress = factory.Faker("random_int", min=0, max=1)
    product_title = factory.Faker("sentence")
    created_at = factory.LazyAttribute(lambda _: datetime.now(timezone.utc))
    is_aggregate = factory.Faker("random_int", min=0, max=1)
    product_unique_id = factory.Faker("password", length=12, special_chars=False, digits=True, upper_case=False,
                                      lower_case=True)
    validator_id = factory.Faker("random_int", min=0, max=10000)
    status = factory.LazyFunction(lambda: random.choice(list(VisitStatus)).value)
    product_button_link = factory.Faker("ipv4")
    date_end = factory.Faker("future_datetime", end_date="+30d")
    product_count_day = factory.Faker("random_int", min=0, max=10)
    updated_at = factory.LazyAttribute(lambda _: datetime.now(timezone.utc))
    product_short_description = factory.Faker("text", max_nb_chars=100)
    product_full_description = factory.Faker("text", max_nb_chars=300)
    product_button_text = factory.Faker("password", length=45, special_chars=False, digits=True, upper_case=False,
                                        lower_case=True)
    product_images = factory.Faker("image_url")
    product_theme = factory.Faker("country_code")
    type = factory.LazyFunction(lambda: random.choice(list(CampaignType)).value)
    umax = factory.Faker("pyfloat", positive=True)
