# R1 independent review

Status: accepted final attempt3 brief after independent claim-by-claim review; four initial validator failures were corrected and all36 tests pass. Reviewer R1 did not implement the adapter, corrective guards, or brief. Director owns integration and final acceptance.

## Scope and checks actually performed

Inspected `agents.md`, `orchestrator.py`, `live_sources.py`, `README_AGENT.md`, `tests/test_live_html.py`, original test modules, HTML fixture, source evidence map, saved discovery HTML, both real-run audits, saved raw/normalized release, and the then-current offline brief. No network or model calls were made by this reviewer.

Ran `python3 -m unittest discover -s tests -v`: all 32 pre-existing tests passed. Added four independent desired-rejection counterexamples in `tests/test_live_review.py`; all four initially failed because validation returned an empty error list. These failures are intentional evidence of the initial implementation, not an approval. Parent will implement any correction separately.

For run `20261015T202427-92628242dd`, recomputed raw and normalized SHA-256 hashes and matched the audit. Re-normalizing saved raw HTML exactly reproduced its normalized Markdown. Discovery HTML differs byte-for-byte from this later fetch; source text inspected at discovery lines 2110–2128 agrees with the fetched financial narrative. No claim relies on treating those captures as byte-identical.

## Material findings before integration

**High: validator accepts incorrect financial metric/basis/scope claims.** `orchestrator.py:210`–`242` checks numeric-token presence and a small topic list, but initially omitted net income, constant-currency versus reported growth, consolidated/standalone scope, and segment versus company-wide margins. Each following claim passed `validate(..., model=True)` with one exact source quote:

| Unsupported claim | Selected source evidence | Required correction |
|---|---|---|
| “Wipro's net income was ₹247.5 billion.” | “Gross revenue at ₹247.5 billion ($2,583.0 million [1] ), an increase of 1.1% QoQ and 9.1% YoY.” | Reject revenue evidence as support for net income; actual released net income is ₹32.0 billion. |
| “Reported IT Services revenue increased 0.6% YoY.” | “Non-GAAP constant currency [2] IT Services segment revenue was flat sequentially and increase of 0.6% YoY.” | Retain non-GAAP CC basis; reported growth is 0.3% YoY, with 0.1% QoQ decrease. |
| “Wipro's consolidated gross revenue was ₹247.5 billion.” | Same gross-revenue sentence above | Reject added consolidated or standalone scope when selected evidence does not state it. |
| “Company-wide operating margin was 16.5%.” | “IT services operating margin [5] for Q2’27 was at 16.5%, up by 0.5% QoQ and down by 0.2% YoY.” | Retain IT Services segment scope. Footnote definition is Segment Results Total under IFRS. |

Regression locations: `tests/test_live_review.py`. Empty validation errors never establish full semantic entailment; final output still requires claim-by-claim review, especially when several selected paragraphs provide the same numbers for different measures.

**Low: ordered-list footnote numbering is not retained.** `live_sources.py:45`–`47` starts each `li` as plain text, so actual source `<ol><li>` definitions lose their native 1–5 labels, although their wording and ordering survive. Superscript references are retained as `[1]`–`[5]`. The fixture uses an already-numbered paragraph for its footnote and therefore does not exercise native ordered-list numbering. Preserve list numbers or document this fidelity limit if reliable direct footnote linking is claimed. It did not alter the inspected financial wording.

## Source and retrieval review

Saved release explicitly identifies Wipro Limited with NSE: WIPRO; publication is October 15, 2026, distinct from the September 30, 2026 reporting quarter. Run as-of October 16, 2026 is consistent. Dateline and identity are native article text, not URL-derived metadata.

Gross revenue ₹247.5 billion and translated $2,583.0 million, net income ₹32.0 billion and translated $333.9 million, IT Services reported revenue $2,611.5 million, non-GAAP CC growth, segment operating margin 16.5%, bookings, cash flow, currency definitions, and forward-looking December-quarter guidance survive normalization. Do not infer standalone/consolidated scope. General USD convenience translation uses INR95.83/USD; realized IT Services FX is INR94.45/USD. Total bookings are contract value, not current-period revenue. Margin changes must retain the source's exact percent wording or correctly identify percentage-point interpretation; do not turn segment margin into company-wide margin.

The parser omits six image-backed financial tables and reports six omitted images. It does not claim OCR or table coverage. Script/style/navigation/footer exclusions, future-date rejection, missing dateline/identity rejection, invalid encoding, oversized response, HTTP404 evidence preservation, ticker-prefix mismatch, and injected identity rejection are covered by passing tests. Fictional SRVCABLE live opt-in is rejected before retrieval; existing offline fictional behavior remains covered. No blocking parser defect was found in the actual saved release.

