# Test log

## Assignment and evidence

The director read `agents.md`, the supplied `AI innovator assignment/README.md`, and all eight research Markdown documents before implementation. `candidate.zip` was inventoried: its eight research files are byte-identical to the extracted files. Its README differs only in the research-pack hyperlink and formatting. The required research date is **2026-09-23**, independent of the machine date. SRVCABLE is fictional. No SRVCABLE URLs were fetched or searched; provider API documentation was consulted separately.

`evidence/original_hashes.json` records the original files before implementation. `evidence/source_inventory.json` records the eight source records. Source IDs use filename order: S1 Business Daily, S2 transcript, S3 company release, S4 old pledge news, S5 promotional blog, S6 unrelated cable operator, S7 GST disclosure, S8 shareholding filing.

## Delegation and ownership

Delegation was available through T3 Code. Workers received bounded tasks with explicit models, effort, clean context, file scope, reviewer, resource limits, prohibited work, and stop conditions. No nested pools were used.

| Task | Route | Scope and reviewer |
| --- | --- | --- |
| D1 inventory | gpt-6-luna / medium | Read-only source metadata and constraints; reviewed by director and A1 |
| E1 evidence synthesis | gpt-6-luna / medium | Source-indexed coverage, time comparisons, archive README; reviewed by director and A1 |
| I1 implementation | gpt-6.1-sol / medium | Owns orchestrator, prompt, focused tests; reviewed by R1 and A1 |
| A1 adversarial review | gpt-6.1-sol / high | Independent threat model and output challenges; director integrates findings |

D1's narrative contained cross-reference typos for the revenue and shareholding rows; the table itself and E1 used the correct filename-sorted mapping. The director checked the source inventory and retained the corrected mapping above. No model-route escalation was needed.

I2 was a bounded correction task at the original Sol/medium route, with integration owned by the Sol/high director. An initial follow-up mentioned escalation, but that wording was explicitly corrected before execution because follow-up messages do not change a worker's model/effort. The implementation and independent-review owners remained separate.

## Acceptance criteria fixed before the runs

- Exactly Snapshot, Bull case, Bear case, Open questions, Sources; concise retail language.
- Official Q1 revenue ₹1,248 crore/+18.0%; explicitly contrast news ₹1,428 crore/+35% rather than silently resolving it.
- Date the current promoter pledge (4.1% of promoter holding, June 2026), distinguish the March 2024 article's 35%, and do not label a time change as a same-period contradiction.
- Attribute forecasts and the GST impact/appeal position to management; do not claim an appeal has succeeded or already been filed.
- Exclude the cable-TV namesake's ₹8 lakh penalty from SRVCABLE evidence.
- Ignore the blog injection, target, recommendation, and unsupported consensus.
- Require valid source IDs and grounded numeric claims; preserve metadata, failed visible outputs, validation results, and fallback reasons.
- Verify no-credential operation, deterministic offline behavior, API failures, input validation, and original-source hashes.

Run commands, actual results, and changes are appended below after execution. A run counts as model-generated only when its audit records a successful model response accepted by validation.

## Initial transport failure (preserved)

```sh
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider groq --model openai/gpt-oss-120b --review balanced --as-of 2026-09-23 --output evidence/iteration1/brief.md --audit evidence/iteration1/run_audit.json
```

Outcome: Groq returned HTTP 403 with urllib's default User-Agent. The run emitted an honestly labeled offline extractive brief (453 words), retained its request/prompt/code snapshot, recorded `API HTTP 403`, and passed structural/offline validation. This is a failed model attempt, not a successful model iteration.

A separate authenticated `/models` probe with an explicit `document-research-agent/1.0` User-Agent succeeded and confirmed `openai/gpt-oss-120b` availability (`evidence/provider_probe.json`). No research URL was fetched. The implementation was revised to send an explicit application User-Agent before retrying the writer.


## Genuine writer iterations and revisions

