"""Flight schema for API requests and responses."""
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.passenger import PassengerCreate, PassengerResponse


class FlightBase(BaseModel):
    """Base flight schema with common fields."""
    
    flightCode: str


class FlightCreate(FlightBase):
    """Schema for creating a new flight."""
    
    passengers: List[PassengerCreate] = []


class FlightUpdate(BaseModel):
    """Schema for updating an existing flight."""
    
    flightCode: Optional[str] = None
    passengers: Optional[List[PassengerCreate]] = None


class FlightResponse(FlightBase):
    """Schema for flight in API responses."""
    
    id: str
    passengers: List[PassengerResponse] = []

    class Config:
        """Pydantic config."""
        
        from_attributes = True
