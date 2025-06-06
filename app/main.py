from fastapi import FastAPI
from .api.flights import router as flights_router

app = FastAPI(
    title="Flights API",
    summary="Manage flights & embedded passenger manifests",
)

app.include_router(flights_router)
