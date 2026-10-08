# Assignment 2, Part 2 — schema comparison findings

**Observation date:** October 6, 2026
**Tested live ZIP:** `16801` (State College, PA)
**Database file:** `backend/reservation.db`

## Database inspection

The `hotels` table currently contains these columns:

| Column | Type | Notes |
| --- | --- | --- |
| `hotel_id` | TEXT | Local primary key, for example `H001` |
| `hotel_name` | TEXT | Local supplied hotel name |
| `city` | TEXT | City portion of a location |
| `state` | TEXT | State portion of a location |
| `nightly_rate_usd` | REAL | One local sample nightly rate |

Sample rows include `H001 / Harbor Lantern Hotel / Boston / MA / 150.0` and
`H002 / Maple Square Inn / Boston / MA / 120.0`.

Other available tables are `trips`, `users`, and `bookings`. `trips` contains
`check_in` and `check_out`; it is tied to the existing local `hotel_id` records,
not live provider hotels. No table stores room inventory or availability by
hotel and date.

## Live API inspection

The Part 1 endpoint `GET /api/nearby-hotels?zip=16801` returned 15 hotels. One
observed record was:

```json
{
  "id": "5139ed7d...",
  "name": "Ramada State College",
  "address": "Ramada State College, 1450 South Atherton Street, State College, PA 16801, United States of America",
  "latitude": 40.78415615285288,
  "longitude": -77.83974468514943
}
```

The raw Geoapify Places properties included `place_id`, `name`, `formatted`,
`lat`, and `lon`. The response contained no price-, rate-, room-, or
availability-related properties.

## Required field comparison

| API information | Matching database column — or missing | Finding |
| --- | --- | --- |
| Provider hotel ID | **Missing** | `hotels.hotel_id` is a local supplied ID (`H001` etc.), not Geoapify `place_id`. |
| Hotel name | `hotels.hotel_name` | Similar purpose, but current values describe supplied local hotels rather than live provider hotels. |
| Address | **Missing** | `city` and `state` store only parts of a location; there is no full street/formatted address column. |
| Latitude | **Missing** | No latitude column exists. |
| Longitude | **Missing** | No longitude column exists. |

## Price check

The live Geoapify hotel response did **not** supply a nightly price. The
existing `hotels.nightly_rate_usd` is a local Assignment 1 sample value and
does not establish a price for a live provider hotel. A live hotel must not be
given that local price.

## Date, rate, and room-availability storage check

No available table can store a complete live availability record consisting of:

- Provider hotel ID
- Date
- Nightly rate for that date
- Number of rooms available for that date

`trips.check_in` and `trips.check_out` describe pre-seeded local trips, and
`hotels.nightly_rate_usd` is one value per local hotel. They cannot represent
different prices or room counts for different dates. Part 2 therefore needs a
new provider-hotel identity and date-specific availability/pricing storage
relationship rather than reusing one `hotels` table price.