All runs used the supplied local SRVCABLE pack and `--as-of 2026-09-23`. Research browsing stayed disabled. Failed model output is retained as `runs/<unique-id>/response.json` when the provider returned visible text; the corresponding `brief.md` may be an explicitly labeled fallback. Inference requests contain no tool definitions.

1. **Balanced / GPT-OSS 120B:** after the User-Agent transport fix, the model returned altered/nonexistent evidence quotations and cited a capacity figure to a transcript that did not contain it. The response was rejected. Its open question did contain the revenue discrepancy, so the early regex's “missing conflict” diagnosis was also over-strict. We preserved the output, tightened exact-quote instructions, shortened the requested answer, and required a clear conflict label.
2. **Conservative / GPT-OSS 120B:** exact-quote and numeric checks passed (330 words), but independent A2 review rejected “is appealing” because the source only establishes an intended appeal. We added an appeal-status check, moved from model-copied quotes to program-assigned evidence IDs, and required selected evidence for each cited source.
3. **Skeptical / GPT-OSS 120B:** evidence IDs removed fabricated quotations. A historical year in metadata was initially rejected because the selected body excerpt lacked it. Publication-date support was added. The next run passed automated checks (387 words), but A3 noted imprecise attribution and historical labeling; it was not chosen as the final answer.
4. **Alternative models requested by user:** tested Groq `qwen/qwen3.8-27b` and `openai/gpt-oss-20b` under the same skeptical policy. GPT-OSS 20B passed initial automated checks but independent review found a revenue-share-to-sales error; its second output changed the scope of the capacity addition and omitted important context. Qwen produced stronger source distinctions, but missed historical pledge coverage and selected incomplete evidence for some question premises. One Qwen retry returned HTTP 429. No failed run was substituted with a stronger model without recording the change.
5. **Validator corrections from real runs:** normalized abbreviated fiscal years, stopped treating future-tense questions as certain forecasts, added current-table-value binding and reversed-direction checks, retained source title/date context, and kept paragraphs together so speaker/subject/qualifications survive extraction. Explicit conflict sentences can discuss both reports without being mistaken for a single current-value assertion. These changes preserve stricter citation and numeric checks rather than accepting the earlier defective prose.
6. **Gemini requested by user:** API model listing succeeded without exposing the key. Added explicit Gemini support using its OpenAI-compatible endpoint. Gemini 3.8 Flash and 3 Flash Preview returned HTTP 503; Gemini 2.5 Pro returned HTTP 404 despite appearing in the listing. Gemini 2.5 Flash returned genuine responses. Those early responses exposed missing selected date context, a false table-binding rejection inside an explicit conflict, and omission of the required historical label. Their responses and honest fallbacks are preserved. The prompt was revised to require precise planned-appeal language, plant scope, simple supported sentences, and the historical label.

### Commands

The exact model-run commands below correspond to preserved experiment directories. Code and standalone prompt snapshots are stored beside each experiment. The conservative run deliberately used its snapshot entry point; later root changes do not alter that experiment.

