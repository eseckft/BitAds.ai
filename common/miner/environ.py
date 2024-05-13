from os import environ


class Environ:
    ACTIVE_DB_URL = environ.get(
        "MINER_ACTIVE_DB_URL", "sqlite+aiosqlite:///miner_active.db"
    )
    HISTORY_DB_URL = environ.get(
        "MINER_HISTORY_DB_URL", "sqlite+aiosqlite:///miner_history.db"
    )
    PROXY_PORT = environ.get("MINER_PROXY_PORT", 8011)
