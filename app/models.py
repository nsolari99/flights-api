from typing import List, Optional, Literal, Annotated
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict
from pydantic.functional_validators import BeforeValidator

# --- MongoDB ObjectId bridge ----------------------------------------------
PyObjectId = Annotated[str, BeforeValidator(str)]


class PassengerModel(BaseModel):
    """Embedded sub-document for a passenger record."""
    id: int
    name: str
    hasConnections: bool
    age: int
    flightCategory: Literal["Black", "Platinum", "Gold", "Normal"]
    reservationId: str
    hasCheckedBaggage: bool


class FlightModel(BaseModel):
    """Top-level flight document."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    flightCode: str
    passengers: List[PassengerModel]
    capacity: Optional[int] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "flightCode": "LA040",
                "passengers": [
                    {
                        "id": 1,
                        "name": "María Perez",
                        "hasConnections": False,
                        "age": 34,
                        "flightCategory": "Gold",
                        "reservationId": "ABC123",
                        "hasCheckedBaggage": True,
                    }
                ],
                "capacity": 150,
            }
        },
    )


class UpdateFlightModel(BaseModel):
    """Sparse update – only supply fields you want to change."""
    flightCode: Optional[str] = None
    passengers: Optional[List[PassengerModel]] = None
    capacity: Optional[int] = None

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "flightCode": "LA041",
                "passengers": "…same shape as above but optional…",
            }
        },
    )
