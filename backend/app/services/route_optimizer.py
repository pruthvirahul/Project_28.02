from __future__ import annotations

from dataclasses import dataclass

from app.schemas import Offer, RankedOffer


@dataclass(frozen=True)
class Weights:
    price: float = 0.50
    duration: float = 0.30
    layovers: float = 0.20


def _inverse_minmax(value: float, low: float, high: float) -> float:
    if high == low:
        return 1.0
    return round((high - value) / (high - low), 6)


def _first_available(candidates: list[int], used: set[int]) -> int:
    for idx in candidates:
        if idx not in used:
            return idx
    return candidates[0]


def rank_offers(offers: list[Offer], weights: Weights | None = None) -> list[RankedOffer]:
    if not offers:
        return []

    weights = weights or Weights()

    min_price, max_price = min(o.total_fare for o in offers), max(o.total_fare for o in offers)
    min_duration, max_duration = min(o.duration_minutes for o in offers), max(o.duration_minutes for o in offers)
    min_layovers, max_layovers = min(o.layovers for o in offers), max(o.layovers for o in offers)

    scored: list[RankedOffer] = []
    for offer in offers:
        s_price = _inverse_minmax(offer.total_fare, min_price, max_price)
        s_duration = _inverse_minmax(offer.duration_minutes, min_duration, max_duration)
        s_layovers = _inverse_minmax(offer.layovers, min_layovers, max_layovers)
        total = round(
            (s_price * weights.price)
            + (s_duration * weights.duration)
            + (s_layovers * weights.layovers),
            6,
        )

        scored.append(
            RankedOffer(
                **offer.model_dump(),
                label="alternative",
                score_total=total,
                score_price=s_price,
                score_duration=s_duration,
                score_layovers=s_layovers,
            )
        )

    ranked = sorted(scored, key=lambda x: x.score_total, reverse=True)

    by_price = sorted(range(len(ranked)), key=lambda i: ranked[i].total_fare)
    by_duration = sorted(range(len(ranked)), key=lambda i: ranked[i].duration_minutes)

    used: set[int] = set()

    best_idx = 0
    ranked[best_idx].label = "best_value"
    used.add(best_idx)

    cheapest_idx = _first_available(by_price, used)
    ranked[cheapest_idx].label = "cheapest"
    used.add(cheapest_idx)

    fastest_idx = _first_available(by_duration, used)
    ranked[fastest_idx].label = "fastest"

    return ranked