```sh
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider groq --model openai/gpt-oss-120b --review balanced --as-of 2026-09-23 --output evidence/iteration2_balanced/brief.md --audit evidence/iteration2_balanced/run_audit.json
python3 evidence/iteration3_conservative/orchestrator.py SRVCABLE 'AI innovator assignment' --provider groq --model openai/gpt-oss-120b --review conservative --as-of 2026-09-23 --output evidence/iteration3_conservative/brief.md --audit evidence/iteration3_conservative/run_audit.json
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider groq --model openai/gpt-oss-120b --review skeptical --as-of 2026-09-23 --output evidence/iteration4_skeptical/brief.md --audit evidence/iteration4_skeptical/run_audit.json
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider groq --model openai/gpt-oss-120b --review skeptical --as-of 2026-09-23 --output evidence/iteration5_skeptical/brief.md --audit evidence/iteration5_skeptical/run_audit.json
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider groq --model qwen/qwen3.8-27b --review skeptical --as-of 2026-09-23 --output evidence/model_qwen/brief.md --audit evidence/model_qwen/run_audit.json
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider groq --model openai/gpt-oss-20b --review skeptical --as-of 2026-09-23 --output evidence/model_gptoss20b/brief.md --audit evidence/model_gptoss20b/run_audit.json
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider groq --model qwen/qwen3.8-27b --review skeptical --as-of 2026-09-23 --output evidence/model_qwen_v2/brief.md --audit evidence/model_qwen_v2/run_audit.json
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider groq --model openai/gpt-oss-20b --review skeptical --as-of 2026-09-23 --output evidence/model_gptoss20b_v2/brief.md --audit evidence/model_gptoss20b_v2/run_audit.json
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider groq --model qwen/qwen3.8-27b --review skeptical --as-of 2026-09-23 --output evidence/model_qwen_v3/brief.md --audit evidence/model_qwen_v3/run_audit.json
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider gemini --model gemini-3.8-flash --review skeptical --as-of 2026-09-23 --output evidence/model_gemini38/brief.md --audit evidence/model_gemini38/run_audit.json
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider gemini --model gemini-2.5-flash --review skeptical --as-of 2026-09-23 --output evidence/model_gemini25/brief.md --audit evidence/model_gemini25/run_audit.json
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider gemini --model gemini-3-flash-preview --review skeptical --as-of 2026-09-23 --output evidence/model_gemini3/brief.md --audit evidence/model_gemini3/run_audit.json
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider gemini --model gemini-2.5-flash --review skeptical --as-of 2026-09-23 --output evidence/model_gemini25_v2/brief.md --audit evidence/model_gemini25_v2/run_audit.json
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider gemini --model gemini-2.5-flash --review skeptical --as-of 2026-09-23 --output evidence/model_gemini25_v3/brief.md --audit evidence/model_gemini25_v3/run_audit.json
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider gemini --model gemini-2.5-pro --review skeptical --as-of 2026-09-23 --output evidence/model_gemini25pro/brief.md --audit evidence/model_gemini25pro/run_audit.json
python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider groq --model qwen/qwen3.8-27b --review skeptical --as-of 2026-09-23 --output evidence/model_qwen_final/brief.md --audit evidence/model_qwen_final/run_audit.json
```

### Machine-recorded outcomes

| Experiment | Model | Mode | Words | Validation / outcome |
| --- | --- | --- | ---: | --- |
| iteration2_balanced | openai/gpt-oss-120b | offline | 457 | Model validation failed: evidence quote absent from cited source; missing explicit revenue conflict; unsupported numeric claim |
| iteration3_conservative | openai/gpt-oss-120b | model | 330 | Automated validation passed; see independent review for semantic acceptance |
| iteration4_skeptical | openai/gpt-oss-120b | offline | 457 | Model validation failed: unsupported numeric claim in selected evidence |
| iteration5_skeptical | openai/gpt-oss-120b | model | 387 | Automated validation passed; see independent review for semantic acceptance |
| model_qwen | qwen/qwen3.8-27b | offline | 437 | Model validation failed: claim metric/topic absent from selected evidence; forecast presented as certain; unsupported numeric claim; unsupported numeric claim in selected evidence |
| model_gptoss20b | openai/gpt-oss-20b | model | 356 | Automated validation passed; see independent review for semantic acceptance |
| model_qwen_v2 | qwen/qwen3.8-27b | offline | 435 | API HTTP 429 |
| model_gptoss20b_v2 | openai/gpt-oss-20b | model | 336 | Automated validation passed; see independent review for semantic acceptance |
| model_qwen_v3 | qwen/qwen3.8-27b | offline | 435 | Model validation failed: claim metric/topic absent from selected evidence |
| model_gemini38 | gemini-3.8-flash | offline | 435 | API HTTP 503 |
| model_gemini25 | gemini-2.5-flash | offline | 435 | Model validation failed: unsupported numeric claim in selected evidence |
| model_gemini3 | gemini-3-flash-preview | offline | 435 | API HTTP 503 |
| model_gemini25_v2 | gemini-2.5-flash | offline | 489 | Model validation failed: table value does not match claimed reporting period; unsupported numeric claim in selected evidence |
| model_gemini25_v3 | gemini-2.5-flash | offline | 489 | Model validation failed: missing dated historical/current pledge comparison with denominator |
| model_gemini25pro | gemini-2.5-pro | offline | 489 | API HTTP 404 |
| model_qwen_final | qwen/qwen3.8-27b | model | 395 | Automated validation passed; see independent review for semantic acceptance |

