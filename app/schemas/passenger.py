"""Passenger schema for API requests and responses."""
from typing import Literal
from pydantic import BaseModel, Field


class PassengerBase(BaseModel):
    """Base passenger schema with common fields."""
    
    name: str
    hasConnections: bool
    age: int
    flightCategory: Literal["Black", "Platinum", "Gold", "Normal"]
    reservationId: str
    hasCheckedBaggage: bool


class PassengerCreate(PassengerBase):
    """Schema for creating a new passenger."""
    
    id: int


class PassengerResponse(PassengerBase):
    """Schema for passenger in API responses."""
    
    id: int

    class Config:
        """Pydantic config."""
        
        from_attributes = True
