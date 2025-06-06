from typing import List, Optional

from bson import ObjectId
from pymongo import ReturnDocument
from fastapi import HTTPException, status

from .database import get_flight_collection
from .models import FlightModel, UpdateFlightModel, PassengerModel
from .priority import sort_passengers, DEFAULT_RULES


async def create_flight(flight: FlightModel) -> FlightModel:
    # Check if we need to apply capacity limits
    if flight.capacity is not None and len(flight.passengers) > flight.capacity:
        # Convert Pydantic models to dictionaries for sorting
        passenger_dicts = [p.model_dump() for p in flight.passengers]
        
        # Sort passengers by priority
        sorted_passenger_dicts = sort_passengers(passenger_dicts, rules=DEFAULT_RULES)
        
        # Keep only the highest priority passengers up to capacity
        limited_passenger_dicts = sorted_passenger_dicts[:flight.capacity]
        
        # Convert dictionaries back to Pydantic models
        flight.passengers = [PassengerModel(**p) for p in limited_passenger_dicts]
        
        # Provide information about dropped passengers
        dropped_count = len(passenger_dicts) - flight.capacity
        print(f"Notice: {dropped_count} passengers dropped due to capacity limits")
    
    # Insert the (potentially modified) flight into the database
    collection = get_flight_collection()
    res = await collection.insert_one(
        flight.model_dump(by_alias=True, exclude=["id"])
    )
    return await collection.find_one({"_id": res.inserted_id})


async def list_flights(limit: int = 1000) -> List[FlightModel]:
    return await get_flight_collection().find().to_list(limit)


async def get_flight(flight_id: str) -> Optional[FlightModel]:
    return await get_flight_collection().find_one({"_id": ObjectId(flight_id)})


async def update_flight(flight_id: str, updates: UpdateFlightModel) -> FlightModel:
    payload = {k: v for k, v in updates.model_dump(by_alias=True).items() if v is not None}
    if not payload:
        raise HTTPException(status_code=400, detail="No fields provided to update.")

    doc = await get_flight_collection().find_one_and_update(
        {"_id": ObjectId(flight_id)},
        {"$set": payload},
        return_document=ReturnDocument.AFTER,
    )
    if doc:
        return doc
    raise HTTPException(status_code=404, detail=f"Flight {flight_id} not found")


async def delete_flight(flight_id: str) -> None:
    result = await get_flight_collection().delete_one({"_id": ObjectId(flight_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Flight {flight_id} not found")
