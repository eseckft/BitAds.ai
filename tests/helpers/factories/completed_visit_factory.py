import factory
from datetime import datetime
from common.db.entities import CompletedVisit, Device  # Adjust the import according to your actual model location
from sqlalchemy.orm import Session


def create_completed_visit(session: Session, **kwargs):
    CompletedVisitFactory._meta.sqlalchemy_session = session
    return CompletedVisitFactory(**kwargs)


class CompletedVisitFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = CompletedVisit

    id = factory.Faker('uuid4')
    referer = factory.Faker('url')
    ip_address = factory.Faker('ipv4')
    country = factory.Faker('country_code')
    user_agent = factory.Faker('user_agent')
    campaign_id = factory.Faker("password", length=12, special_chars=False, digits=True, upper_case=False, lower_case=True)
    campaign_item = factory.Faker("password", length=12, special_chars=False, digits=True, upper_case=False, lower_case=True)
    miner_hotkey = factory.Faker("password", length=45, special_chars=False, digits=True, upper_case=True, lower_case=True)
    at = factory.Faker('boolean')
    device = factory.Faker('random_element', elements=[device for device in Device])
    is_unique = factory.Faker('boolean')
    return_in_site = factory.Faker('boolean')
    count_image_click = factory.Faker('random_int', min=0, max=100)
    count_mouse_movement = factory.Faker('random_int', min=0, max=1000)
    count_read_more_click = factory.Faker('random_int', min=0, max=100)
    count_through_rate_click = factory.Faker('random_int', min=0, max=100)
    miner_block = factory.Faker('random_int', min=0, max=10000)
    validator_block = factory.Faker('random_int', min=0, max=10000)
    complete_block = factory.Faker('random_int', min=0, max=10000)
    created_at = factory.Faker('date_time_this_year', tzinfo=None)
    sales = factory.Faker('random_int', min=0, max=100)
    sale_amount = factory.Faker("pyfloat", positive=True, min_value=3.0, max_value=3000.0)
    refund = factory.Faker('random_int', min=0, max=10)


    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return super()._create(model_class, *args, **kwargs)