## Final selection and checks

The selected artifact is **`evidence/model_qwen_final/brief.md`**, generated by `qwen/qwen3.8-27b` through Groq with the skeptical writer policy. It is 395 words including all eight source records (225 body words). Independent A4 review passed the exact unedited text, including its factual claims, source citations, planned appeal status, forecasts and historical pledge comparison. R3 implementation review found no new core workflow blocker. The director selected this output rather than the earlier automatically accepted but semantically defective outputs.

Promotion copied generated bytes without editing:

```sh
cp evidence/model_qwen_final/brief.md brief.md
cp evidence/model_qwen_final/run_audit.json run_audit.json
```

Both the run artifact and final brief/audit are byte-identical. The audit's code and actual writer-prompt hashes match the delivered code and selected prompt snapshot. No company facts or prose were manually written into the final brief.

```sh
python3 -m py_compile orchestrator.py
python3 -m unittest discover -s tests -v

env -u GROQ_API_KEY -u GEMINI_API_KEY -u GOOGLE_API_KEY -u OPENAI_API_KEY -u OPENAI_BASE_URL python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider auto --env-file /dev/null --output evidence/offline_a/brief.md --audit evidence/offline_a/run_audit.json
env -u GROQ_API_KEY -u GEMINI_API_KEY -u GOOGLE_API_KEY -u OPENAI_API_KEY -u OPENAI_BASE_URL python3 orchestrator.py SRVCABLE 'AI innovator assignment' --provider auto --env-file /dev/null --output evidence/offline_b/brief.md --audit evidence/offline_b/run_audit.json
```

Results:

- Compilation and **25 unittest tests passed**; full output in `evidence/tests_final.txt`.
- Both real CLI runs without credentials selected offline mode and produced identical briefs. Their unique audit/artifact directories remain separate.
- Tests cover metadata, date/URL/size rejection, duplicate/symlink handling, identity mismatch, relocated injection, unrelated-entity contamination, same/different reporting periods, revenue and profit conflicts, exact evidence/metric/sign/direction checks, intended appeal status, fiscal-year equivalence, malformed/truncated/API-error fallback, Gemini routing, a real local keyless HTTP gateway, explicit live-mode gating and mocked retrieval, secret exclusion, output path isolation, and source immutability.
- Original six independent counterexamples failed initially (`evidence/review_before_fixes.txt`) and now pass without changing their tests. Other observed integration failures and corrections are retained in `evidence/intermediate_test_failures.md`.
- All original input-file hashes match. No SRVCABLE research URL was fetched. The final run has no live fetches, exact required five headings, valid cited evidence, and no leaked configured API keys in generated code/Markdown/JSON. Checks are recorded in `evidence/final_validation.json`.
- Independent reports: `evidence/implementation_review.md`, `implementation_review_final.md`, `implementation_review_latest.md`, `adversarial_review.md`, `model_comparison_review.md`, and `adversarial_final.md`.

## Limitations and submission handoff

Automated checks remain conservative heuristics rather than a proof of semantic entailment. Period/value binding, temporal date/value completeness, unfamiliar financial metrics, broad entity aliases and unseen injection wording still need review. The selected brief's actual figures, dates, units and scope were independently checked. Source IDs are stable for the same corpus; changing corpus membership may renumber them. Supplied source metadata is not authenticated against the web.

The opt-in live source tool supports trusted public HTTPS Markdown with valid metadata, not automatic web search, HTML or PDF scraping. It was tested with mocks, not a real ticker. Its DNS precheck is not hardened against rebinding. No hidden model reasoning is stored; token-count metadata may include a reasoning-token count. The no-credential brief is extractive and less polished. The exact final brief retains ITC/CGST/bps abbreviations as a minor retail-readability limitation.

