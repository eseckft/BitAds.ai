from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from common.schemas.visitor import VisitorSchema

app = FastAPI()


@app.middleware("http")
async def anti_ddos_middleware(request: Request, call_next):
    response = await call_next(request)
    return response


@app.get("/")
async def fetch_request_data_and_redirect(request: Request):
    # TODO(developer): remove miner ID from request and save data
    modified_headers = request.headers.mutablecopy()
    visitor = VisitorSchema(
        referrer=request.headers.get("referer", "1"),
        ip_address=request.client.host,
        miner_assigned=request.headers.get("X-Miner-Assigned", "1"),
        target_landing_page=request.query_params.get("landing_page", "d"),
        user_agent=request.headers.get("user-agent"),
        additional_headers=dict(request.headers),
    )
    return RedirectResponse(
        url="https://example.com", headers=modified_headers
    )
