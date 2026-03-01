from fastapi.testclient import TestClient

from app.main import app
from app.schemas import Offer
from app.services.route_optimizer import rank_offers

client = TestClient(app)


def test_rank_offers_labels_present():
    offers = [
        Offer(provider="p1", transport_mode="flight", total_fare=100, currency="INR", duration_minutes=200, layovers=1),
        Offer(provider="p2", transport_mode="flight", total_fare=90, currency="INR", duration_minutes=240, layovers=0),
        Offer(provider="p3", transport_mode="flight", total_fare=140, currency="INR", duration_minutes=120, layovers=0),
    ]

    ranked = rank_offers(offers)
    labels = {o.label for o in ranked}
    assert "best_value" in labels
    assert "cheapest" in labels
    assert "fastest" in labels


def test_optimize_endpoint_returns_mobile_friendly_inr_results():
    response = client.post(
        "/v1/routes/optimize",
        json={"origin": "HYD", "destination": "CMB", "date": "2026-06-10", "mode": "flight", "preferred_currency": "INR"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) > 0
    assert body["source"] in ("mock", "amadeus")
    assert body["results"][0]["currency"] == "INR"
    assert "duration" in body["results"][0]


def test_score_endpoint_ranks_custom_offers():
    response = client.post(
        "/v1/routes/score",
        json={
            "offers": [
                {"provider": "a", "transport_mode": "flight", "total_fare": 200, "currency": "INR", "duration_minutes": 100, "layovers": 0},
                {"provider": "b", "transport_mode": "flight", "total_fare": 120, "currency": "INR", "duration_minutes": 300, "layovers": 1},
            ]
        },
    )
    assert response.status_code == 200
    assert len(response.json()["results"]) == 2
