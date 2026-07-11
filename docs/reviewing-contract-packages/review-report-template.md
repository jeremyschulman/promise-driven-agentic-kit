# Contract Package Review Report

Use this template for pull requests, architecture reviews, release gates, or periodic
assurance reviews. Delete prompts that do not apply; do not delete required evidence
because it is unavailable.

## Review decision

**Outcome:** Approved | Approved with follow-up | Changes required | Unable to assess

**Decision basis:**

State the highest unresolved severity and the assurance claim it affects.

## Scope

| Item | Reviewed value |
| --- | --- |
| Workflow or package | |
| Consequential operations | |
| Agent contracts and versions | |
| Deterministic manifests and versions | |
| Implementation revision | |
| Schemas and verifier versions | |
| Runtime or deployment context | |
| Explicit exclusions | |

## Findings

List findings before summaries, ordered P0 through P3.

### [P0-P3] Finding title

**Evidence location:** artifact, section or line, and stable identity

**Observed behavior:**

**Consequence:**

**Required change:**

**Closure verification:**

**Owner and due condition:**

## Traceability matrix

Add one row per consequential promise or safety property.

| Promise | Safety identity | Condition identities | Capability | Provider/use | Python boundary | Enforcement twin | Runtime assessment | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | |

## Gate evidence

| Gate | Artifact version | Result | Evidence reference | Claim supported | Important limitation |
| --- | --- | --- | --- | --- | --- |
| XSD validation | | | | Structural completeness | No behavioral-safety claim |
| FizzBee model check | | | | Invariant coherence over reachable modeled states | No Python or LLM correctness claim |
| Promise-graph verification | | | | Declared binding and quenching coherence | No runtime availability claim |
| Enforcement tests | | | | Exercised implementation paths | No universal runtime claim |
| Runtime assessment | | | | Current decision against authoritative state | No future-behavior claim |

## Runtime readiness

- [ ] Authoritative state owner is named.
- [ ] Guards precede protected mutation.
- [ ] Concurrency and transaction boundary are reviewed.
- [ ] Receipt and structured-refusal shapes are defined.
- [ ] Failure and unknown outcomes are distinguishable.
- [ ] Idempotency and reconciliation are defined.
- [ ] Assessment records resolve to contract and implementation versions.
- [ ] Privacy classification, redaction, access, and retention are defined.

## Residual risk

Describe meaningful behavior outside the model, test suite, authoritative boundary, or
review scope. Name its owner and planned evidence.

## Follow-up register

Only P2 and P3 items may remain after approval with follow-up.

| Finding | Severity | Owner | Closure condition | Due event | Status |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## Evidence reviewed

List exact files, generated reports, test runs, runtime samples, diagrams, and review
conversations needed to reproduce the decision.

## Reviewers

| Role | Name | Scope assessed | Date |
| --- | --- | --- | --- |
| Contract or workflow owner | | | |
| Formal-model reviewer | | | |
| Enforcement or service owner | | | |
| Runtime or operations reviewer | | | |
| Privacy or domain reviewer, when required | | | |
