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
    currency_code: str = "INR"
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
                    "currencyCode": query.currency_code,
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

            itinerary = itineraries[0]
            segs = itinerary.get("segments", [])
            duration_iso = itinerary.get("duration", "PT0M")
            duration_minutes = _duration_minutes(duration_iso)
            segments = max(len(segs), 1)
            layovers = max(segments - 1, 0)

            price_obj = item.get("price", {})
            price = float(price_obj.get("grandTotal", 0))
            if price <= 0:
                continue

            offers.append(
                Offer(
                    provider="amadeus",
                    transport_mode="flight",
                    total_fare=price,
                    currency=price_obj.get("currency", query.currency_code),
                    duration_minutes=max(duration_minutes, 1),
                    duration_iso=duration_iso,
                    segments=segments,
                    layovers=layovers,
                )
            )

        return offers


def _duration_minutes(iso_duration: str) -> int:
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
