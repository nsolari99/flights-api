from typing import List, Literal
from beanie import Document
from pydantic import BaseModel

class Passenger(BaseModel):
    id: int
    name: str
    hasConnections: bool
    age: int
    flightCategory: Literal["Black", "Platinum", "Gold", "Normal"]
    reservationId: str
    hasCheckedBaggage: bool

class Flight(Document):
    flightCode: str
    passengers: List[Passenger]

    class Settings:
        name = "flights"
        indexes = ["flightCode"]  # unique enforced in service/business validations
