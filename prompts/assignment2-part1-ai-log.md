# Assignment 2, Part 1 — AI disclosure and evidence log

## Tool and model disclosure

| Tool or model | Use |
| --- | --- |
| Codex (GPT-5) | Planned the MVC structure, drafted the code and documentation, reviewed test output, and explained implementation choices. |
| Codex terminal and file-editing tools | Read the repository, created and updated the backend, frontend, tests, documentation, and local configuration example. |
| Codex browser automation | Verified the live running application with ZIP `16801`; confirmed the live hotel list, Leaflet map, map controls, and 5 km circle. |
| OpenAI Image Generation | Created the early annotated mockup at `docs/mockups/assignment2-part1-hotel-search-mockup.png`. |
| Geoapify documentation and live API | Consulted Geoapify Geocoding and Places documentation; live API supplied ZIP locations and hotel records during browser verification. |

## Selected prompt excerpts and evidence

| Prompt excerpt / decision | Evidence and resulting work |
| --- | --- |
| “FastAPI uses Geoapify to resolve [the ZIP] … and obtain hotels within 5 km of the returned point.” | Implemented exact ZIP validation in `backend/controllers/location_controller.py` and 5 km `accommodation.hotel` circle searching in `backend/controllers/nearby_hotels_controller.py`. |
| “Selecting a hotel in either representation identifies the same hotel in the other.” | Added shared Vue selected-index behavior and Leaflet marker click handling in `frontend/src/main.js`. |
| “No invented prices, ratings, room availability, or booking confirmations are permitted.” | The response contract and frontend render only provider-derived name, address, latitude, and longitude. See `docs/api-contract.md` and `frontend/src/main.js`. |
| 
| Failed/revised approach: Leaflet initially displayed a blank map panel in browser testing. | The hotel list proved that the live API worked; the Leaflet CDN tags’ integrity metadata prevented the library/styles from rendering. `frontend/index.html` was revised to use the version-pinned Leaflet CDN links without those incorrect integrity attributes. After a refresh, ZIP `16801` showed 15 hotels, an interactive map, markers, zoom controls, and the 5 km circle. |

## Human review

I reviewed the mockup, supplied the local Geoapify key, selected the
live ZIP test, provided the leaflet map. Checked everything if it was working correctly.
