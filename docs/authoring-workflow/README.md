# Authoring an Agent Contract

This guide is the practical path from an intended behavioral promise to a verified
contract, deterministic Python enforcement, and executable evidence. It uses generic
names so the method can be applied to any domain.

The central discipline is simple:

> Formalize structural behavior, leave judgment in prose, and independently assess
> every consequential operation in code.

## Before authoring: choose the participant type

Do not give every participant an LLM contract. Use
[Choosing a Participant and Document Type](../participant-types/README.md) when the
autonomy or document boundary is not yet clear.

| Participant | Document | Use when |
| --- | --- | --- |
| Stochastic LLM agent | `agent_<workflow>.xml` | The participant interprets intent, selects actions, or conducts a multi-step conversation. It has all six sections, including `<verifiable-behavior>`. |
| Deterministic agent or boundary | `manifest_<agent>.xml` | The participant is a service, shared-state store, protocol boundary, or other deterministic provider. It publishes promises but has no LLM behavior model. |

Start from a working file in the [skeleton](../../skeleton/template/agent_contracts/)
or one of the [examples](../../examples/). The schema fixes section order and required
attributes; copying a valid envelope avoids unproductive structural mistakes.

## Design 1: state the promise before writing XML

Write one consequential capability as a promise with four parts:

| Part | Question | Generic example |
| --- | --- | --- |
| Capability | What operation may occur? | Commit an action. |
| Condition | What fact must be true first? | `precondition_met` is true. |
| Refusal | What happens when the fact is false? | Return a structured refusal naming `precondition_met`. |
| State effect | What must remain unchanged after refusal? | Authoritative state is not modified. |

The working statement is:

> Commit the action only when `precondition_met` is true. Otherwise refuse, identify
> the unmet condition, and leave authoritative state unchanged.

This sentence is the seed for the model, promise graph, enforcement rule, Python guard,
and test. If the sentence cannot say what is forbidden and what evidence demonstrates
refusal, it is not ready to formalize.

## Design 2: choose stable identifiers

The kit deliberately carries meaning across several identifier families. Choose names
before filling the sections.

| Relationship | Identifier | Appears in |
| --- | --- | --- |
| Modeled action | `CommitAction` | FizzBee action and usually `<step-guidance action>` |
| Safety identity | `NoUnsafeCommit` | FizzBee `always assertion`, `<rule id>`, and test name or citation |
| Condition identity | `precondition_met` | State/guard, `<condition ref>`, `<use quenches>`, and refusal evidence |
| Capability binding | `commit_action` | `<tool name>` and Python callable |
| Promise identity | `safe_action` | `<offer id>` used by promisees |
| Dependency identity | `evidence` | `<use id>` matched to a provider's `<offer id>` |

These are related names, not one global namespace. Preserve identity where it creates
traceability; do not force unrelated concepts to share a string.

## Design 3: establish the six-section envelope

The **agent contract** is the whole XML document. `<verifiable-behavior>` is only the
section containing its exhaustively checkable behavior model.

```xml
<agent-instructions workflow="safe_workflow" version="1.0">
  <objective>...</objective>
  <verifiable-behavior>
    <fizzbee mode="runtime-instructions">...</fizzbee>
  </verifiable-behavior>
  <promises>...</promises>
  <step-guidance action="CommitAction">...</step-guidance>
  <enforcement>...</enforcement>
  <responses>...</responses>
</agent-instructions>
```

All six section types are required and ordered. There may be multiple
`<step-guidance>` blocks.

## Design 4: model the behavior that must always hold

Put states, actions, guards, and invariants in `<verifiable-behavior>`. Model uncertainty
with alternatives so the checker explores success and failure rather than assuming the
happy path.

```python
---
deadlock_detection: false
liveness: "false"
options:
  max_concurrent_actions: 1
---

action Init:
    precondition_met = oneof [True, False]
    committed = False

atomic action CommitAction:
    require precondition_met
    require not committed
    committed = True

always assertion NoUnsafeCommit:
    return (not committed) or precondition_met
```

The guard says when the action is permitted. The invariant says what must remain true
over every reachable modeled state. FizzBee may prove this model internally coherent;
it does not prove that an LLM will honor the guard at runtime.

Keep intent classification, nuanced tool choice, wording, and other fuzzy judgment out
of the model. Those belong in `<objective>`, `<step-guidance>`, and `<responses>`.

## Design 5: declare the promise and its dependencies

The `<promises>` section makes the behavior composable. It declares bound tools, offers
made to promisees, and uses accepted from providers.

