"""Script to seed the database with initial data."""
import asyncio
import json
import os
from pathlib import Path

from app.core.database import init_db
from app.models.flight import Flight, Passenger


async def load_passengers(file_path: str) -> list[Passenger]:
    """Load passengers from a JSON file."""
    try:
        with open(file_path, "r") as f:
            passengers_data = json.load(f)
        
        return [Passenger(**passenger) for passenger in passengers_data]
    except Exception as e:
        print(f"Error loading passengers: {e}")
        return []


async def create_flights(passengers: list[Passenger], num_flights: int = 5) -> None:
    """Create flights with passengers."""
    # Generate flight codes
    airlines = ["AA", "DL", "UA", "BA", "LH", "AF", "IB", "EK"]
    flight_codes = [f"{airlines[i % len(airlines)]}{100 + i}" for i in range(num_flights)]
    
    # Distribute passengers among flights
    passengers_per_flight = len(passengers) // num_flights
    flights = []
    
    for i, code in enumerate(flight_codes):
        start_idx = i * passengers_per_flight
        end_idx = start_idx + passengers_per_flight if i < num_flights - 1 else len(passengers)
        
        flight = Flight(
            flightCode=code,
            passengers=passengers[start_idx:end_idx]
        )
        flights.append(flight)
    
    # Insert flights into the database
    for flight in flights:
        await flight.insert()
        print(f"Created flight {flight.flightCode} with {len(flight.passengers)} passengers")


async def seed_database():
    """Seed the database with initial data."""
    print("Initializing database connection...")
    await init_db()
    
    # Check if flights collection is empty
    flights_count = await Flight.count()
    if flights_count > 0:
        print(f"Database already contains {flights_count} flights. Skipping seeding.")
        return
    
    # Load passengers from JSON file
    project_root = Path(__file__).parent.parent.parent
    passengers_file = os.path.join(project_root, "passengers_20.json")
    
    print(f"Loading passengers from {passengers_file}...")
    passengers = await load_passengers(passengers_file)
    
    if not passengers:
        print("No passengers loaded. Exiting.")
        return
    
    print(f"Loaded {len(passengers)} passengers")
    
    # Create flights with passengers
    print("Creating flights...")
    await create_flights(passengers)
    
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
