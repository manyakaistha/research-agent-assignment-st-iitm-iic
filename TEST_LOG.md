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