All six requested files are created. Original research and failed model evidence remain intact. This folder was not an existing Git repository; no remote repository was created or published. The assignment's personal 2–3 minute narrated screen recording remains a submission step, documented in `README_AGENT.md`.

## Optional live-data bonus — 16 October 2026 (Asia/Kolkata)

Scope: extend existing explicit URL tool; preserve SRVCABLE inputs and selected submission artifacts. Read agents.md, README_AGENT.md, orchestrator.py, all existing tests and the assignment brief before implementation. Baseline 25 tests passed. Director selected WIPRO based on accessible official sources. No SRVCABLE research URL was requested. Before hashes of the 13 original assignment/submission files are saved in `evidence/live_bonus/preserved_artifacts_before.json`.

Delegation followed agents.md: I1 (gpt-6.1-sol, medium, clean context) owned retrieval/parser and focused tests; E1 (gpt-6-luna, medium, clean context) independently mapped raw source quotes; R1 (gpt-6.1-sol, high, clean context) independently reviewed implementation and generated claims. No nested workers. Director selected source, ran inference, integrated findings and owned final checks. E1 map: `evidence/live_bonus/source_evidence_map.md`; routing/scoping and discovery notes: `evidence/live_bonus/discovery.md`.

Discovery retained `evidence/live_bonus_discovery/attempts.json` and raw probes: current TCS release returned 403 (no bypass); current and prior-quarter Wipro releases returned 200. Pre-existing `evidence/live_discovery/` contains earlier TCS/Infosys 403s, HCLTech timeout and a successful older Wipro page; these were preserved. The final selected source is the official Wipro release dated 2026-10-15, reporting the quarter ended 2026-09-30. The actual machine date was 2026-10-16; UTC retrieval timestamps are 2026-10-15 because local time is UTC+05:30.

I1 added a narrow stdlib HTML adapter, native multiple-exchange identity support, raw/normalized snapshots and hashes, dateline evidence, coverage gaps, durable retrieval failure audit, and a live-only coverage prompt suffix. The fictional system_prompt.md remains unchanged. During development the encoding-error classification test initially failed because UnicodeDecodeError inherits ValueError; it was corrected to record the exception class and the unchanged test passed. A director integration check caught ticker-prefix ambiguity; I1 added exact token delimiters and regression tests. Injection-marked documents cannot establish identity. No gate was weakened to make a run pass.

First live CLI attempt (same source URL as README; Groq qwen/qwen3.8-27b): actual retrieval HTTP200, raw snapshot 151,904 bytes, native company/ticker anchor and 2026-10-15 publication dateline. API returned 429 because requested output budget 6000 exceeds this key's output-token limit 1000. Mode was explicitly offline; its thin extractive fallback was NOT accepted as the bonus demonstration. Preserved `attempt1_audit.json`, `attempt1_fallback_brief.md`, stdout/stderr and unique run directory. Retried with already-configured Gemini 2.5 Flash credentials; no secret values printed or saved.

Attempt 2 (Gemini 2.5 Flash) retrieved the same latest official source successfully and returned JSON. Validation rejected a question referring to revenue while selecting only a CEO AI-strategy paragraph with no revenue metric. Kept `attempt2_audit.json`, `attempt2_fallback_brief.md` and the visible response in its unique run directory. Did not weaken the topic gate. I1 followup narrowed live-only prompt instructions to source metrics and explicit management attribution; original fictional prompt unchanged. R1 independently found financial scope/metric counterexamples that exposed gaps in the generic heuristic; these findings and regression tests are retained before correction.

R1 supplied four independent counterexamples that initially failed the desired-rejection tests (`evidence/live_bonus/review_before_fixes.txt`): invented consolidated scope, gross revenue relabeled as net income, CC growth relabeled as reported growth, and segment margin relabeled company-wide. Director added targeted metric/scope guards; all four unchanged tests now pass. The checks remain lexical: selecting unrelated-but-numerically-compatible metric quotes together may still evade entailment checks. Independent claim review remains necessary.

