# Assignment 2 Part 2 early chatbot mockup

Prepared before chatbot implementation. It extends the Part 1 search/list/map
mockup with the locally grounded question area.

```text
┌──────────────────────────────── Nearby Hotel Search ────────────────────────────────┐
│ ZIP [ 16801 ] [Search]                                                               │
│ Saved locally / API results                                                          │
│                                                                                      │
│ Ask about saved hotels                                                               │
│ [ Which saved hotel has rooms on October 12?                              ]          │
│ [Ask question]                                                                       │
│                                                                                      │
│ Answer: ...                                                                          │
│ ▸ Show checked SQL and retrieved records                                             │
│                                                                                      │
│ Hotels with Add to Local / Remove from Local             Map                         │
│ Saved results show simulated classroom rate and rooms per date                       │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

The implemented design keeps the early mockup's disclosure area but adds clear
loading, insufficient-data, no-match, and provider-failure feedback. It also
uses a collapsible evidence section rather than placing SQL and JSON in every
hotel card.
