from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import settings
from app.schemas import Offer


@dataclass(frozen=True)
class RouteQuery:
    origin: str
    destination: str
    departure_date: str
    adults: int = 1


class AmadeusClient:
    async def _get_access_token(self) -> str:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{settings.amadeus_base_url}/v1/security/oauth2/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.amadeus_api_key,
                    "client_secret": settings.amadeus_api_secret,
                },
            )
            response.raise_for_status()
            return response.json()["access_token"]

    async def search_flight_offers(self, query: RouteQuery) -> list[Offer]:
        if not settings.amadeus_enabled:
            return []

        token = await self._get_access_token()
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{settings.amadeus_base_url}/v2/shopping/flight-offers",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "originLocationCode": query.origin,
                    "destinationLocationCode": query.destination,
                    "departureDate": query.departure_date,
                    "adults": query.adults,
                    "max": 5,
                },
            )
            response.raise_for_status()
            payload = response.json().get("data", [])

        offers: list[Offer] = []
        for item in payload:
            itineraries = item.get("itineraries", [])
            if not itineraries:
                continue

            segs = itineraries[0].get("segments", [])
            duration_minutes = _duration_minutes(itineraries[0].get("duration", "PT0M"))
            layovers = max(len(segs) - 1, 0)

            price = float(item.get("price", {}).get("grandTotal", 0))
            if price <= 0:
                continue

            offers.append(
                Offer(
                    provider="amadeus",
                    transport_mode="flight",
                    total_fare=price,
                    duration_minutes=max(duration_minutes, 1),
                    layovers=layovers,
                )
            )

        return offers


def _duration_minutes(iso_duration: str) -> int:
    # Minimal parser for strings like PT2H30M / PT45M / PT10H
    hours = 0
    minutes = 0
    value = iso_duration.replace("PT", "")
    if "H" in value:
        h, value = value.split("H", 1)
        hours = int(h or 0)
    if "M" in value:
        m = value.replace("M", "")
        minutes = int(m or 0)
    return (hours * 60) + minutes