Successful actual live command (attempt 3):

```sh
python3 orchestrator.py WIPRO live_inputs --live-data --live-url 'https://www.wipro.com/newsroom/press-releases/2026/wipro-announces-results-for-the-quarter-ended-september-30-2026/' --provider gemini --model gemini-2.5-flash --review skeptical --output evidence/live_bonus/wipro_brief.md --audit evidence/live_bonus/wipro_audit.json
```

Result: **model-generated, Gemini 2.5 Flash**, no fallback, no model/final validation errors, 369 words including Sources. This run uses actual current local date **2026-10-16**, publication **2026-10-15**, reporting quarter end **2026-09-30**. Its immutable artifacts are in `evidence/live_bonus/runs/20261015T202619-bb1caf209a/`; `live_sources/live_001.raw` is the original HTML snapshot, `live_sources/live_001.md` the normalized document, and `fetches.json` records original URL, UTC retrieval timestamp, publication-date evidence, native legal identity, hashes and coverage gap. Request, visible response, writer prompt, audit and brief remain beside them. Promoted brief bytes match the generated run brief exactly; no manual edits.

Independent R1 review accepts all 12 generated entries and source metadata against exact selected evidence and original HTML. Review covers reporting dates, INR billion/USD million units, source USD translations versus segment realized FX, gross revenue versus net income, segment margin, reported/CC growth, guidance attribution, trailing-twelve-month attrition and negative IT Products segment results. Review is in `evidence/live_bonus/independent_review.md`. The Bull case has management statements and guidance rather than independent corroboration, and no valuation conclusion is supported.

Final actual checks:

```sh
python3 -m py_compile orchestrator.py live_sources.py
python3 -m unittest discover -s tests -v
git diff --check
```

**37 tests passed**, including all 25 existing tests, 8 new retrieval/parser tests and 4 independent scope/metric counterexamples. Full final output: `evidence/live_bonus/tests_final.txt`. Focused tests cover semantic HTML extraction, inline numeric footnotes, dates, native multi-exchange identity and prefix rejection, injected identity exclusion, unsupported host/content, empty/missing dates, malformed encoding, timeout, HTTP404, future date, bounded response failure and durable snapshots. No redirects or access-control bypass was introduced.

`evidence/live_bonus/final_verification.json` records: all 13 original source/submission hashes unchanged; raw/normalized hashes match; reparsing the raw snapshot reproduces normalized bytes exactly; both current code hashes match the successful audit; model claim validation re-run passed; all five sections present; promoted/generated brief bytes equal; current as-of date correct; configured credentials absent from live artifacts. Only credential variable names were printed during setup, never values. No commit, push or publication was performed.

Bonus answer: **Yes — live data was added and actually run on NSE: WIPRO.** Its latest official release reported gross revenue of ₹247.5 billion, up 9.1% YoY, while net income was ₹32.0 billion, down 1.9% YoY. Total bookings fell 22.9% QoQ in constant currency. This demonstrates why revenue growth alone is insufficient: profit, deal flow, metric scope, FX basis and reporting dates all matter. These are observations from the retrieved release, not an investment recommendation.

Limitations: one official company release is a useful quarterly snapshot, not an independently corroborated investment thesis. Six image-based financial tables were explicitly omitted (no OCR); their contents and standalone/consolidated statement scope were not invented. The HTML adapter intentionally supports Wipro press releases only; other companies still need a supported Markdown source or a new reviewed adapter. DNS prechecks are not pinned against rebinding, and semantic entailment is not guaranteed by automated checks. Groq failed under the configured key limit; Gemini is the demonstrated successful model. Earlier attempts and review findings remain preserved.

## Two additional live tickers and workflow routing — 16 October 2026

User requested two further live NSE tickers and automatic Groq routing for the supplied fictional data / Gemini routing for live data. Original assignment artifacts and the prior Wipro brief/audit/review were hashed before work in `evidence/live_more/preserved_before.json`. No fictional-company web research was performed.

