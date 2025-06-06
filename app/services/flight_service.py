"""Thin domain layer so controllers stay lean
and business rules remain testable in isolation."""
import logging
from typing import List, Optional, Dict, Any

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.models.flight import Flight
from app.schemas.flight import FlightCreate, FlightUpdate, FlightResponse
from app.schemas.passenger import PassengerResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

# Get MongoDB client and collection
client = AsyncIOMotorClient(settings.mongodb_url)
db = client.get_default_database()
flights_collection = db[Flight.Settings.name]


def convert_to_api_response(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB document to API response format."""
    # Convert top-level ObjectId to string
    if '_id' in doc:
        doc['id'] = str(doc['_id'])
        del doc['_id']
    elif 'id' in doc and isinstance(doc['id'], ObjectId):
        doc['id'] = str(doc['id'])
    
    # Convert passenger ObjectIds to strings if present
    if 'passengers' in doc and isinstance(doc['passengers'], list):
        for passenger in doc['passengers']:
            if '_id' in passenger:
                passenger['id'] = str(passenger['_id'])
                del passenger['_id']
            elif 'id' in passenger and isinstance(passenger['id'], ObjectId):
                passenger['id'] = str(passenger['id'])
    
    return doc


async def fetch_all() -> List[Dict[str, Any]]:
    """Fetch all flights from the database."""
    try:
        # Fetch all flights directly from MongoDB
        cursor = flights_collection.find({})
        flights_data = await cursor.to_list(length=None)
        
        # Convert MongoDB documents to API response format
        flights = []
        for doc in flights_data:
            # Convert the document to API response format
            api_doc = convert_to_api_response(doc)
            flights.append(api_doc)
            
        logger.debug(f"Fetched {len(flights)} flights")
        return flights
    except Exception as e:
        logger.error(f"Error fetching all flights: {e}", exc_info=True)
        raise


async def fetch_by_id(id: str) -> Optional[Dict[str, Any]]:
    """Fetch a flight by its ID."""
    try:
        # Convert ID to ObjectId if it's a string
        object_id = ObjectId(id) if isinstance(id, str) else id
        
        # Fetch flight directly from MongoDB
        doc = await flights_collection.find_one({"_id": object_id})
        if not doc:
            logger.debug(f"Flight with ID {id} not found")
            return None
            
        # Convert the document to API response format
        api_doc = convert_to_api_response(doc)
        
        logger.debug(f"Fetched flight: {api_doc['flightCode']}, ID: {api_doc['id']}")
        return api_doc
    except Exception as e:
        logger.error(f"Error fetching flight by ID {id}: {e}", exc_info=True)
        raise


async def fetch_by_flight_code(flight_code: str) -> Optional[Dict[str, Any]]:
    """Fetch a flight by its flight code."""
    try:
        # Fetch flight directly from MongoDB
        doc = await flights_collection.find_one({"flightCode": flight_code})
        if not doc:
            logger.debug(f"Flight with code {flight_code} not found")
            return None
            
        # Convert the document to API response format
        api_doc = convert_to_api_response(doc)
        
        logger.debug(f"Fetched flight by code: {api_doc['flightCode']}, ID: {api_doc['id']}")
        return api_doc
    except Exception as e:
        logger.error(f"Error fetching flight by code {flight_code}: {e}", exc_info=True)
        raise


async def create_flight(flight_data: FlightCreate) -> Dict[str, Any]:
    """Create a new flight."""
    try:
        # Check if flight code already exists
        existing = await fetch_by_flight_code(flight_data.flightCode)
        if existing:
            logger.debug(f"Flight with code {flight_data.flightCode} already exists")
            raise ValueError(f"Flight with code {flight_data.flightCode} already exists")
        
        # Convert flight data to dict
        flight_dict = flight_data.model_dump()
        
        # Insert directly into MongoDB
        result = await flights_collection.insert_one(flight_dict)
        
        # Fetch the created flight to return it
        created_flight = await fetch_by_id(str(result.inserted_id))
        logger.debug(f"Created flight: {created_flight['flightCode']}, ID: {created_flight['id']}")
        return created_flight
    except Exception as e:
        if not isinstance(e, ValueError):
            logger.error(f"Error creating flight: {e}", exc_info=True)
        raise


async def update_flight(id: str, flight_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update an existing flight."""
    try:
        logger.debug(f"Attempting to update flight with ID: {id}, data: {flight_data}")
        flight = await fetch_by_id(id)
        if not flight:
            logger.debug(f"Flight with ID {id} not found")
            return None
        
        # If updating flight code, check for uniqueness
        if "flightCode" in flight_data and flight_data["flightCode"] != flight['flightCode']:
            existing = await fetch_by_flight_code(flight_data["flightCode"])
            if existing:
                logger.debug(f"Flight with code {flight_data['flightCode']} already exists")
                raise ValueError(f"Flight with code {flight_data['flightCode']} already exists")
        
        # Convert ID to ObjectId if it's a string
        object_id = ObjectId(id) if isinstance(id, str) else id
        
        # Update the document directly
        await flights_collection.update_one({"_id": object_id}, {"$set": flight_data})
        
        # Fetch the updated flight
        updated_flight = await fetch_by_id(id)
        logger.debug(f"Flight updated successfully: {updated_flight['flightCode']}")
        return updated_flight
    except Exception as e:
        if not isinstance(e, ValueError):
            logger.error(f"Error updating flight: {e}", exc_info=True)
        raise


async def delete_flight(id: str) -> bool:
    """Delete a flight by its ID."""
    try:
        logger.debug(f"Attempting to delete flight with ID: {id}")
        flight = await fetch_by_id(id)
        if not flight:
            logger.debug(f"Flight with ID {id} not found")
            return False
            
        logger.debug(f"Flight found: {flight['flightCode']}, ID: {flight['id']}")
        
        # Convert ID to ObjectId if it's a string
        object_id = ObjectId(id) if isinstance(id, str) else id
        
        # Delete the document directly
        result = await flights_collection.delete_one({"_id": object_id})
        logger.debug(f"Delete result: {result.deleted_count} document(s) deleted")
        
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting flight: {e}", exc_info=True)
        raise
