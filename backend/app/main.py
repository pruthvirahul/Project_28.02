from datetime import datetime

from fastapi import FastAPI

from app.config import settings
from app.schemas import Offer, RouteOptimizeRequest, RouteScoreRequest
from app.services.amadeus import AmadeusClient, RouteQuery
from app.services.route_optimizer import rank_offers

app = FastAPI(title="AI Travel Planner API", version="0.3.0")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "live_provider_enabled": settings.amadeus_enabled,
    }


def _mock_provider_offers(payload: RouteOptimizeRequest) -> list[Offer]:
    sample = [
        Offer(provider="demo-air", transport_mode="flight", total_fare=129.99, duration_minutes=210, layovers=0),
        Offer(provider="demo-rail", transport_mode="train", total_fare=89.00, duration_minutes=340, layovers=0),
        Offer(provider="demo-bus", transport_mode="bus", total_fare=45.00, duration_minutes=540, layovers=0),
        Offer(provider="demo-air-plus", transport_mode="flight", total_fare=179.49, duration_minutes=120, layovers=0),
        Offer(provider="demo-air-connector", transport_mode="flight", total_fare=99.99, duration_minutes=260, layovers=1),
    ]

    return [
        offer
        for offer in sample
        if (payload.mode == "any" or offer.transport_mode == payload.mode)
        and offer.layovers <= payload.max_layovers
    ]


@app.post("/v1/routes/optimize")
async def optimize_route(payload: RouteOptimizeRequest) -> dict:
    live_offers: list[Offer] = []
    source = "mock"

    if payload.mode in ("flight", "any") and settings.amadeus_enabled:
        client = AmadeusClient()
        live_offers = await client.search_flight_offers(
            RouteQuery(
                origin=payload.origin,
                destination=payload.destination,
                departure_date=payload.date,
            )
        )

    offers = live_offers or _mock_provider_offers(payload)
    if live_offers:
        source = "amadeus"

    ranked = rank_offers(offers)
    return {
        "query": payload.model_dump(),
        "source": source,
        "results": [item.model_dump() for item in ranked],
        "note": "Set AMADEUS_API_KEY/AMADEUS_API_SECRET in .env to enable live flight provider.",
    }


@app.post("/v1/routes/score")
def score_route_payload(payload: RouteScoreRequest) -> dict:
    ranked = rank_offers(payload.offers)
    return {"results": [item.model_dump() for item in ranked]}
