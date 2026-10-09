# Assignment 2 — Part 2: Persistent Shortlist and Grounded Hotel Chatbot

## Project access

- Repository: [github.com/emadzam/reservation](https://github.com/emadzam/reservation)
- Assessed implementation commit: `7b91a6b4d414eb31eae0687efe79a16153b06740`.
- Startup and configuration: [README.md](README.md)
- API contract: [docs/api-contract.md](docs/api-contract.md)

Create a local `.env` from `.env.example`. Configure `GEOAPIFY_API_KEY` for
Part 1 live searches and `OPENAI_API_KEY` for the Part 2 chatbot. Both
stay in `.env`, which is ignored by Git. Start FastAPI and serve `frontend/`
on port 5173 as described in the README.

## Research notes

Sources, observed limitations, and resulting design choices are in
[docs/assignment2-part2-research.md](docs/assignment2-part2-research.md).

The design keeps Geoapify data separate from simulated course data. It uses two
backend-only model requests: an SQL proposal, then a grounded answer using only
checked SQLite records. The model has no direct database access.

## Early mockup

[View the early Part 2 chatbot mockup](docs/mockups/assignment2-part2-chatbot-mockup.md).

It extends the earlier search/list/map layout with a saved-hotel question area,
an answer state, and a collapsible checked-SQL/retrieved-records panel. The
implemented interface adds explicit loading, insufficient-data, no-match, and
provider-failure feedback.

## Screen-recorded demo video

[Watch the Assignment 2 Part 2 demonstration](docs/assignment2-part2-demo.mp4).
It shows API results, Add to Local, stored local results after refresh, one
grounded chatbot answer with its SQL and retrieved records, the simulated-data
labels, and Remove from Local.

## Verification record

| Date | Input or action | Expected result | Observed result | Correction or limitation |
| --- | --- | --- | --- | --- |
| 2026-10-08 | ZIP `16801`, no saved local match | API results label and live hotel list/map | 15 API results appeared in the browser | Live results can change with Geoapify data. |
| 2026-10-08 | Add one API hotel locally | One saved hotel, ZIP context, and Oct. 10–14 demo nights | Record, association, and five rows with 10000 cents / 20 rooms were observed | Rates and room counts are simulated course data. |
| 2026-10-08 | Refresh and repeat ZIP `16801` | Saved-local result, no live provider lookup needed | Saved locally label, one local card, and five dated rows appeared | Local results are a saved subset, not a complete area inventory. |
| 2026-10-08 | Select local hotel card | Matching map marker and popup become selected | List selection opened the matching map popup | None. |
| 2026-10-08 | Remove from Local | Selected hotel, context, and five demo nights are deleted; Assignment 1 records remain | Local Part 2 tables returned to zero rows; Assignment 1 counts remained 8 hotels, 12 trips, 6 users, 6 bookings | None. |
| 2026-10-08 | Fixed successful chatbot fixture | Two model calls, checked SELECT, bounded records, grounded answer | Automated test passed | Fixture is a labeled mock, not a live model call. See [success fixture](docs/fixtures/hotel-chat-success.json). |
| 2026-10-08 | Fixed invalid-query fixture (`DELETE`) | Proposal rejected before SQLite execution | Automated test passed and saved row remained | Fixture is a labeled failure mock. See [invalid fixture](docs/fixtures/hotel-chat-invalid-query.json). |
| 2026-10-08 | Fixed no-match fixture | Checked `SELECT` returns no rows and the second model call answers from that empty result | Automated test passed with `status: no_matches` and zero records | This is a labeled mock. See [no-match fixture](docs/fixtures/hotel-chat-no-match.json). |
| 2026-10-08 | Fixed OpenAI rate-limit fixture | A simulated HTTP 429 produces clear feedback without consuming quota | Automated test passed; no real provider request or database write occurred | This is a labeled mock. See [rate-limit fixture](docs/fixtures/hotel-chat-rate-limit.json). |
| 2026-10-08 | Fixed OpenAI provider-failure fixture | A simulated provider outage produces clear feedback without a database write | Automated test passed; no real provider request or database write occurred | This is a labeled mock. See [provider-failure fixture](docs/fixtures/hotel-chat-provider-failure.json). |
| 2026-10-08 | Live OpenAI chatbot call after saving a local hotel | Provider returns a checked-SQL, grounded answer from saved data | A successful answer appeared in the browser after the response budget was increased; the UI exposed the proposed SQL and retrieved records | The answer is limited to saved hotels and simulated classroom records; it is not a complete hotel inventory. |

Repeat the deterministic chatbot checks:

```powershell
$env:TEMP="$PWD\.test-temp"; $env:TMP="$PWD\.test-temp"
.venv\Scripts\python.exe -m unittest backend.test_hotel_chat backend.test_openai_controller -v
```

## AI disclosure and evidence log

| Tool or model | Use |
| --- | --- |
| Codex (GPT-5) | Planned the MVC workflow, implemented backend/frontend changes, wrote tests and documentation, and reviewed verification output. |
| Codex terminal and browser tools | Inspected code, tested local endpoints, verified the browser’s local-storage behavior, and ran automated checks. |
| OpenAI Responses API / GPT-6 Luna | Backend-only provider for the required two-request SQL-proposal and grounded-answer workflow. It uses `OPENAI_API_KEY` and `OPENAI_MODEL` from `.env`. |
| Geoapify | Supplies Part 1 ZIP and nearby-place data only; it does not supply the demo rates or room counts. |

Selected prompt evidence:

- “Generate and execute a focused query”: implemented in
  [hotel_chat_controller.py](backend/controllers/hotel_chat_controller.py) and
  [database_controller.py](backend/controllers/database_controller.py), with
  SQL validation, SQLite read authorization, and a 50-row cap.
- “Augment the answer with retrieved records”: the second provider request
  receives only the checked result rows, not database access.
- Failed/revised approach: an initial test run used the sandbox's default
  temporary directory and could not create temporary SQLite files. The checks
  were rerun with a workspace-local `.test-temp` directory; all application
  tests then passed. The first live model request returned an empty response,
  so the protected response budgets were increased before the successful
  browser verification.
