# Intermediate test failures observed during integration

This record transcribes the failures observed in terminal tool results. These are historical observations, not newly executed tests. The complete original six-counterexample failure run is separately preserved in `review_before_fixes.txt`.

1. The first real localhost gateway integration test expected `Model validation failed` in the fallback reason but received `'Snapshot'`. The gateway request itself succeeded; the malformed `{}` model response reached rendering before schema validation. The assertion failed in `test_actual_keyless_http_gateway_and_failure_fallback`. Correction: validate the schema before rendering. The unchanged integration assertion now passes.
2. Adding mandatory temporal coverage to every direct call of the generic validator broke the valid single-claim grounding unit fixture in `test_validator_rejects_wrong_citations_and_injection`. Expected `[]`; observed `['missing dated historical/current pledge comparison with denominator']`. Correction: accept an explicit temporal-context argument. Production model runs pass the detected temporal evidence and enforce coverage; isolated grounding tests can validate one claim without pretending to be complete briefs. The original assertion remains unchanged and passes.

Subsequent final test files contain the latest passing results; this record retains the earlier negative findings and their resolutions. No original research document or failed model response was removed.
