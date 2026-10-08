# Assignment 2 Part 2 research notes

## Sources consulted

- [OpenAI Responses API](https://developers.openai.com/api/reference/resources/responses/methods/create)
- [OpenAI GPT-6 Luna model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna)
- [Geoapify Geocoding documentation](https://apidocs.geoapify.com/docs/geocoding/)
- [Geoapify Places documentation](https://apidocs.geoapify.com/docs/places/)

## Useful patterns and limitations

OpenAI's Responses API accepts a model, instructions, and text input from the
backend. GPT-6 Luna supports the Responses API and medium reasoning effort. The
selected model stays configurable through `OPENAI_MODEL`, rather than being
hard-coded in the frontend.

Geoapify supplies locations and places, not proof of rooms, rates, or booking
availability. The local SQLite `demo_hotel_nights` records therefore remain
explicitly labeled simulated classroom data.

## Design decisions

- Keep the OpenAI credential and both model requests in FastAPI only.
- Use two model requests: first to propose SQL, second to answer only from the
  checked rows.
- Do not let the model connect to SQLite. `DatabaseController` validates that
  the proposal is one `SELECT`, authorizes reads only from the three Part 2
  local tables, and caps results at 50 rows.
- Return the proposed SQL and retrieved rows in the UI so the workflow can be
  demonstrated and verified.
- Treat missing saved hotels as insufficient data and a valid query with no
  rows as no matches; do not guess hotel, date, rate, or availability details.
