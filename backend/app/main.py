from datetime import datetime

from fastapi import FastAPI

from app.config import settings
from app.schemas import Offer, RouteOptimizeRequest, RouteScoreRequest
from app.services.amadeus import AmadeusClient, RouteQuery
from app.services.route_optimizer import rank_offers

app = FastAPI(title="AI Travel Planner API", version="0.4.0")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "live_provider_enabled": settings.amadeus_enabled,
        "default_currency": "INR",
    }


def _mock_provider_offers(payload: RouteOptimizeRequest) -> list[Offer]:
    sample = [
        Offer(provider="demo-air", transport_mode="flight", total_fare=8200.0, currency="INR", duration_minutes=210, duration_iso="PT3H30M", segments=1, layovers=0),
        Offer(provider="demo-air-plus", transport_mode="flight", total_fare=10500.0, currency="INR", duration_minutes=120, duration_iso="PT2H", segments=1, layovers=0),
        Offer(provider="demo-air-connector", transport_mode="flight", total_fare=7600.0, currency="INR", duration_minutes=260, duration_iso="PT4H20M", segments=2, layovers=1),
    ]
    return [o for o in sample if o.layovers <= payload.max_layovers]


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
                currency_code=payload.preferred_currency.upper(),
            )
        )

    offers = live_offers or _mock_provider_offers(payload)
    if live_offers:
        source = "amadeus"

    ranked = rank_offers(offers)
    mobile_results = [
        {
            "provider": r.provider,
            "price": f"{r.total_fare:.2f}",
            "currency": r.currency,
            "duration": r.duration_iso or f"PT{r.duration_minutes}M",
            "segments": r.segments,
            "label": r.label,
            "score": r.score_total,
        }
        for r in ranked
    ]

    return {
        "query": payload.model_dump(),
        "source": source,
        "results": mobile_results,
        "note": "INR-first mobile response. Set AMADEUS_API_KEY/AMADEUS_API_SECRET in backend/.env for live fares.",
    }


@app.post("/v1/routes/score")
def score_route_payload(payload: RouteScoreRequest) -> dict:
    ranked = rank_offers(payload.offers)
    return {"results": [item.model_dump() for item in ranked]}
