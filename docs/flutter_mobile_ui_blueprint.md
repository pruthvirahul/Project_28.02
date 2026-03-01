# Flutter Mobile UI Blueprint (Travel Search Results)

## Goal
Render `POST /v1/routes/optimize` INR-first response in an elegant card-based mobile UX.

## Suggested screens
1. Search form (Origin, Destination, Date, Mode, Currency)
2. Results list with chips for `best_value`, `cheapest`, `fastest`
3. Offer detail modal

## API contract consumed
Each result item:
- `provider`
- `price`
- `currency`
- `duration`
- `segments`
- `label`
- `score`

## Flutter widget sketch
- `Scaffold`
- `SliverAppBar` (search summary)
- `ListView.builder`
- Custom `OfferCard` with:
  - price headline (₹)
  - duration + segments row
  - provider logo placeholder
  - ranking chip (best value/cheapest/fastest)

## Design notes
- Use Material 3 + dynamic color.
- Keep card elevation subtle and rounded corners (12-16).
- Show `source` badge (`amadeus` vs `mock`) for transparency.
