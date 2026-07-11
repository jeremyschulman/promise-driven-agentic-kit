# 30-Minute Orientation

This orientation provides enough shared language to navigate the kit and participate
in a contract-package discussion. It does not make the learner a formal-model reviewer
or production-readiness approver.

## Learning outcomes

At the end, the learner should be able to:

- Explain why the method uses contracts rather than prose prompts alone.
- Name the six sections of an LLM agent contract and their responsibilities.
- Trace one safety promise through Design, Build, and Run.
- State what model checking proves and what it does not prove.
- Explain why structured refusal and runtime assessment are first-class outcomes.

## Minute 0-5: begin with the boundary

An LLM is stochastic and autonomous. It can interpret intent, select actions, and
communicate, but its output is not authoritative state. The surrounding system remains
responsible for what it accepts.

The method therefore pairs two responsibilities:

```text
LLM agent                    Deterministic boundary
interprets and proposes  ->  reads authoritative state
promises behavior            accepts or refuses the real operation
communicates result      <-  emits receipt or structured refusal
```

The code does not control what the model samples. It controls what the system allows
to commit.

## Minute 5-10: understand the whole contract

An LLM agent contract contains six coordinated section types:

| Section | Responsibility |
| --- | --- |
| `<objective>` | Purpose, scope, and judgment expressed in prose |
| `<verifiable-behavior>` | FizzBee state, actions, guards, and invariants |
| `<promises>` | Tools, offers, uses, conditions, and dependencies |
| `<step-guidance>` | Runtime judgment and action bindings for the LLM |
| `<enforcement>` | Traceability from invariant names to deterministic duties |
| `<responses>` | Honest communication of success, clarification, and refusal |

The whole XML document is the **agent contract**. The embedded behavior model is not a
second contract.

Deterministic participants publish narrower `manifest_*.xml` documents because they do
not need LLM instructions or an embedded FizzBee model.

## Minute 10-17: follow one promise

Use the generic statement:

> Commit the action only when `precondition_met` is true. Otherwise refuse, identify
> the unmet condition, and leave authoritative state unchanged.

It creates four identity chains:

| Identity | Trace |
| --- | --- |
| Safety | `NoUnsafeCommit` invariant -> `<rule id>` -> Python guard duty -> test and assessment |
| Condition | `precondition_met` state/guard -> `<condition ref>` -> `<use quenches>` -> refusal `unmet` |
| Capability | `<tool name="commit_action">` -> Python `commit_action(...)` |
| Promise | Provider `<offer id>` -> consumer `<use id>` together with `from` |

The provider capability might be named `evidence`; the fact it establishes might be
`precondition_met`. Those names should remain different because they represent
different relationships.

## Minute 17-23: separate the assurance layers

Five gates answer five questions:

1. **Schema validation:** Is the document structurally complete?
2. **FizzBee model check:** Can a reachable modeled path violate an invariant?
3. **Promise-graph verification:** Do offers, uses, and conditions compose?
4. **Enforcement-twin tests:** Does the exercised code refuse the forbidden operation
   without changing protected state?
5. **Runtime assessment:** May this real operation proceed against authoritative state
   now?

Confidence comes from preserving all five results. None substitutes for another.

The precise model-check claim is:

> The invariant holds over every reachable state represented by this bounded model.

It is not “the LLM is safe,” “the Python is proven,” or “the system cannot fail.”

## Minute 23-27: treat refusal and uncertainty honestly

Runtime operations have four terminal classifications:

| Outcome | Meaning |
| --- | --- |
| `committed` | The boundary accepted the operation. |
| `refused` | The boundary declined normally and protected state did not change. |
| `failed` | An unexpected implementation or dependency failure prevented a normal decision. |
| `unknown` | The boundary cannot yet determine whether the operation committed. |

Do not turn failures or unknown outcomes into friendly refusals. Unknown consequential
operations require reconciliation before retry.

Operational outcome is separate from promise assessment. A refused unsafe operation
can assess `NoUnsafeCommit` as `kept` and the conditional capability as
`not-applicable`.

## Minute 27-30: test the mental model

Answer aloud:

1. Which artifact decides whether the LLM followed its step guidance?
2. What proves that a provider actually offered a dependency used by another agent?
3. What must an enforcement twin assert beyond `ok is False`?
4. Why can a refusal represent a kept promise?
5. What should happen after a timeout leaves commit state unknown?

Expected answers:

1. No single artifact decides universally; the deterministic boundary makes the
   current accept-or-refuse decision, and named assessors record local judgments.
2. The promise-graph verifier resolves the consumer's `(from, id)` use to a provider
   offer.
3. The refusal code, unmet condition, and unchanged authoritative state.
4. The boundary may keep a safety promise by refusing when a required condition is
   false.
5. Reconcile through authoritative state or idempotency evidence before retrying.

## Continue learning

- Complete the [knowledge check](knowledge-check.md).
- Build the same chain in the [90-minute workshop](workshop.md).
- Choose a [role-specific path](role-paths.md).
- Keep the [Glossary and Naming Conventions](../glossary/README.md) nearby.