Delegation: D2 (gpt-6-luna/low, clean context) discovered official accessible source candidates, preserving raw HTML and URL/time/hash/status in `evidence/live_more/discovery/`. I2 (gpt-6.1-sol/medium, clean context) implemented routing and focused tests. I3 (gpt-6.1-sol/medium, clean context) owns bounded official HTML adapters and parsing tests after discovery. R2 (gpt-6.1-sol/high, clean context) independently reviews routing, completed adapters, and later each exact generated brief against snapshots; director integrates and owns final output. No nested workers. Routing and source work were independent; implementation precedes its review.

I2: auto local SRVCABLE selects Groq when its credential exists, otherwise offline; auto `--live-data` selects Gemini when its credential exists, otherwise offline. Unrelated configured credentials cannot divert either workflow. Explicit `--provider` overrides remain supported. Other local real-company corpora retain prior provider priority. Model/environment/base URL behavior is retained. Five focused routing tests added; two old assertions intentionally changed because their previous SRVCABLE→OpenAI expectations contradicted the new user instruction. All 42 tests passed after routing. R2 approved six focused routing checks; its initial nonexistent test-name loader error and correction remain in the independent review report.

Discovery found current Tech Mahindra Q2 FY27 official release accessible (HTTP200, 166870 bytes), dated October15 2026, period ended September30 2026. Persistent Q1 FY27 official release was accessible (HTTP200, 329941 bytes), dated August2 2026, period ended June30 2026. Persistent Q2 URL redirected to a Radware access-challenge page; discovery saved the response and final URL and classified it as unsuccessful content despite terminal HTTP200. No access challenge was bypassed. The production fetcher retains its no-redirect rule. The older Persistent disclosure is explicitly an earlier-period result, not represented as latest company results.

Initial production runs used provider auto (no provider override). TECHM selected Gemini2.5Flash and retrieved actual source but fell back after a mixed reported/CC paragraph triggered the existing CC gate. R2 identified real semantic errors in that rejected response too: INR versus USD growth was mislabeled a revenue conflict and historical achieved growth was turned into guidance. The live prompt was refined without changing the fictional prompt; CC validation now binds growth values and QoQ/YoY axes to explicitly reported clauses, preserving CC-only rejection. Positive reported and negative CC/axis cases were added; 50 tests passed.

PERSISTENT production retrieval returned HTTP302 to an access challenge, despite earlier successful discovery. The fetcher refused the redirect, saved raw response/failure audit and emitted no brief. We did not alter request headers or solve the challenge to force access. All attempted sources/failure artifacts remain. A normal direct request using production headers and redirects disabled found accessible official Coforge Q1FY27 instead; source dated July27 2026 for quarter endedJune30 2026. D2 retained original URL/time/hash/status/raw and quotes in discovery/followup_candidates.json. Coforge replaces Persistent as the second intended successful live company; the earlier adapter and its tests remain useful for snapshot replay and its availability limitation remains explicit.

A separate local SRVCABLE auto run verified Groq openai/gpt-oss-120b was selected and actually returned JSON. Its output was rejected because selected evidence lacked dates used in claims, and it emitted the labeled extractive fallback. It did not fetch a research URL. Its attempted response and audit are preserved under fake_routing/. The existing independently accepted submission brief/audit remain untouched. This extra verification establishes routing, not a new approved fictional submission.

TECHM attempt2 and COFORGE attempt1 both retrieved official live HTML successfully using automatic Gemini routing, but their model outputs were rejected and not accepted as demonstrations. R2 found the shared base fictional prompt still mandated revenue conflict/pledge discussion, causing invented conflicts and uncited absence claims. TECHM also returned evidence IDs as strings instead of required objects. Coforge used unsupported formulations of missing-evidence statements. The validator itself rejected even its exact allowed generic insufficiency sentence during model quote validation. All original rejected responses, fallback briefs and audits remain in unique run directories plus attempt-number copies.

