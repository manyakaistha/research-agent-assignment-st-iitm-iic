# General agent orchestration contract

Use T3 Code as the coordinating environment. The parent agent is the director:
it decomposes the task, assigns bounded work, integrates results, and owns the
final decision and deliverable. This file defines delegation only; the task
prompt supplies the domain, data, constraints, and output format.

## Capacity and delegation

- Count the director in the global four-agent limit.
- Use at most three active worker agents.
- Do not create nested agent pools. Workers request more work from the
  director instead of spawning their own workers.
- Keep independent implementation and review ownership separate.
- Use parallel workers only for genuinely independent tasks. Keep dependent
  work sequential: discovery before implementation, implementation before
  review, and review before final integration.
- Keep one critic or independent reviewer involved in substantive work.

## Model routing

| Work type | Model | Effort | Expected output |
|---|---|---:|---|
| File discovery, bounded reading, simple checks | `gpt-6-luna` | low | Paths, facts, raw evidence, and omissions |
| Structured extraction, inventories, evidence maps | `gpt-6-luna` | medium | Complete structured data with source locations |
| Bounded implementation and routine code review | `gpt-6.1-sol` | medium | Working code, tests, and implementation notes |
| Integration, debugging, statistics, adversarial review, production review | `gpt-6.1-sol` | high | Technical conclusions, risks, and corrections |
| Difficult proofs, complex system reductions, or coupled planning | `gpt-6-astra` | high | A bounded proof or formal analysis with assumptions |

Use the cheapest model that can reliably complete the task. Do not use Astra
for routine reading or mechanical work. Do not silently substitute a stronger
model when the assigned model is unavailable; report the limitation and ask
the director to revise the route.

Reasoning effort may be `low`, `medium`, or `high`. Never request `xhigh`,
`max`, or `ultra`.

## Task decomposition

Before spawning a worker, the director must define:

- a unique task ID;
- one concrete question or falsifiable hypothesis;
- exact files, inputs, or a read-only scope;
- exclusive files the worker may modify, if any;
- the expected deliverable and evidence format;
- CPU, time, storage, or output limits;
- the named independent reviewer;
- prohibited dependent work; and
- a stop condition.

Prefer this general sequence:

1. **Discovery:** inventory files, interfaces, dependencies, and constraints.
2. **Structured extraction:** turn raw material into a source-indexed evidence
   map or requirements table.
3. **Design:** compare approaches and define the smallest viable implementation.
4. **Implementation:** have one worker own the code and focused tests.
5. **Independent review:** have a different worker challenge correctness,
   leakage, unsupported assumptions, and edge cases.
6. **Integration:** the director resolves disagreements, runs final checks,
   and produces the user-facing result.

Do not ask a single worker to discover, implement, and approve its own work.
Do not spend a stronger model on work that can be returned as bounded facts by
Luna.

## Escalation

Escalate only once per bounded task and only for an evidenced ambiguity,
failure, or need for deeper reasoning. Use these routes:

- Luna/low → Luna/medium or Sol/medium
- Luna/medium → Sol/medium
- Sol/medium → Sol/high
- Sol/high → Astra/high

Record the original task, failure or ambiguity, replacement route, and reviewer.
Escalation increases reasoning strength; it does not expand the task scope or
change the acceptance criteria.

## Handoffs and review

Every worker response must include:

- status and summary;
- files changed or inspected;
- evidence locations and important omissions;
- tests or checks actually run;
- resource usage where requested;
- unresolved risks or contradictions; and
- the next dependency, if any.

Mechanical workers report evidence without making final scientific or product
claims. Stronger reviewers interpret the evidence and own technical
conclusions. The director integrates disagreements using source inspection,
tests, counterexamples, or a clearly recorded decision—not majority vote.

Preserve failed attempts, negative findings, and superseded decisions. Do not
delete evidence, weaken a gate, or revise acceptance criteria to make a result
pass.

## Spawn requirements

When using T3 Code delegation, pass an explicit model, reasoning effort, clean
context policy, and a bounded task message. The task message must include the
scope and reviewer. A routing plan prepares delegation; it does not itself
execute work or authorize experiments outside the user’s prompt.
