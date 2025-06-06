"""Flights router module."""
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends
from app.models.flight import Flight
from app.schemas.flight import FlightCreate, FlightResponse, FlightUpdate
from app.services import flight_service

router = APIRouter(prefix="/flights", tags=["Flights"])


@router.post("/", response_model=FlightResponse, status_code=status.HTTP_201_CREATED)
async def create_flight(flight_data: FlightCreate):
    """Create a new flight."""
    try:
        flight_dict = await flight_service.create_flight(flight_data)
        return flight_dict
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[FlightResponse])
async def list_flights():
    """List all flights."""
    flights = await flight_service.fetch_all()
    return flights


@router.get("/{id}", response_model=FlightResponse)
async def get_flight(id: str):
    """Get a flight by ID."""
    flight_dict = await flight_service.fetch_by_id(id)
    if not flight_dict:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight_dict


@router.patch("/{id}", response_model=FlightResponse)
async def update_flight(id: str, data: Dict[str, Any]):
    """Update a flight by ID."""
    try:
        flight_dict = await flight_service.update_flight(id, data)
        if not flight_dict:
            raise HTTPException(status_code=404, detail="Flight not found")
        return flight_dict
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flight(id: str):
    """Delete a flight by ID."""
    success = await flight_service.delete_flight(id)
    if not success:
        raise HTTPException(status_code=404, detail="Flight not found")
