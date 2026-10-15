# Independent review — R2

## Stage 1: provider policy

Status: approved for the inspected routing change; no blocking finding.

Inspected `agents.md`, `orchestrator.py:528-547`, `tests/test_provider_policy.py`, and the changed assertion at `tests/test_orchestrator.py:98-99`. Auto local SRVCABLE chooses Groq only when its credential is present; auto live mode chooses Gemini with GEMINI_API_KEY or GOOGLE_API_KEY; missing workflow credentials select offline even when other providers are configured. Explicit providers bypass this policy. Existing model/base URL overrides remain applied to the selected provider, and unrelated local tickers retain previous priority. Case normalization for SRVCABLE is present.

Validation: `python3 -m unittest tests.test_provider_policy tests.test_orchestrator.OrchestratorTests.test_custom_keyless_routing -v` passed 6 tests without network/model calls. An earlier attempted test name `test_routing_and_env` did not exist (loader error); corrected to the actual `test_custom_keyless_routing`, preserving that negative attempt here.

Limits: no live provider request or credential validation was performed. Workflow routing only is approved; source adapters and generated briefs await completed dependent artifacts. No counterexample test needed. Files changed: this report only. Resource use: seconds of local test CPU; no network/model usage.

Next dependency: director notification that I3 source changes are complete, then generated TECHM/PERSISTENT runs for claim-level review.

## Stage 2: completed source adapters

Status: approved within the deliberately narrow observed URL/template scope. Inspected complete `live_sources.py`, native-anchor and HTML dispatch changes in `orchestrator.py`, `tests/test_more_sources.py`, and both representative fixtures. Ran `python3 -m unittest discover -s tests -p 'test_more_sources.py' -v`: 7 tests passed, without network/model calls. Also normalized both full discovery HTML files independently, rather than relying only on reduced fixtures.

Verified: exact host/path allowlist; no query/fragment/credentials for the new adapters; visible article/main extraction; dates from article metadata; native brand/ticker anchors without synthesizing a legal suffix; nested TECHM revenue lists retain reported/constant-currency growth; Persistent table rows retain fiscal quarter, quarter end, currency/unit, metric, column names and signed changes. Ambiguous/merged tables are omitted with coverage gaps. Wipro dispatch equality is tested. Exact paths remain a deliberate limitation, not general company coverage.

Nonblocking residuals: Persistent's table-level forex figcaption is copied into every row; only PBT/PAT are starred in the original, so causal attribution must remain tied to those starred declines. TECHM repeats its whole numeric headline in every list evidence unit, weakening lexical metric binding; the gate is not semantic proof. Hidden-content pruning does not evaluate arbitrary CSS classes. Neither observation invalidates the inspected current normalization.

## Stage 3: first production attempts (not final approval)

### TECHM

Run `techm/runs/20261015T203505-6942581d88`; Gemini `gemini-2.5-flash` was selected and called, then validation triggered offline fallback. Inspected every final brief claim and the entire rejected response. Final `techm/brief.md` SHA256 was `4c30cda1c97523fbeae500d718edf10b9fd9991336776fabfe8430028dadb2c8`. Its only factual bullet accurately quotes identity, business, audited consolidated scope and September 30, 2026 quarter end from the release intro. Source URL/date are correct. The other three sections say evidence does not establish a conclusion. The 114-word fallback is safe but materially incomplete despite ample extracted metrics; do not describe it as a successful generated financial brief.

Verified saved raw SHA256 against manifest, rebuilt normalization from saved raw byte-for-byte, and verified normalized SHA256. Raw evidence: `techm/runs/20261015T203505-6942581d88/live_sources/live_001.raw`; selected evidence in that run's `request.json`; rejected visible answer in `response.json`.

High-priority corrections for any retry: the rejected answer's Open questions item calls INR revenue growth 15.6% versus USD reported growth 6.8% a “Revenue conflict.” These are different currency bases, not a demonstrated contradiction. Its Bull item says management “expects” to sustain momentum “with 7.2%” CC growth, whereas the CEO describes achieved growth and continuing momentum, not a 7.2% forecast. Preserve achieved-result versus management-forward-view distinction. The remaining proposed numeric metrics (INR revenue 16,180 crores; PAT 1,586 crores/32.7% YoY; PAT margin 9.8%/+130bps; deal wins USD1,023m/+25.4%; DSO88; headcount152,206; LTM attrition11.7%; dividendINR15; FCFUSD135m) match the saved release and selected evidence. Raw headcount differs from general About-company employee boilerplate; the response correctly used the quarter-specific metric. Descriptive neutral headcount/attrition bullets provide little bear analysis.

Separate validator defect reproduced without model calls: correct claim `Q2 FY27 revenue was $1,693 mn, up 6.8% YoY in reported terms.` with selected `S1:E4` returns `constant-currency revenue growth presented as reported growth`. The same evidence unit contains both reported6.8% and CC7.2%; current line-level exclusion removes the reported basis. Correct this conservatively; the rejected response also had genuine semantic flaws, so simply disabling the gate would be unsafe.

