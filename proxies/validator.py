from fastapi import FastAPI, Depends

from common.validator import dependencies
from common.validator.schemas import TrackingDataSchema
from common.validator.services.track_data.base import TrackingDataService

app = FastAPI()


@app.post("/collect")
async def collect_visit_information(
    tracking_data: TrackingDataSchema,
    tracking_data_service: TrackingDataService = Depends(
        dependencies.get_tracking_data_service
    ),
) -> None:
    await tracking_data_service.add_data(tracking_data)
