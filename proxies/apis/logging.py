import os

import bittensor as bt
from bittensor.btlogging.defines import DEFAULT_LOG_FILE_NAME
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/logs")
async def get_logs():
    config = bt.logging.get_config()
    logging_dir = config.logging.logging_dir
    expanded_dir = os.path.expanduser(logging_dir)
    logfile = os.path.abspath(os.path.join(expanded_dir, DEFAULT_LOG_FILE_NAME))
    return FileResponse(logfile)