Corrective design: separate live_system_prompt.md for genuine company disclosures; preserve the fictional system_prompt.md byte-for-byte. Keep citation/numeric/entity/injection gates intact. Only the exact existing generic insufficiency sentence with empty citations and evidence is allowed through the model quote gate; arbitrary uncited/negative company claims remain rejected. Flexible section counts avoid filling a company disclosure with invented risks. R2 recommended this correction independently. The CC guard is still heuristic; a long title prefix may contain percentages for unrelated metrics, so independent metric/value review remains mandatory.

Successful production commands (no explicit provider override):

```sh
python3 orchestrator.py TECHM live_inputs --live-data --live-url 'https://www.techmahindra.com/insights/press-releases/techmahindra-q2-fy27-results/' --review skeptical --output evidence/live_more/techm/brief.md --audit evidence/live_more/techm/audit.json
python3 orchestrator.py COFORGE live_inputs --live-data --live-url 'https://news.coforge.com/newsroom/press-release/coforge-delivers-49-yoy-growth-pat-increases-110-yoy' --review skeptical --output evidence/live_more/coforge/brief.md --audit evidence/live_more/coforge/audit.json
```

Final actual live results: both **Gemini 2.5 Flash, mode=model**, no fallback, empty model and final validation errors. TECHM attempt3: 369 words including source; COFORGE attempt2: 285 words. The briefs are unedited generated bytes; snapshots retain URL, retrieval time, actual article publication date, native company/ticker identity, raw and normalized hashes. Local as_of is 2026-10-16; UTC retrieval timestamps are 2026-10-15 because local time is UTC+05:30.

R2 independently approved all 19 entries across both exact generated briefs against selected evidence IDs, normalized snapshots and original raw HTML. Review checked dates, periods, USD/INR differences, millions/crores, reported/CC growth, consolidated scope only where stated, management attribution, bonus recommendation versus completed issuance, order-book horizon, dividend record date and attrition comparison. Its report is `evidence/live_more/independent_review.md`; all initial findings and failed attempts remain there.

Lessons from the retrieved sources: TECHM's September2026 quarter reports INR revenue growth15.6%YoY versus reported USD6.8% and CC7.2%; different currencies/bases are not a conflict. Coforge's June2026 release reports INR revenue49%YoY, PAT110%YoY and EBITDA margin20.3%; an attractive company release alone does not establish a supported bear conclusion, so the generated brief explicitly reports insufficiency instead of inventing risks. Coforge is a historical-quarter brief as_ofOctober16, not a claim to cover subsequently published results.

Final checks: `python3 -m unittest discover -s tests -v` passed **55 tests** (`evidence/live_more/tests_final.txt`), including original tests, five routing tests, ten new source/CC cases and three prompt/sentinel cases. `python3 -m py_compile orchestrator.py live_sources.py` and `git diff --check` passed. `evidence/live_more/final_verification.json` verifies all 16 original/submission/prior-live artifact hashes preserved, both raw/normalized hashes and exact reparsing, code/prompt hashes, unchanged generated/promoted bytes, all five sections, current as_of dates, providerGemini and source-grounding revalidation, and no configured credentials in live_more artifacts.

Residual limits: narrow exact-source adapters, one company-authored source per brief, heuristic financial entailment checks, TechM complex statement table explicitly omitted, no OCR/PDF support. The review accepted actual facts; automated validation alone is not a guarantee. TechM has three Bull bullets despite the prompt preference for one or two (editorial only). Persistent's production retrieval remains failed, with no successful brief claimed. Explicit provider overrides remain possible. Original SRVCABLE and Wipro deliverables are unchanged; no commit, push or publication occurred.

A second unchanged local-auto SRVCABLE check again called Groq openai/gpt-oss-120b and returned JSON; its model draft was rejected for an incomplete historical/current pledge comparison and safely fell back. Both local checks are routing evidence, not new accepted model briefs. The original accepted Groq SRVCABLE submission remains the selected artifact. This is an observed model-reliability limitation, not a failure to route. The final verification record reflects the latest local check and confirms the original Wipro raw snapshot still reparses exactly under the extended dispatcher.
