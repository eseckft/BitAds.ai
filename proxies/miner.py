import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse

from common.miner import dependencies
from common.miner.environ import Environ
from common.miner.schemas import VisitorSchema
from common.miner.services.visitors.base import VisitorService

app = FastAPI()


@app.middleware("http")
async def anti_ddos_middleware(request: Request, call_next):
    response = await call_next(request)
    return response


@app.get("/")
async def fetch_request_data_and_redirect(
    request: Request,
    visitor_service: VisitorService = Depends(
        dependencies.get_visitor_service
    ),
):
    # TODO(developer): remove miner ID from request and use correct redirect
    modified_headers = request.headers.mutablecopy()
    visitor = VisitorSchema(
        referrer=request.headers.get("referer", "1"),
        ip_address=request.client.host,
        miner_assigned=request.headers.get("X-Miner-Assigned", "1"),
        target_landing_page=request.query_params.get("landing_page", "d"),
        user_agent=request.headers.get("user-agent"),
        additional_headers=dict(request.headers),
    )
    await visitor_service.add_visitor(visitor)
    return RedirectResponse(
        url="https://example.com", headers=modified_headers
    )


if __name__ == "__main__":
    uvicorn.run(app, port=Environ.PROXY_PORT)
