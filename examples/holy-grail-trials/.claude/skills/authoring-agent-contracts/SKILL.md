---
name: authoring-agent-contracts
description: >-
  Author, edit, or review a contract-driven agent — the agent_*.xml and
  manifest_*.xml contract documents from the promise-driven-agentic-kit (or any
  repo scaffolded from it). Covers writing the FizzBee state machine and its
  invariants, the Promise Theory manifest (offers/uses/conditions), pairing every
  invariant with code enforcement, and running the schema + model-check +
  promise-graph gate. Use this whenever someone adds or changes an agent
  contract, an invariant, a promise offer/use, a step-guidance block, or an
  enforcement rule — or asks how to make an agent's behavior "provably" safe,
  how to validate/model-check a contract, or how to fix a schema/promise-graph
  failure — even if they never say the word "contract".
---

# Authoring agent contracts

## The mental model (read this first)

A contract document is a single artifact read by three consumers:

1. a **FizzBee model checker** — proves no reachable state violates an invariant;
2. the **agent constructor** — reads the Promise Theory manifest to build the agent; and
3. the **LLM at runtime** — receives the whole document as its instructions.

The reason this pattern exists: an LLM is an autonomous, **stochastic** agent. You
cannot command it — you can only publish a promise about the agent's behavior and
then *assess* whether it kept it. The contract is that published promise; the
enforcement code is the assessment; the model checker proves the promise is at
least self-consistent before anyone relies on it.

The governing discipline follows directly:

> **Formalize structure; leave judgment to prose.**
> Ordering, mutual exclusion, and safety invariants go in the FizzBee `<contract>`.
> Intent classification, tool choice, and wording go in prose (`<step-guidance>`,
> `<responses>`). Don't try to formalize the fuzzy parts — you'll fail. Don't leave
> the structural parts to prose — they'll drift.

## Two document types — pick one first

| Type | File | Has FizzBee? | Validated by | For |
| --- | --- | --- | --- | --- |
| **LLM agent** | `agent_<name>.xml` | yes (`<contract>`) | `schema/agent-contract.xsd` | a stochastic, conversational agent with multi-step state |
| **Non-LLM agent** | `manifest_<name>.xml` | no | `schema/agent-manifest.xsd` | a deterministic service, shared-state store, or external boundary |

A non-LLM agent has no state machine to model-check, but it is still a full
participant in the promise graph — it publishes offers other agents consume.

## Workflow

### 1. Start from a working example, not a blank file

Copy the repo's example and rename it. Reusing an already-validated,
already-model-checked document is far more reliable than authoring from scratch:

```bash
cp agent_contracts/agent_barista.xml   agent_contracts/agent_<name>.xml    # LLM agent
cp agent_contracts/manifest_machine.xml agent_contracts/manifest_<name>.xml # non-LLM agent
```

Set the root attribute: `workflow="<name>"` for an LLM agent, `agent="<name>"` for
a manifest. If your repo has no example, read `references/contract-anatomy.md`.

### 2. Fill the sections in order

For an LLM agent (`agent_*.xml`), all six are required:

| Section | Holds | Register |
| --- | --- | --- |
| `<objective>` | what the agent is for | prose |
| `<contract>` | the FizzBee state machine: state, guards, invariants | formal |
| `<promises>` | description, tools, `+offers`, `−uses` | declarative |
| `<step-guidance>` | per-action judgment, tool bindings, phrasing | prose |
| `<enforcement>` | the invariants your code enforces independently | declarative |
| `<responses>` | reusable reply templates | prose |

A manifest is just `<description>` + `<promises>`.

### 3. Write the FizzBee `<contract>`

This skill assumes you can write FizzBee. For the language itself, install
FizzBee's own reference skills (`fizz install-skills`) — don't reinvent that here.
The contract-specific rules:

- Keep `mode="runtime-instructions"` on the `<fizzbee>` tag. It makes `oneof` mean
  "explore all branches" to the checker and "the agent picks one" to the LLM. The
  schema enforces this value.
