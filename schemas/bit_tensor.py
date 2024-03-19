import pydantic


class Wallet(pydantic.BaseModel):
    cold_key: str
    hot_key: str
