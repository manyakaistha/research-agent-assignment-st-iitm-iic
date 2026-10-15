# Additional live runs and default providers

Two additional successful real live retrieval + Gemini generation runs: **TECHM** and **COFORGE**. With the earlier **WIPRO** run, three real NSE tickers have been demonstrated. Each brief is saved exactly as generated and independently reviewed.

| Ticker | Retrieved results period | Publication | Generation | Brief |
|---|---|---|---|---|
| TECHM | Quarter ended 2026-09-30 (Q2 FY27) | 2026-10-15 | Auto → Gemini 2.5 Flash, model | [brief](techm/brief.md) |
| COFORGE | Quarter ended 2026-06-30 (Q1 FY27) | 2026-07-27 | Auto → Gemini 2.5 Flash, model | [brief](coforge/brief.md) |
| WIPRO (previous preserved run) | Quarter ended 2026-09-30 (Q2 FY27) | 2026-10-15 | Gemini 2.5 Flash, model | [brief](../live_bonus/wipro_brief.md) |

TECHM and COFORGE audits sit next to the briefs; each audit points to immutable raw snapshots, normalized evidence, URL/time/date/identity/hash provenance, request/visible response and exact generated output. [Independent review](independent_review.md) accepted all 19 entries in the two new briefs. [Final verification](final_verification.json) and [55-test output](tests_final.txt) retain checks. Actual local run date was 2026-10-16 (Asia/Kolkata). Coforge covers an earlier quarter; it is not presented as current/latest results.

Provider defaults: local SRVCABLE → Groq; --live-data → Gemini. Explicit provider overrides remain supported; missing workflow credentials use offline instead of switching APIs. Two new local Groq calls returned drafts that validation rejected; both fell back explicitly. The original accepted Groq SRVCABLE artifact is unchanged.

What we learned: Tech Mahindra's INR, USD reported and USD constant-currency growth rates describe different measurement bases, not a conflict. Coforge's strong reported revenue/profit growth does not establish a bear case from the same press release; the brief says evidence is insufficient. Dates, currencies and period scope matter as much as numeric citation checks. Both briefs are source-grounded research summaries, not recommendations.

Persistent was attempted but its production fetch returned an access-challenge redirect; no successful Persistent brief is claimed. Earlier successful discovery snapshots and all failed attempts remain. No challenge was bypassed. Full commands, corrections and limitations are in ../../TEST_LOG.md and ../../README_AGENT.md.
