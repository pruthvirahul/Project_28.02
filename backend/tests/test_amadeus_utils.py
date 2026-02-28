from app.services.amadeus import _duration_minutes


def test_duration_parser_hours_and_minutes():
    assert _duration_minutes("PT2H30M") == 150


def test_duration_parser_minutes_only():
    assert _duration_minutes("PT45M") == 45