- Declare state in an `Init` action; give each capability an `atomic action` with
  `require` guards (the preconditions); state safety properties as
  `always assertion` invariants.
- Model uncertain outcomes (an API that may fail, a receipt that may be unreadable)
  with `oneof [True, False]` so the checker explores both.

### 4. Write the `<promises>` manifest

This is the half most people underweight. It is what makes the agent composable.

- **Offers (`+`)** — what this agent promises. Each needs an `id`, a `type` from the
  controlled vocabulary (see `references/contract-anatomy.md`), a `to` (space-separated
  promisees), and a `<body>`. A conditional offer carries `<condition ref="…"/>`.
- **Every condition must be quenched.** A `<condition ref="c"/>` is either satisfied by
  some agent's `<use … quenches="c">` or marked `assessed="self"` (the agent evaluates
  it itself). An unquenched condition is a promise-graph failure — that is the point:
  it surfaces a dependency nobody agreed to provide.
- **Uses (`−`)** — what this agent accepts from others. Each names the providing agent in
  `from`. If that agent is inside your system, it must publish an `<offer>` with the same
  `id`; the promise-graph verifier checks this binding.
- **Tools** — list only names that resolve to real callables at construction time.

By convention a `<condition ref="x"/>` uses the **same token** as the FizzBee guard
variable `x`, so the prose promise and the model-checked spec share one vocabulary.

### 5. Pair every invariant with code enforcement + a test — non-negotiable

This is the step that separates a real contract from theater, and the one most often
skipped. Model-checking proves the *state machine* cannot reach a bad state. It does
**not** prove the stochastic LLM follows the state machine — the model can still skip a
guard or fabricate an argument.

So for every `always assertion` in the contract:

1. Enforce it in your service/tool layer, independently of the model (e.g. refuse the
   write when the precondition is false; don't even expose a parameter the model could
   misuse).
2. Add a test that exercises the enforcement.
3. Restate it in the `<enforcement>` section, with the `<rule id="…">` matching the
   invariant name so the proof and the guard are traceably paired.

If you catch yourself thinking "the model check passed, we're covered" — you're not.

### 6. Run the gate

All of these must pass before the contract is done (adjust the runner to your repo):

```bash
# schema validation
xmllint --noout --schema schema/agent-contract.xsd  agent_contracts/agent_<name>.xml
xmllint --noout --schema schema/agent-manifest.xsd  agent_contracts/manifest_<name>.xml

# model-check every contract, verify the promise graph, run the tests
uv run python scripts/verify_fizzbee_contracts.py
uv run python scripts/verify_promise_graph.py
uv run pytest -q
```

## Common failures and how to fix them

| Symptom | Cause & fix |
| --- | --- |
| xmllint: `'x' is not an element of the set {…}` on `type` | The offer `type` must be one of the controlled vocabulary. See `references/contract-anatomy.md`; pick the closest category or extend the enum deliberately. |
| xmllint: `Missing child element(s). Expected is ( step-guidance )` | An LLM contract is missing a required section. All six are mandatory. |
| promise-graph: `condition 'c' is not quenched by any use` | Add a `<use … quenches="c">` on some agent, or mark the condition `assessed="self"`. |
| promise-graph: `uses 'x' which 'Y' does not offer` | The `use` id/`from` don't match any offer; fix them or add the missing offer to agent Y. |
| fizz: model check FAILS | The checker prints the exact step sequence to the bad state. Tighten a guard or correct the invariant — don't weaken the invariant just to pass. |
| model check passes but behavior is wrong at runtime | You skipped step 5. The invariant has no code twin. Add enforcement + a test. |

## Before you finish

Run through `references/authoring-checklist.md`. In particular, confirm every
invariant has a code twin — that is the load-bearing check.

## Reference files

- `references/contract-anatomy.md` — the full element/attribute structure of both
  document types, the promise `type` vocabulary with meanings, condition/quench
  semantics, and a validation-error → fix table. Read it when writing or debugging a
  contract.
- `references/authoring-checklist.md` — the pre-commit checklist.
