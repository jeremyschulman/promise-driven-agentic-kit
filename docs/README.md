# Documentation

The promise-driven-agentic-kit is a methodology and a set of reusable engineering
artifacts. Use this page to choose the shortest path from your current question to
the relevant guide.

## Choose a path

| I want to... | Start with | Continue with |
| --- | --- | --- |
| Understand the method quickly | [From Contract to Enforcement](contract-assessment/README.md) | [The assurance model](assurance-model/README.md) |
| Decide what should be an agent | [Choosing a Participant and Document Type](participant-types/README.md) | [Composing Promises](promise-graph/README.md) |
| Author or change an agent contract | [Authoring an Agent Contract](authoring-workflow/README.md) | [Contract anatomy](../skills/authoring-agent-contracts/references/contract-anatomy.md) |
| Evolve an existing contract safely | [Evolving an Agent Contract](contract-evolution/README.md) | [The assurance model](assurance-model/README.md) |
| Diagnose a failed model check | [Debugging a FizzBee Counterexample](counterexample-debugging/README.md) | [The assurance model](assurance-model/README.md) |
| Compose several agents and services | [Composing Promises](promise-graph/README.md) | [Promise Theory architecture analysis](promise-theory-architecture.md) |
| Understand the theory | [The Promise-Driven Agent](why-promise-driven-agents.md) | [Promise Theory architecture analysis](promise-theory-architecture.md) |
| Evaluate the approach without formal-methods background | [Contracts, Not Prompts](contracts-not-prompts.md) | [From Contract to Enforcement](contract-assessment/README.md) |
| Scaffold a working project | [Skeleton guide](../skeleton/README.md) | [Authoring an Agent Contract](authoring-workflow/README.md) |
| Read the draft article series | [Medium article series](medium-articles/README.md) | [The Promise-Driven Agent](why-promise-driven-agents.md) |

## Design, Build, Run

The documentation follows the same lifecycle as the method:

| Stage | Engineering work | Primary guides |
| --- | --- | --- |
| **Design** | Define behavior, promises, conditions, and invariants; validate the XML; model-check reachable states; verify the promise graph. | [Authoring workflow](authoring-workflow/README.md), [counterexample debugging](counterexample-debugging/README.md), [Promise Graph guide](promise-graph/README.md) |
| **Build** | Bind tools, implement deterministic safeguards, create enforcement-twin tests, and run the complete gate. | [Authoring workflow](authoring-workflow/README.md), [contract-to-enforcement guide](contract-assessment/README.md) |
| **Run** | Give the contract to the LLM and reassess consequential operations against authoritative state. | [Contract-to-enforcement guide](contract-assessment/README.md), [assurance model](assurance-model/README.md) |

## Theory and architecture

- [The Promise-Driven Agent](why-promise-driven-agents.md) is the full whitepaper and
  eight-point rubric.
- [Contracts, Not Prompts](contracts-not-prompts.md) is the shorter conceptual
  introduction.
- [Promise Theory Architecture](promise-theory-architecture.md) examines composition,
  assessment, trust, and future architectural extensions.

## Practical guides

- [From Contract to Enforcement](contract-assessment/README.md) explains the six XML
  sections and traces one invariant into Python enforcement and test evidence.
- [Authoring an Agent Contract](authoring-workflow/README.md) walks from an intended
  promise to a contract, implementation guard, test twin, and green verification gate.
- [Choosing a Participant and Document Type](participant-types/README.md) distinguishes
  LLM contracts, deterministic manifests, shared-state and enforcement roles, external
  parties, implementation details, and superagent boundaries.
- [Composing Promises](promise-graph/README.md) explains offer/use binding, condition
  quenching, deterministic participants, external parties, and superagent entailment.
- [Debugging a FizzBee Counterexample](counterexample-debugging/README.md) turns a
  failed invariant trace into a classified design defect, repair, and complete recheck.
- [Evolving an Agent Contract](contract-evolution/README.md) maps local and structural
  changes across identifiers, peer agents, enforcement, tests, runtime consumers, and
  compatibility strategies.
- [Five Questions, Five Kinds of Evidence](assurance-model/README.md) explains what each
  verification layer establishes and, equally importantly, what it does not establish.

## Reference material

- [Annotated agent-contract schema](../schema/agent-contract.xsd)
- [Annotated non-LLM manifest schema](../schema/agent-manifest.xsd)
- [Shared Promise Theory vocabulary](../schema/promise-common.xsd)
- [Contract anatomy reference](../skills/authoring-agent-contracts/references/contract-anatomy.md)
- [Authoring checklist](../skills/authoring-agent-contracts/references/authoring-checklist.md)
- [Complete worked examples](../examples/)
