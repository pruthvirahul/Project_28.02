from datetime import datetime
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="AI Travel Planner API", version="0.1.0")


class RouteOptimizeRequest(BaseModel):
    origin: str = Field(..., min_length=3, max_length=5)
    destination: str = Field(..., min_length=3, max_length=5)
    date: str
    mode: Literal["flight", "train", "bus", "any"] = "any"


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/v1/routes/optimize")
def optimize_route(payload: RouteOptimizeRequest) -> dict:
    # Stub response for MVP wiring/testing before provider integrations are added.
    return {
        "query": payload.model_dump(),
        "results": [
            {
                "label": "cheapest",
                "provider": "demo-provider",
                "price": 129.99,
                "currency": "USD",
                "duration_minutes": 210,
                "layovers": 0,
            },
            {
                "label": "fastest",
                "provider": "demo-provider",
                "price": 189.49,
                "currency": "USD",
                "duration_minutes": 120,
                "layovers": 0,
            },
        ],
        "note": "Stub data. Replace with Aggregation + Optimization services.",
    }
