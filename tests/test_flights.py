"""Tests for the flights API endpoints."""
import pytest
from httpx import AsyncClient
from beanie import PydanticObjectId

from app.models.flight import Flight, Passenger


@pytest.fixture
async def sample_flight() -> Flight:
    """Create a sample flight for testing."""
    flight = Flight(
        flightCode="AA123",
        passengers=[
            Passenger(
                id=1,
                name="John Doe",
                hasConnections=False,
                age=30,
                flightCategory="Gold",
                reservationId="RES123",
                hasCheckedBaggage=True
            )
        ]
    )
    await flight.insert()
    return flight


@pytest.mark.asyncio
async def test_create_flight(async_client: AsyncClient):
    """Test creating a new flight."""
    flight_data = {
        "flightCode": "BA456",
        "passengers": [
            {
                "id": 2,
                "name": "Jane Smith",
                "hasConnections": True,
                "age": 25,
                "flightCategory": "Platinum",
                "reservationId": "RES456",
                "hasCheckedBaggage": False
            }
        ]
    }
    
    response = await async_client.post("/flights/", json=flight_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["flightCode"] == "BA456"
    assert len(data["passengers"]) == 1
    assert data["passengers"][0]["name"] == "Jane Smith"
    
    # Verify flight was created in the database
    flight = await Flight.find_one({"flightCode": "BA456"})
    assert flight is not None
    assert flight.flightCode == "BA456"


@pytest.mark.asyncio
async def test_get_flight(async_client: AsyncClient, sample_flight: Flight):
    """Test getting a flight by ID."""
    response = await async_client.get(f"/flights/{sample_flight.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["flightCode"] == sample_flight.flightCode
    assert len(data["passengers"]) == 1
    assert data["passengers"][0]["name"] == "John Doe"


@pytest.mark.asyncio
async def test_get_nonexistent_flight(async_client: AsyncClient):
    """Test getting a flight that doesn't exist."""
    fake_id = str(PydanticObjectId())
    response = await async_client.get(f"/flights/{fake_id}")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Flight not found"


@pytest.mark.asyncio
async def test_list_flights(async_client: AsyncClient, sample_flight: Flight):
    """Test listing all flights."""
    # Create another flight
    await Flight(
        flightCode="LH789",
        passengers=[
            Passenger(
                id=3,
                name="Bob Johnson",
                hasConnections=True,
                age=45,
                flightCategory="Normal",
                reservationId="RES789",
                hasCheckedBaggage=True
            )
        ]
    ).insert()
    
    response = await async_client.get("/flights/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {flight["flightCode"] for flight in data} == {"AA123", "LH789"}


@pytest.mark.asyncio
async def test_update_flight(async_client: AsyncClient, sample_flight: Flight):
    """Test updating a flight."""
    update_data = {
        "flightCode": "AA123-UPDATED"
    }
    
    response = await async_client.patch(f"/flights/{sample_flight.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["flightCode"] == "AA123-UPDATED"
    
    # Verify flight was updated in the database
    updated_flight = await Flight.get(sample_flight.id)
    assert updated_flight.flightCode == "AA123-UPDATED"


@pytest.mark.asyncio
async def test_delete_flight(async_client: AsyncClient, sample_flight: Flight):
    """Test deleting a flight."""
    response = await async_client.delete(f"/flights/{sample_flight.id}")
    
    assert response.status_code == 204
    
    # Verify flight was deleted from the database
    deleted_flight = await Flight.get(sample_flight.id)
    assert deleted_flight is None