## Interim brief review and remaining dependency

Attempt1 failed with provider HTTP429 (requested output6000 exceeds key1000 output-token limit). Attempt2 returned a model response but failed topic/evidence validation. Their offline fallbacks correctly disclose that no model was used and retain source URL/date. The one substantive fallback deal-win paragraph matches the saved source and preserves company attribution and future tense. However, blank Snapshot/Bear/Open-question conclusions omit ample available financial evidence and do not qualify as a successful live financial brief demonstration. They remain preserved as negative results.

## Corrections and final artifact decision

Director added targeted metric, financial-scope, segment-margin and CC-only growth guards at `orchestrator.py:215`–`235`. R1 inspected the changes and independently reran `python3 -m unittest discover -s tests -v`: all36 tests passed, including all four new rejection cases. Original failures remain in `review_before_fixes.txt`; parent validation is retained in `tests_after_review.txt`. The corrections do not provide general semantic proof: selecting both gross-revenue and net-income paragraphs still allows an incorrect net-income value drawn from the revenue paragraph. This remains a material limitation of automated approval, addressed for this delivered artifact by the complete human review below. Broader semantic metric/value binding is outside these targeted guards.

Reviewed final run `20261015T202619-bb1caf209a`, generated by `gemini-2.5-flash`, `mode=model`, no fallback, finish reason `stop`, 369 words including sources. Recomputed raw/normalized hashes, matched both tool-code hashes, reproduced normalized Markdown from saved raw, confirmed delivered brief is identical to run brief, and reran model validation independently (empty error list). The response artifact stores `visible_content`, finish reason, and usage, rather than an untouched provider envelope. Full request, visible response and run audit remain available.

All12 final brief entries (plus source metadata) were checked against selected evidence IDs and corresponding saved raw HTML, not merely the evidence map:

| Brief location | Selected evidence | Independent conclusion |
|---|---|---|
| Snapshot1, business identity | E65/E66; normalized About Wipro text | Supported description; company disclosure, not independent assessment. |
| Snapshot2, gross revenue | E4/E7; normalized lines13/19; raw results highlights | ₹247.5bn/$2,583.0m, +1.1%QoQ/+9.1%YoY and Sep30 quarter supported. USD is a source convenience translation. No consolidated/standalone scope invented. |
| Snapshot3, net income | E4/E12; normalized lines13/29 | ₹32.0bn/$333.9m, -4.7%QoQ/-1.9%YoY and reporting quarter supported. |
| Snapshot4, margin | E4/E11; normalized lines13/27 | 16.5% explicitly IT Services; +0.5%QoQ/-0.2%YoY wording retained from source. Calendar quarter is supported by E4. |
| Bull1, strategic investment effect | E20; normalized line45 | Correctly attributed to CEO/Managing Director, not independently established fact. |
| Bull2, guidance | E16/E17; normalized lines37/39 | Dec31 future quarter, $2,571m–$2,625m and -1.5%–+0.5% sequential CC range exact; expectation remains explicit. |
| Bear1, bookings | E10/E4; normalized lines25/13 | $2,595m total bookings;22.9% and58.6%QoQ declines explicitly CC; no claim that bookings equal realized revenue. |
| Bear2, net-income decline | E4/E12; normalized lines13/29 | Supported repeated downside fact. |
| Bear3, attrition | E15/E4; normalized lines35/13 | 13.8% retained as trailing12months to quarter end, not a quarterly attrition rate. |
| Question1, future bookings/revenue | E10/E17 | Declines are supported; future plans and potential revenue effect are questions, not invented answers. |
| Question2, cash deployment | E4/E14/E21; normalized lines13/33/47 | 165.8% net-income conversion is exact; CFO supports “robust”; future deployment is asked rather than asserted. |
| Question3, IT Products | E4/E55; normalized lines13/115 | Negative segment result ₹0.1bn/$0.8m faithfully quoted as loss; reporting quarter supported. Values are source-reported, not a reviewer recomputation or company-wide loss. |

The sole source line correctly links the fetched official URL and states October15 publication. No unsupported legal, pledge, debt, plant, conflicting-source, analyst-consensus, or investment-recommendation claim appears. No actual final-output contradiction warrants regeneration. The release is one issuer source; image-only tables remain outside coverage, with six-image omission explicitly retained in the audit. The brief does not independently disclose that extraction limit, so users need the accompanying audit/README for coverage limits.

Files changed by R1: this report and `tests/test_live_review.py`; no implementation or brief edits. No reviewer network/model calls. Local tests consumed under one second of reported suite runtime across the two suite invocations. No remaining dependency for factual approval of attempt3; director should retain the audit, raw/normalized evidence, negative attempts and stated lexical/extraction limitations with the deliverable.
