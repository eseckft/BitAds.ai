from os import environ


class Environ:
    ACTIVE_DB_URL = environ.get(
        "ACTIVE_DB_URL", "sqlite+aiosqlite:///validator_active.db"
    )
    HISTORY_DB_URL = environ.get(
        "HISTORY_DB_URL", "sqlite+aiosqlite:///validator_history.db"
    )
