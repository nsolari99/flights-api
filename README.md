# ✈️ Flights API

A modern FastAPI application for managing flights and passengers with MongoDB.

## Tech Stack

- **Python 3.12**: Modern Python features
- **FastAPI**: High-performance web framework
- **MongoDB 7**: NoSQL database
- **Motor/Beanie**: Async MongoDB ODM
- **Poetry**: Dependency management

## Project Structure

```
/flights-api
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml          # managed by Poetry
├── .env
├── app
│   ├── core
│   │   ├── config.py       # Pydantic settings
│   │   └── database.py     # Motor client + Beanie init
│   ├── models              # ODM documents
│   │   └── flight.py
│   ├── schemas             # Pydantic I/O schemas (decouple from DB)
│   │   ├── passenger.py
│   │   └── flight.py
│   ├── routers             # FastAPI routers (1‑per‑aggregate)
│   │   └── flights.py
│   ├── services            # Domain logic (thin layer over models)
│   │   └── flight_service.py
│   ├── health.py           # lightweight healthcheck endpoint
│   └── main.py             # FastAPI instance & router wiring
└── tests
    ├── conftest.py         # fixtures (db, client)
    └── test_flights.py
```

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Running the Application

1. Clone the repository
2. Start the application with Docker Compose:

```bash
docker-compose up
```

The API will be available at http://localhost:8000

- API Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

### Development Setup

1. Install Poetry:
```bash
pip install poetry
```

2. Install dependencies:
```bash
poetry install
```

3. Run MongoDB locally or via Docker:
```bash
docker-compose up -d mongo
```

4. Run the application:
```bash
poetry run uvicorn app.main:app --reload
```

## API Endpoints

- `GET /flights`: List all flights
- `POST /flights`: Create a new flight
- `GET /flights/{id}`: Get a specific flight
- `PATCH /flights/{id}`: Update a flight
- `DELETE /flights/{id}`: Delete a flight
- `GET /health`: Health check endpoint

## Testing

Run tests with pytest:

```bash
poetry run pytest
```

## Architecture

This project follows clean code principles and SOLID design:

- **SRP**: Each module has a single responsibility
- **OCP**: New functionality is added via new modules
- **LSP**: Services return base types that consumers can rely on
- **ISP**: Routers depend only on needed service functions
- **DIP**: Future: inject repositories via FastAPI Depends for easier mocking
- **DRY**: Shared utils in core, avoiding duplicated logic
