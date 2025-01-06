import os

import bittensor as bt
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/logs")
async def get_logs():
    config = bt.logging.get_config()
    try:
        logging_dir = config.logging.logging_dir
    except:
        logging_dir = "~/.bittensor/miners"
    expanded_dir = os.path.expanduser(logging_dir)
    logfile = os.path.abspath(os.path.join(expanded_dir, "bittensor.log"))
    return FileResponse(logfile)
