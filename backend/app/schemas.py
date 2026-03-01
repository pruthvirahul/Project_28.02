from typing import Literal

from pydantic import BaseModel, Field


TransportMode = Literal["flight", "train", "bus", "any"]


class RouteOptimizeRequest(BaseModel):
    origin: str = Field(..., min_length=3, max_length=5)
    destination: str = Field(..., min_length=3, max_length=5)
    date: str
    mode: TransportMode = "any"
    preferred_currency: str = Field("INR", min_length=3, max_length=3)
    max_layovers: int = Field(2, ge=0, le=4)


class Offer(BaseModel):
    provider: str
    transport_mode: Literal["flight", "train", "bus"]
    total_fare: float = Field(..., gt=0)
    currency: str = Field("INR", min_length=3, max_length=3)
    duration_minutes: int = Field(..., gt=0)
    duration_iso: str = ""
    segments: int = Field(1, ge=1)
    layovers: int = Field(0, ge=0)


class RankedOffer(Offer):
    label: Literal["cheapest", "fastest", "best_value", "alternative"]
    score_total: float
    score_price: float
    score_duration: float
    score_layovers: float


class RouteScoreRequest(BaseModel):
    offers: list[Offer] = Field(..., min_length=1)
