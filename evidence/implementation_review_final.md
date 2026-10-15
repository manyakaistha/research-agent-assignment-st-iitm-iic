# R2 final independent implementation review

Status: the six original counterexamples are fixed at their original acceptance criteria; all 22 tests pass. No new blocker to the assignment's core runnable local-document workflow was found. Approval remains conditional on accurate limitation wording and separate A3 review of final generated prose. Semantic correctness is not guaranteed by the automated validator.

Director/reviewer: `/root`; implementation integration: director and I2. This review changed only this report. Original negative report and `tests/test_review.py` remain preserved. Reviewed code SHA-256: `76eebd75ba8e1032cb62c153e0402a3c906837e01056ad1399067402788f5df8`; prompt: `044412b464149e78794f21436995d5ebda67f6535b73c0e7e549d2d13da78fae`; unchanged R1 test file: `8c25e0de9c084be8d26477fd860f9927f1a725d9b44b2f01b3e14311f1cb750f`.

## Checks actually run

Read latest `orchestrator.py`, `system_prompt.md`, all three test modules, and README limitation/live references. Ran `python3 -m unittest discover -s tests -v`: 22/22 passed in 0.127 seconds. This includes an actual ephemeral localhost HTTP gateway; no external API or live URL was called. Live-retrieval tests mock DNS and HTTP. Additional probes below run in memory against the supplied source pack; originals untouched.

## Original findings: resolution

- **Unrelated quote / false copper assertion:** rejected by selected-evidence topic and negation checks. Evidence IDs map to a locally generated catalog, and every cited source must contribute selected evidence. The old source/quote form remains supported, so passing tests do not merely reflect a schema change.
- **PAT value transferred from revenue and negative sign:** rejected by topic and sign checks against selected evidence, rather than all source numbers. Original regression passes unchanged.
- **Late same-period correction:** detected using explicit reporting period, replacing the arbitrary 14-day publication window.
- **Different quarters:** explicit calendar-quarter context now distinguishes January–March and April–June; original false-conflict test passes.
- **Unrelated company explicitly disclaiming association:** excluded before positive alias matching. The new condition addresses the reproduced case; entity detection remains heuristic.
- **Artifacts written inside input directory named `runs`:** computed artifact path is checked, relocated outside the source root, and checked again. Original directory-set comparison passes.

No acceptance gate was weakened to make these six tests pass. Existing fallback, metadata, corpus limits, hash immutability, blog quarantine, unrelated-entity exclusion, and supplied pack conflict/pledge checks still pass.

## Changed functionality

The fictional-ticker live gate runs before ingestion/retrieval. Tests cover SRVCABLE with either live flag and real tickers without explicit opt-in, asserting the fetch function is never called. Real-ticker live mode requires `--live-data` and 1–5 explicit URLs; HTTPS/public DNS addresses, no redirects, file size/content type, UTF-8, required metadata, source dates, duplicate handling and combined corpus size are checked. Provenance metadata URLs remain inert. This is a bounded Markdown fetch tool, not broad search, HTML/PDF parsing or evidence authentication.

The keyless gateway integration test confirms `/v1/chat/completions`, configured model, absent Authorization and absent tool calls. An invalid `{}` response now receives “Model validation failed” and labeled offline fallback because schema is validated before rendering. Generic extra financial conflicts and intended-versus-filed appeal checks pass their focused tests.

## Residual findings

1. **Material known limitation — lexical checks are not entailment.** With the latest schema, claim `Q1 FY27 EBITDA margin was 12.9%.` selecting `S3:E6` validates with `[]`, though 12.9% is Q1 FY26 and current is 11.2%. Claim `Copper prices fell sharply during the quarter.` selecting `S3:E13` also validates with `[]`, though that excerpt says a sharp rise. Reproduction: build one item containing that text, citations `["S3"]`, evidence `[{"id":"S3:E6"}]` (or E13), repeat under the four required headings, and call `validate(..., model=True)` with conflicts `[]`. The prompt forbids both mistakes, but the validator cannot enforce every value/period relationship or directional paraphrase. Do not claim automatic hallucination prevention; A3 human-style source review remains necessary for the submitted brief.

2. **Low — offline display currency label on percent row.** `excerpt_display` currently returns `EBITDA margin (₹ crore): Q1 FY27 11.2%; Q1 FY26 12.9%; YoY −170 bps.` The table-wide currency header is inapplicable to margin. Values remain percentages, so this is presentation ambiguity, not corrupted numeric results. Director notified; omit the currency label for percentage/basis-point rows.

3. **Live hardening limit.** Public DNS addresses are checked once, then urllib performs its own connection resolution. DNS rebinding/proxy behavior can bypass an absolute “public-only connection” guarantee. No such request was attempted. Appropriate for a small explicit-URL prototype with trusted URLs; pin/verify connection addresses before describing it as a hardened untrusted-URL fetcher.

Reporting-period inference remains document-level and covers a small set of fiscal/calendar quarter patterns. Unknown periods are not equated; metadata trust is declared rather than authenticated. These are generalization limitations, not newly observed failure of the supplied pack.

## Handoff and omissions

No external model quality, real-ticker live data, recording, publication or submission was verified. A3 separately reviews generated prose. One incidental `git diff` check could not run because this directory is not a Git repository; source inspections and test results above do not depend on Git. Resource use was bounded local tests and small in-memory probes, under six minutes, negligible storage. Next dependency: director addresses or records the minor renderer issue and accurate semantic/live limitations, integrates A3's prose decision, and runs final checks if code changes.
