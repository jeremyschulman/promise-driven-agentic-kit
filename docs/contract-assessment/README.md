# From Contract to Enforcement

A contract-driven agent is described once, but that description has several jobs. The
XML contract is simultaneously a formal behavioral model, a Promise Theory manifest,
runtime guidance for an LLM, and a traceability record for safeguards implemented in
Python.

That concentration is useful, but it creates a reading problem: the six XML sections
use different descriptive registers, and their connections are expressed through
several kinds of identifiers. The figures in this guide provide two views of the same
architecture:

1. **The overview** explains the responsibility of each contract section and which
   part of the system consumes it.
2. **The trace** follows one generic safety promise from the XML model to a Python
   guard, a structured refusal, and an enforcement test.

The examples are intentionally domain-neutral. Names such as `NoUnsafeCommit`,
`precondition_met`, and `commit_action` stand in for invariants, conditions, and
capabilities in any workflow.

## Figure 1: one contract, six coordinated sections

[![Overview of the six contract sections and their consumers](contract-assessment-overview.png)](contract-assessment-overview.svg)

The six sections are not six versions of the same information. Each carries the kind
of statement best suited to its purpose:

| Section | Primary question | Register | Principal consumer |
| --- | --- | --- | --- |
| `<objective>` | What is this agent for? | Prose | LLM runtime |
| `<contract>` | Which states are reachable, and what must always hold? | Formal FizzBee | Model checker and LLM runtime |
| `<promises>` | What does this agent offer, use, and depend on? | Declarative Promise Theory | Agent constructor, promise-graph verifier, and LLM runtime |
| `<step-guidance>` | How should each action be judged and carried out? | Prose with action bindings | LLM runtime |
| `<enforcement>` | Which invariants have independent code safeguards? | Declarative traceability | Engineers, reviewers, and LLM runtime |
| `<responses>` | How are outcomes and refusals communicated? | Reusable prose | LLM runtime |

The contract therefore supports three readings before execution:

- The **schema validator** checks that the document has the correct shape.
- The **model checker** explores the FizzBee state machine and proves its invariants
  over every reachable modeled state.
- The **promise-graph verifier and constructor** resolve offers, uses, conditions,
  tools, and agent boundaries.

At runtime, the LLM receives the whole contract as instructions. Python services remain
the authoritative boundary for consequential operations. They assess the requested
operation against real state and either keep the promise or return a specific refusal.

This distinction matters: a model check proves the specification is internally safe.
It does not prove that a stochastic model will follow the specification. Independent
code enforcement closes that gap.

## Figure 2: tracing one assessed promise

[![Trace of identifiers from XML contract to Python enforcement](contract-assessment-trace.png)](contract-assessment-trace.svg)

The trace figure separates three identifier families that are easy to conflate.

### Safety identity

The FizzBee invariant name and the enforcement rule ID are deliberately identical:

```text
always assertion NoUnsafeCommit  <->  <rule id="NoUnsafeCommit">
```

This creates a reviewable link between the property proved in the model and the
safeguard expected in code. An enforcement test should name or cite the same invariant
so a reviewer can complete the trace.

### Condition identity

The condition token describes a fact that must hold:

```text
FizzBee variable/guard: precondition_met
Promise condition:      <condition ref="precondition_met"/>
Dependency satisfaction:<use ... quenches="precondition_met"/>
Refusal evidence:       {"unmet": "precondition_met"}
```

By convention, the same token is used across these locations. It lets the formal
model, promise graph, and runtime refusal speak about the same unmet dependency. A
condition may instead be marked `assessed="self"` when the promising agent evaluates
it without an external provider.

### Capability identity

Capability names bind declarations to executable behavior:

```text
<tool name="commit_action"/>  <->  Python callable commit_action(...)
```

For inter-agent cooperation, a consumer's `<use id="..." from="...">` must resolve to
an offer with the same ID on the named provider. Tool names and offer/use IDs can be
the same when that is useful, but they are separate relationships and should not be
treated as one global namespace.

## The Python assessment boundary

The Python function should not merely assume that the LLM honored the contract. It
reassesses the facts that protect the operation:

<p align="center">
  <a href="python-assessment-boundary.svg"><img src="python-assessment-boundary.svg" alt="Syntax-highlighted Python assessment guard" width="700"></a>
</p>

The shape of the refusal is part of the architecture:

- `refusal` identifies the declined operation in machine-readable form.
- `unmet` identifies the promise condition that failed.
- `message` provides evidence the agent can relay without inventing a reason.

The service owns the final decision because it can inspect authoritative state at the
moment of commitment. The LLM remains responsible for judgment, orchestration, and
communication, but it cannot bypass the guard by choosing different wording or tool
arguments.

## The enforcement twin

The matching test deliberately presents the service with a forbidden request. It
checks both the refusal evidence and the more important outcome: authoritative state
did not change.

<p align="center">
  <a href="python-enforcement-test.svg"><img src="python-enforcement-test.svg" alt="Syntax-highlighted Python enforcement twin test" width="640"></a>
</p>

## Authoring and review checklist

For each safety invariant:

- Give the FizzBee `always assertion` a stable, descriptive name.
- Use the exact same name for its `<rule id="...">` in `<enforcement>`.
- Use stable condition tokens across FizzBee guards, promise conditions, quenching
  uses, and structured refusals.
- Bind every declared tool name to a real Python callable.
- Enforce the invariant in the service or tool layer independently of the LLM.
- Add a test that attempts the forbidden operation and verifies that state is not
  changed.
- Run schema validation, model checking, promise-graph verification, and tests.

The resulting assurance is layered: the schema checks completeness, the model checker
checks reachability, the promise graph checks cooperation, and Python tests check the
real enforcement boundary.

## Image sources

The SVG files are the editable sources; the PNG files are rendered copies for Markdown,
articles, and presentation software:

- [`contract-assessment-overview.svg`](contract-assessment-overview.svg)
- [`contract-assessment-overview.png`](contract-assessment-overview.png)
- [`contract-assessment-trace.svg`](contract-assessment-trace.svg)
- [`contract-assessment-trace.png`](contract-assessment-trace.png)
- [`python-assessment-boundary.svg`](python-assessment-boundary.svg)
- [`python-assessment-boundary.png`](python-assessment-boundary.png)
- [`python-enforcement-test.svg`](python-enforcement-test.svg)
- [`python-enforcement-test.png`](python-enforcement-test.png)

The two Python SVGs are generated with Rich. Run `render_code_snippets.py` from a
Python environment containing `rich` to regenerate them after changing the examples.
