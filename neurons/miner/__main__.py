from typing import Annotated, Optional

import uvicorn
from fastapi import Request, Depends, status, HTTPException, FastAPI
from fastapi.responses import RedirectResponse
from fiber.logging_utils import get_logger
from fiber.miner.endpoints.handshake import factory_router as handshake_factory_router
from fiber.miner.endpoints.subnet import factory_router as get_subnet_router

from common.miner import dependencies
from common.miner.environ import Environ
from common.miner.schemas import VisitorSchema
from common.services.miner.base import MinerService
from neurons.miner.lifespan import lifespan
from neurons.miner.routers.external import router as external_router
from proxies.apis.fetch_from_db_test import router as test_router
from proxies.apis.get_database import router as database_router
from proxies.apis.logging import router as logs_router
from proxies.apis.two_factor import router as two_factor_router
from proxies.apis.version import router as version_router

# Configure the application
app = FastAPI(lifespan=lifespan)
app.version = "0.6.0"


# Include all routers in a modular and readable way
routers = [
    get_subnet_router(),
    version_router,
    test_router,
    logs_router,
    database_router,
    two_factor_router,
    external_router,
    handshake_factory_router(),
]
for router in routers:
    app.include_router(router)


app.mount("/chain", external_router)

# Initialize logger with the appropriate configuration
logger = get_logger(__name__)


# Error handling with clear error response
@app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
async def internal_exception_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error at {request.url.path}: {exc}", exc_info=True)
    return RedirectResponse(url="/error", status_code=status.HTTP_302_FOUND)


# Handler function to fetch visit by ID, with annotated return type
@app.get("/visitors/{id}", response_model=Optional[VisitorSchema])
async def get_visit_by_id(
    id: str,
    miner_service: Annotated[MinerService, Depends(dependencies.get_miner_service)],
) -> Optional[VisitorSchema]:
    visit = await miner_service.get_visit_by_id(id)
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found"
        )
    return visit


# Entry point for the application
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=Environ.PROXY_PORT,
        ssl_certfile="cert.pem",
        ssl_keyfile="key.pem",
    )