```xml
<promises>
  <description>Commits an action only after its required evidence is present.</description>
  <tools>
    <tool name="commit_action"/>
  </tools>

  <offer id="safe_action" type="workflow" to="requester">
    <body>Commit the requested action only after its precondition is met.</body>
    <condition ref="precondition_met"/>
  </offer>

  <offer id="no_unsafe_commit" type="invariant" to="requester compliance">
    <body>An action is never committed before its precondition holds.</body>
  </offer>

  <use id="evidence" from="provider" quenches="precondition_met">
    <body>Use the provider's evidence to satisfy the commit precondition.</body>
  </use>
</promises>
```

The provider must publish an `<offer id="evidence">`, or the promise graph must treat
it as a declared external party. A condition that the agent evaluates itself uses
`<condition ref="..." assessed="self"/>` instead of an external quenching dependency.
For the full composition model, see [Composing Promises](../promise-graph/README.md).

## Design 6: write guidance, enforcement traceability, and responses

`<step-guidance>` tells the LLM how to exercise judgment and use the declared tool. It
does not replace the tool's guard.

```xml
<step-guidance action="CommitAction">
  <binding>
    Call commit_action only after obtaining evidence that precondition_met is true.
    Relay the tool result, including any structured refusal, without inventing success.
  </binding>
</step-guidance>

<enforcement>
  The service layer enforces this independently of the model:
  <rule id="NoUnsafeCommit">
    commit_action refuses unless precondition_met is true.
  </rule>
</enforcement>

<responses>
  <precondition-required>
    I cannot commit that action until [required evidence] is available.
  </precondition-required>
  <committed>The action was committed successfully.</committed>
</responses>
```

The exact `NoUnsafeCommit` spelling joins the model proof to the expected code duty.
The exact `precondition_met` token joins the model guard, promise condition, dependency,
and refusal evidence.

## Build 1: implement the authoritative boundary

The service or tool function reassesses real state at the moment of commitment. It must
not trust the LLM's claim that a condition was previously satisfied.

```python
def commit_action(*, precondition_met: bool) -> dict:
    if not precondition_met:
        return {
            "ok": False,
            "refusal": "precondition_required",
            "unmet": "precondition_met",
            "message": "The precondition must hold.",
        }

    apply_change()
    return {"ok": True, "committed": True}
```

In a real implementation, derive `precondition_met` from authoritative service state
when possible rather than exposing it as an assertion the model can choose.

## Build 2: create the enforcement twin

For every safety invariant, write a test that attempts the forbidden operation. Assert
both the refusal evidence and the more important outcome: state did not change.

```python
def test_no_unsafe_commit():
    result = commit_action(precondition_met=False)

    assert result["ok"] is False
    assert result["unmet"] == "precondition_met"
    assert authoritative_state_unchanged()
```

The test does not prove all runtime behavior. It demonstrates that the implemented
boundary keeps this invariant for the exercised case and makes regression detectable.

## Build 3: run the complete gate

Run each check because each answers a different question:

```bash
xmllint --noout --schema schema/agent-contract.xsd \
  agent_contracts/agent_safe_workflow.xml

uv run python scripts/verify_fizzbee_contracts.py
uv run python scripts/verify_promise_graph.py
uv run pytest -q
```

Do not repair a failing gate by weakening the promise until it passes. Read the failure
as evidence:

| Failure | What to inspect |
| --- | --- |
| XSD validation | Missing or misordered sections, required attributes, controlled vocabulary |
| [FizzBee counterexample](../counterexample-debugging/README.md) | The exact reachable action sequence; missing guard or incorrect invariant |
| Promise-graph failure | Unmatched offer/use, unquenched condition, or invalid declared entailment where that check is enabled |
| Enforcement-test failure | Guard logic, refusal evidence, or forbidden state mutation |

## Run: assess before committing

At runtime, the LLM receives the whole contract and may propose `commit_action`. The
Python boundary then reads authoritative state and decides whether to commit or refuse.
The LLM remains autonomous; the surrounding system remains responsible for what it
accepts as a kept promise.

Record enough structured evidence to explain the decision: operation, invariant or
policy identity, unmet condition, outcome, and correlation information appropriate to
the application. This is assessment evidence, not proof that future requests will
behave the same way.

## Definition of done

- The document validates against the correct schema.
- Every modeled action has explicit guards and state effects.
- Every safety invariant has a stable name.
- Every conditional offer is quenched or explicitly self-assessed.
- Every use resolves to a provider offer or declared external boundary.
- Every tool name resolves to a callable.
- Every invariant has an independent code guard, matching `<rule id>`, and test twin.
- Refusals identify the unmet condition and do not mutate forbidden state.
- Schema validation, model checking, promise-graph verification, and tests all pass.

For the exact element and attribute vocabulary, use the
[contract anatomy reference](../../skills/authoring-agent-contracts/references/contract-anatomy.md).
For a visual trace from XML identifiers into Python, continue with
[From Contract to Enforcement](../contract-assessment/README.md). When changing an
existing contract, use [Evolving an Agent Contract](../contract-evolution/README.md) to
trace its full change radius.
