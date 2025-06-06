---
trigger: manual
---

# ✈️ Flights‑API Agentic LLM Instructions

> **Stack**  Python 3.12 • FastAPI • MongoDB 7 • Motor/Beanie • Poetry
>
> **Goal**  Provide a clear, reproducible project skeleton so an Agentic LLM (or any developer) can spin up the API, understand its architecture, and extend it while following modern Python clean‑code practices.

## 1. Project Structure

```text
/flights-api
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml          # managed by Poetry
├── .env*
├── app
│   ├── core
│   │   ├── config.py       # Pydantic settings
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

> **Why Schemas + Models?**  We keep persistence models (Beanie `Document`) isolated from request/response DTOs to obey **SRP** and allow future DB swaps.

---

## 2. Core Components

### 2.1 Models – `app/models/flight.py`

```python
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
```

### 2.2 Router – `app/routers/flights.py`

```python
from fastapi import APIRouter, HTTPException, status
from app.models.flight import Flight
from typing import List

router = APIRouter(prefix="/flights", tags=["Flights"])

@router.post("/", response_model=Flight, status_code=status.HTTP_201_CREATED)
async def create_flight(flight: Flight):
    await flight.insert()
    return flight

@router.get("/", response_model=List[Flight])
async def list_flights():
    return await Flight.find_all().to_list()

@router.get("/{id}", response_model=Flight)
async def get_flight(id: str):
    flight = await Flight.get(id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight

@router.patch("/{id}", response_model=Flight)
async def update_flight(id: str, data: dict):
    flight = await Flight.get(id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    await flight.set(data)
    return flight

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flight(id: str):
    flight = await Flight.get(id)
    if flight:
        await flight.delete()
```

### 2.3 Service Skeleton – `app/services/flight_service.py`

```python
"""Thin domain layer so controllers stay lean
and business rules remain testable in isolation."""
from typing import List
from beanie import PydanticObjectId
from app.models.flight import Flight

async def fetch_all() -> List[Flight]:
    return await Flight.find_all().to_list()

# add more business‑specific helpers here
```

---

## 4. Clean‑Code & Architecture Guidelines

### 4.1 DRY & SOLID

* **SRP**: each module does *one* thing (routers ≠ business ≠ persistence).
* **OCP**: new routes or DB back‑ends are added via new modules, not core edits.
* **LSP**: services return base types (`Flight`, DTO) that consumers can rely on.
* **ISP**: routers depend only on needed service functions.
* **DIP**: future: inject repositories via FastAPI Depends for easier mocking.
* **DRY**: shared utils in `app/core`, avoid duplicating validation logic (schemas reused).

### 4.2 Coding‑Style

| Tool      | Purpose                                                        |
| --------- | -------------------------------------------------------------- |
| **Black** | Formatting, 88 cols                                            |
| **Ruff**  | Linting (flake8 + pylint rules)                                |
| **Isort** | Import ordering (but Black handles if using `--profile black`) |
| **mypy**  | Optional static type checks                                    |

* **Docstrings** in Google style, minimal but meaningful.
* Prefer **`async`********/************\*\*\*\*************\*\*\*\*************\*\*\*\*****\*\*\*\*`await`** end‑to‑end (Motor/Beanie already async).
* Return **typed responses** (`response_model`) for FastAPI auto‑docs.
* Handle exceptions centrally (`app.core.exceptions` in future).
* Log structured JSON via `loguru` or stdlib `logging` with `uvicorn --log-config`.
