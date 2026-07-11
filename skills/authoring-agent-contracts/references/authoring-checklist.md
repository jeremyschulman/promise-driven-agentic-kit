# Authoring checklist

Run through this before considering a contract done. The load-bearing item is the
last one in each section — everything else is in service of it.

## Structure

- [ ] Correct document type: `agent_*.xml` (LLM, has `<verifiable-behavior>`) vs `manifest_*.xml` (non-LLM).
- [ ] Root attribute set: `workflow="…"` (LLM) or `agent="…"` (manifest); `version` present.
- [ ] LLM contract has all six sections in order: objective, verifiable-behavior, promises, step-guidance, enforcement, responses.
- [ ] `<fizzbee mode="runtime-instructions">`.
- [ ] The right things are formal (ordering, mutual exclusion, safety) and the right things are prose (classification, wording). No fuzzy judgment smuggled into the state machine; no safety rule left to prose.

## Promise graph

- [ ] Every `<offer>` has `id`, a valid `type`, `to`, and a `<body>`.
- [ ] Every conditional offer's `<condition>` is quenched by some `<use … quenches>` OR marked `assessed="self"`.
- [ ] Every `<use>` names a `from` agent that publishes a matching `<offer>` id (or is a declared external party).
- [ ] Condition `ref` tokens match the FizzBee guard variable names.
- [ ] Every `<tool name>` resolves to a real callable.

## The non-negotiable

- [ ] **Every `always assertion` invariant has: (a) code enforcement independent of the LLM, (b) a test, and (c) a matching `<rule id>` in `<enforcement>`.** The model check proves the spec, never the LLM's behavior.

## Gate — all green

- [ ] `xmllint --noout --schema schema/agent-contract.xsd <agent-file>` (and `agent-manifest.xsd` for manifests)
- [ ] `uv run python scripts/verify_fizzbee_contracts.py`
- [ ] `uv run python scripts/verify_promise_graph.py`
- [ ] `uv run pytest -q`
- [ ] Stamped `verified="fizz-<version>"` once model-checking is clean.

## Package review

- [ ] The complete Design, Build, and Run evidence chain has been evaluated using the
  [contract-package review guide](../../../docs/reviewing-contract-packages/README.md),
  with no unresolved P0 blocking defect or P1 assurance gap.