### PERSISTENT

First run `persistent/runs/20261015T203507-8f098174f9` failed HTTP302 before normalization/model invocation; `persistent/audit.json` preserves failure/raw response. There was no brief to review. The separate saved discovery Q1 release is valid article content dated August2,2026 with consolidated Q1FY27 quarter ended June30,2026 metrics; it is historical relative to October16,2026. Discovery Q2 HTML is a Radware/JavaScript/captcha challenge, corroborated by its challenge final URL in `discovery/fetch_metadata.json`; it does not establish results. Never label Q1 as current/latest without verifying later-quarter coverage.

Stage3 next dependency: corrected/retried actual production artifacts. These findings do not approve any later brief version. Files changed: this report only; no implementation or brief edits and no new counterexample tests. Checks used local Python and existing tests only; no reviewer network/model calls.

## Follow-up: Coforge adapter, CC correction, second production attempts

Status: final adapter/CC changes inspected; approved for narrow observed scope. Independently ran the now-expanded `test_more_sources.py` suite: 10 tests pass. Reviewed Coforge exact host/path, unique post-body scope, native identity/date and quarter end; normalized full `discovery/coforge_q1fy27.html`. July27,2026 release explicitly reports quarter ended June30,2026 and CEO says Q1; no legal suffix or reporting scope was invented. CFO-style fiscal2025 safe-harbor boilerplate is stale and must not override that period. The revised CC guard accepts correct reported6.8%YoY/2.0%QoQ and rejects CC7.2%YoY/2.4%QoQ and switched6.8%QoQ. The live prompt now warns against invented conflicts and past-growth forecasts, but still inherits contradictory fixture-specific requirements below.

Latest inspected runs: TECHM `20261015T203813-659cdd6044`, COFORGE `20261015T203813-972d505bb4`. Both selected/called Gemini2.5Flash and both ended in offline fallback. Rebuilt both saved normalizations byte-for-byte and verified raw/normalized manifest SHA256 values. No reviewer network/model calls.

All final brief claims checked: TECHM remains the same supported identity-only brief/hash as above. COFORGE final SHA256 `0449bb454802c513fdca8df03db923b10fdfab438f0c75dc36b56debc29ec1c7` has accurate identity/business, July27 publication and June30 quarter end from intro (`S1:E2`); its Bull bullet accurately extracts next12months signed order bookUSD2.23bn/+27%QoQ/+44%YoY (`S1:E1`) but awkwardly embeds headline revenue/PAT growth in parentheses with a dangling colon. Those headline49%/110% values are source-backed, but have no clearly named metric in that bullet. Other sections are generic insufficient-evidence text. This125word fallback lacks financial Snapshot metrics and is not a completed model brief.

Second TECHM rejected response again invents “Revenue conflict” across currencies/bases, claims absent promoter pledge without support and uses string evidence IDs instead of the required objects. Numeric revenue/PAT/margin/deal/DSO/attrition values match raw, but proposed final response is correctly rejected. COFORGE rejected financial claims match raw and selected IDs: revenueINR55,277m/+49%YoY; PATINR5,186m/+110%YoY; EBITDAmargin20.3%/+285bps; signed/executable orderbookUSD2.23bn/+27%QoQ/+44%YoY; management FY27 optimism properly attributed. Its Bear and Open questions invent unsupported absence assertions and use non-schema insufficient-evidence sentences. Do not publish rejected responses.

High-priority implementation issue reproduced locally: `validate()` explicitly permits the exact uncited generic sentence, but `model=True` unconditionally requires nonempty evidence even for that sentence. Four sections each containing exactly the permitted sentence with `citations:[]` and `evidence:[]` returns `['missing exact evidence quotes']`. This contradicts the new live prompt's instruction to use that generic sentence where no adverse conclusion is supported. Correction: exempt only the exact permitted sentence with empty citations/evidence from factual-evidence validation; retain factual claim gates.

High-priority prompt issue: inherited `system_prompt.md:5` still says pledge comparison and revenue conflict MUST be present; appending conditional live warnings has not prevented false TECHM conflicts. Prefer a live-specific prompt that omits irrelevant fixture requirements, explicitly shows the allowed generic sentence and exact evidence-object schema, and asks practical questions with supported premises instead of unsupported absence claims. This is a concrete remedy, not approval to weaken acceptance criteria.

Next dependency: final corrected production artifacts. PERSISTENT remains a preserved failed attempt, with no generated claims to approve.

## Final prompt/sentinel correction review

Inspected `live_system_prompt.md`, prompt selection and narrow sentinel branch in `orchestrator.py`, and `tests/test_live_prompt.py`. Ran the focused suite: 3 tests passed. `git diff --exit-code -- system_prompt.md` passed, confirming original local prompt remains unchanged. Approved the correction: live prompt removes irrelevant fixture mandates and specifies exact evidence-object schema; the only skipped quote requirement is the exact generic sentence with both lists empty. Other unsupported/uncited/schema variants remain rejected. No implementation edits made by reviewer.

