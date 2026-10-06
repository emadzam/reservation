# Assignment 2, Part 1 — research notes

## Sources and decisions

- [Geoapify Geocoding API](https://apidocs.geoapify.com/docs/geocoding/) supports
  a country-filtered postcode lookup. The backend checks that the response is
  for the exact requested U.S. ZIP so an unresolved ZIP cannot silently become
  a search for a nearby place. A limitation is that the provider may omit a
  place name or formatted address, so the interface uses an explicit
  unavailable label instead of inventing one.
- [Geoapify Places API](https://apidocs.geoapify.com/docs/places/) supports the
  `accommodation.hotel` category and a circle filter in metres. The app uses a
  5,000 meter circle centered on the coordinates returned from the ZIP lookup,
  plus proximity bias for useful ordering.
- [Leaflet](https://leafletjs.com/) provides the map and marker interactions.
  The app keeps one selected-hotel index in view, list cards and marker clicks
  both change that same value, so the two views stay synchronized.
- [OpenStreetMap tile policy](https://operations.osmfoundation.org/policies/tiles/)
  explains that its public tiles are appropriate for light, educational use.
  The map uses visible attribution and no credential. A production deployment
  would need to review the provider policy and likely use a dedicated tile plan.

## Interface choices

The page shows separate messages for invalid input, loading, unresolved ZIP,
no results, and service failure. It displays only the live response’s hotel
name, location label, and coordinates; it deliberately omits ratings, prices,
rooms, and booking language.
