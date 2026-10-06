# Assignment 2, Part 1 handoff

## Completed

- Research notes and an early ZIP-search/list/map mockup.
- Backend-only Geoapify configuration through local `.env` and a committed
  `.env.example` without secrets.
- Exact U.S. ZIP geocoding followed by a live Geoapify Places hotel search
  within 5 km of the resolved ZIP center.
- Vue list and Leaflet map with synchronized hotel selection.
- Screen-recorded Part 1 demo saved as `docs/assignment2-part1-demo.mp4` and
  linked from `report.md`.
- Clear invalid-input, loading, unresolved-ZIP, no-results, and service-failure
  states.

## Checked

The full unit suite contains 11 passing tests. Live browser verification for
ZIP `16801` displayed 15 nearby hotels, a map, marker controls, and the 5 km
search circle.

## Next task

Part 2 can add the persistent shortlist to the existing live-search result
model without moving the Geoapify key into the frontend.