Residual lexical guard limitation: the CC reported-clause backward span can include repeated headline percentages from other metrics. Passing it does not prove a metric/value binding. Final human review must still inspect each actual metric, value, growth basis and period against raw and selected evidence. This was not expanded into a claim of universal semantic validation.

## Final production artifact decision

Status: APPROVED for the exact inspected final artifacts below, with no blocking factual finding. Both ran the auto live policy with provider `gemini`, model `gemini-2.5-flash`, mode `model`, no fallback, and empty model/final validation lists. All 19 actual entries were independently checked against selected evidence IDs and saved release content. Each manifest raw SHA256 and normalized SHA256 verified; rebuilding normalization from saved raw reproduced normalized snapshots byte-for-byte. No reviewer network/model calls; no implementation or brief hand edits.

TECHM final run `techm/runs/20261015T204016-81d3fc4da2`, 369 words including sources, `techm/brief.md` SHA256 `0b7a2699af6473b0a207b1d31f327be52b70f4a68339a4ae7ee553a88c9a107b`:

| Actual entry | Selected evidence checked | Decision |
|---|---|---|
| Snapshot identity/business | E2, E79 | Native identity and business supported. |
| September30,2026 consolidated INR revenue16,180crores/+15.6%YoY; EBIT2,387crores/+40.5%YoY | E2, E12, E13 | Correct scope, period, values, units and INR growth. |
| USD revenue1,693million/+6.8%reportedYoY/+7.2%CCYoY; EBIT250million/+30.4%YoY | E4, E5 | Correct separate currency/bases; no false conflict. |
| EBITmargin14.8%/+~260bps; PAT166million/+23.2%YoY; PATmargin9.8%/+130bps | E6, E7, E8 | Correct metric binding, USD section and comparisons. |
| New deals1,023million/+25.4%YoY; CEO says over1billion in four quarters | E1, E9, E21 | Correct reported result and attributed CEO observation. |
| CFO says12consecutive margin-expansion quarters and ongoing AI investment | E22 | Correct attributed judgment/activity; no invented forecast growth. |
| ZeroGravity/SpaceXAI/I-HUB initiatives | E33, E34, E35 | Announced initiatives/partnerships correctly described; no claim of completed future benefits. |
| Bear sentinel | none | Exact permitted non-factual statement. |
| FCF135million/headcount152,206 question | E17, E19 | Both premises supported; question makes no asserted adverse causal conclusion. |
| Board-recommended bonus1:1 question | E1 | Explicit raw headline supports recommendation and ratio; no completed issuance or guaranteed shareholder benefit asserted. |

Every ID above is `S1:En`. Publication October15,2026, source URL and September30 quarter end match raw. Minor editorial limitation: 3 Bull bullets exceed live prompt preference1–2; headcount/FCF question is unconventional but does not invent a factual relationship. Neither is a factual blocker. Source's omitted merged table remains a coverage gap, not proof of financial absence.

COFORGE final run `coforge/runs/20261015T204016-5ae29d1241`, 285 words including sources, `coforge/brief.md` SHA256 `9ee1e25d1eb4e4b342cd25880daccc2c35101abc68befa6ac95f3722d581c6ec`:

| Actual entry | Selected evidence checked | Decision |
|---|---|---|
| NSEidentity/AI-native engineering business | E2, E30 | Supported native identity/business. |
| June30,2026 revenueINR55,277million/+49%YoY | E1, E2, E4 | Correct INR units/basis and quarter. |
| PATINR5,186million/+110%YoY | E1, E2, E7 | Correct metric/currency; not USD46% growth. |
| EBITDAmargin20.3%/+285bpsYoY | E1, E2, E5 | Correct explicitly named margin. |
| Next12months executable orderbookUSD2.23billion/+27%QoQ/+44%YoY | E1, E12 | Source headline and business detail jointly support all claims. |
| Management says Q1margins ahead of guidance; EBIT+414bps/EBITDA+285bps attributed to AI | E9 | Attribution retained for management causal interpretation, not independently established cause. |
| Bear sentinel | none | Exact permitted statement. |
| DividendINR4/share, August03,2026 record date and allocation question | E8, E30 | Source says board recommended dividend; brief reports information, does not claim paid. |
| LTMattrition10.4%vs10.8%lastquarter and talent question | E14, E30 | Correct comparison; preceding Snapshot fixes June30quarter context. |

Publication July27,2026 and June30measurement date are explicitly distinct. No unsupported consolidated/standalone scope, investment advice, valuation or latest/current claim was added. This is historical Q1FY27 coverage relative to as_of October16,2026; do not relabel it latest without further verified coverage. Generic Bear statements mean no supported adverse conclusion from the supplied release, not an assertion that the companies have no risks. PERSISTENT remains excluded/failed; no brief claims were approved for it.

Files changed by reviewer: this report only. Checks actually run across stages:6provider tests,7then10adapter tests,3live-prompt tests, local validator counterexamples, source hash/rebuild checks and all-entry human review. Initial failures and superseded decisions above remain preserved. Next dependency: director integration and final delivery; no further reviewer work required unless artifacts change.
