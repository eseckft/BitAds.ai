from os import environ


class Environ:
    ACTIVE_DB_URL = environ.get(
        "VALIDATOR_ACTIVE_DB_URL", "sqlite+aiosqlite:///validator_active.db"
    )
    HISTORY_DB_URL = environ.get(
        "VALIDATOR_HISTORY_DB_URL", "sqlite+aiosqlite:///validator_history.db"
    )
    PROXY_PORT = environ.get("VALIDATOR_PROXY_PORT", 8012)
