import uvicorn
from common.miner.environ import Environ

from neurons.miner.__main__ import app


# Entry point for the application
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=Environ.PROXY_PORT,
        ssl_certfile="cert.pem",
        ssl_keyfile="key.pem",
    )
