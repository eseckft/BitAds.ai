import datetime

from faker import Faker

faker = Faker()
Faker.seed(datetime.datetime.now().timestamp())

class StingGenerationHelper:
    def __init__(self):
        pass
    def get_random_string(self, length):
        import random
        import string
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def get_random