from fastapi import APIRouter, status, Body, Response, HTTPException

from ..models import FlightModel, UpdateFlightModel, PassengerModel
from .. import crud
from ..priority import sort_passengers, DEFAULT_RULES

router = APIRouter(prefix="/flights", tags=["Flights"])

# Create
@router.post(
    "/",
    response_model=FlightModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_flight(flight: FlightModel = Body(...)):
    return await crud.create_flight(flight)

# List all
@router.get(
    "/",
    response_model=list[FlightModel],
    response_model_by_alias=False,
)
async def list_flights():
    return await crud.list_flights()

# Retrieve one
@router.get(
    "/{flight_id}",
    response_model=FlightModel,
    response_model_by_alias=False,
)
async def read_flight(flight_id: str):
    flight = await crud.get_flight(flight_id)
    if flight is None:
        raise HTTPException(status_code=404, detail=f"Flight {flight_id} not found")
    return flight

# Update / replace partial
@router.put(
    "/{flight_id}",
    response_model=FlightModel,
    response_model_by_alias=False,
)
async def update_flight(flight_id: str, updates: UpdateFlightModel = Body(...)):
    return await crud.update_flight(flight_id, updates)

# Delete
@router.delete("/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flight(flight_id: str):
    await crud.delete_flight(flight_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get(
    "/{flight_id}/passengers/priority",
    response_model=list[PassengerModel],
    response_model_by_alias=False,
)
async def passengers_by_priority(
    flight_id: str,
    # ► Optional future: allow client to pick custom ordering
    # order: str = Query("category", description="Comma-separated rule names"),
):
    flight = await crud.get_flight(flight_id)
    if flight is None:
        raise HTTPException(status_code=404, detail=f"Flight {flight_id} not found")

    return sort_passengers(flight["passengers"], rules=DEFAULT_RULES)
