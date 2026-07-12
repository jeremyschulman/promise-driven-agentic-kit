# promise-driven-agentic-kit

## The short version

**We believe businesses should be able to automate the complex, knowledge-intensive
workflows that actually run them, including workflows conventional software could
never capture. AI makes that possible, but only if we stop engineering autonomous
agents as though they were deterministic programs.**

An LLM does not execute an instruction the way ordinary software executes code. It is
autonomous and stochastic. We can ask it to act, but a prompt cannot guarantee
obedience. We can elicit a promise, give it scoped authority, and independently assess
whether that promise was kept.

The promise-driven-agentic-kit turns that principle into an engineering method. It
uses model-checked contracts to make agent promises explicit, deterministic
enforcement to protect consequential boundaries, and runtime evidence to assess what
actually happened. It is not another agent framework. It is a framework-independent
kit for designing, building, running, and assessing trustworthy agentic workflows.

**Begin with the [Corpus Table of Contents](docs/corpus-table-of-contents.md)** for the
complete reading path through the methodology, practitioner guides, learning material,
examples, essays, and reference assets.

## Why this exists

Businesses have always had workflows that resist automation. They cross organizational
boundaries, depend on institutional knowledge, accumulate exceptions, and require
judgment that is difficult to encode as deterministic logic. Traditional automation
works best when every important path can be specified in advance. Many of the
workflows that matter most do not fit that shape.

AI changes what is reachable. An LLM can interpret language, recover intent, navigate
ambiguity, and participate in processes that once required a person at every step. It
creates an opportunity to automate complex business workflows that were previously
too tangled or expensive to capture in software.

But that opportunity introduces a different engineering problem. The component making
decisions is no longer deterministic. It may misunderstand, omit a step, invent an
argument, or take a plausible action that violates an important business rule.

More detailed prompts can improve behavior, but they cannot turn a stochastic model
into deterministic code. A prompt is a request to an autonomous participant, not an
enforceable constraint. For a conversational assistant, that distinction may be
acceptable. For a stateful workflow involving identity, money, authorization, safety,
or irreversible actions, it is the central architectural concern.

The question therefore changes:

> How do we build useful systems from agents we cannot command, without trusting them
> to police their own promises?

## The reframe: promise and assess

Promise Theory begins with autonomy: an agent can make promises only about its own
behavior. Another agent can request, guide, or constrain access to resources, but it
cannot impose a genuine promise on an autonomous participant.

That description fits an LLM as an engineering fact. We can elicit a promise through
instructions, but the promise has value only when its recipient can assess whether it
was kept.

This leads to the core discipline of the kit:

- Make the promises attributed to each runtime agent explicit and assessable.
- Give each agent only the authority it needs.
- Model-check selected consequential properties of the intended behavior before
  deployment.
- Pair stochastic promises with independent assessment and authority-boundary
  promises.
- Preserve evidence so trust is based on observed outcomes rather than confidence in
  a prompt.
- Compose a system only from promises its participants can actually keep.

The goal is not to remove autonomy from the model. The goal is to place an independently
controlled boundary promise underneath the autonomous actor. The LLM remains free to
interpret and propose; the authoritative software boundary decides whether a
consequential action may occur.

## How the method works

Each LLM agent is described by one XML **agent contract**. The contract combines
purpose, a model-checkable behavior model, Promise Theory relationships, runtime
guidance, enforcement traceability, and response language in one coordinated source.
Deterministic services publish smaller **agent manifests** describing the promises
they offer and use.

Here, **contract** means a structured promise proposal and engineering record, not an
obligation imposed on an autonomous model. Authoring the XML does not make the LLM
comply; the runtime behavior and authoritative outcomes must still be assessed.

Those documents move through a **Design → Build → Run → Assess** lifecycle:

- **Design:** Capture the workflow and its forbidden states. Validate the contract,
  model-check its behavior with FizzBee, and verify that every declared dependency in
  the promise graph has a provider.
- **Build:** Give the verified contract to the engineer and AI coding assistant. Use it
  to implement framework wiring, authoritative Python enforcement, and matching tests
  that exercise both allowed and refused operations.
- **Run:** Give the same contract to the LLM as its complete instruction set. Let it
  propose actions, but reassess consequential operations against authoritative state
  before committing them. A failed condition produces a structured refusal, not a
  hopeful exception.
- **Assess:** Preserve promise-specific evidence about what was proposed, allowed,
  refused, or left unknown. Review each kind of evidence for the claim it can support,
  then feed findings into the next design cycle.

Model checking proves the specified behavior model. It does not prove the stochastic
LLM, the generated Python, or the production environment. Deterministic enforcement,
its test twin, composition checks, and runtime assessment address those separate
questions. No single layer is asked to prove more than it can.

## What this repository provides

This repository is a methodology kit you build with, not a software system you deploy
and not a runtime framework you adopt.

| Folder | What it provides |
| --- | --- |
| `docs` | The complete methodology: foundations, practitioner guidance, learning paths, end-to-end case studies, essays, and reference material. |
| `schema` | Annotated XSD schemas for LLM agent contracts, deterministic agent manifests, and their shared Promise Theory vocabulary. |
| `skills` | An AI-assisted authoring procedure for creating, validating, model-checking, enforcing, and reviewing contracts. |
| `skeleton` | A Copier template that scaffolds a new contract-driven agent package with a working example and verification gate. |
| `examples` | Two runnable systems using different agent frameworks but the same contract, verification, enforcement, and assessment architecture. |

The method is intentionally framework-independent. The included Clinic Appointments
example uses Google ADK; Trials of the Holy Grail uses Pydantic AI. The framework
wiring changes. The contract structure, verification gates, and authority-boundary
discipline do not.

## When to use it

This method is designed for workflows where incorrect behavior has consequences and
where "probably correct" is not a sufficient engineering claim. It is especially
relevant when a system is:

- Multi-step or stateful
- Composed from several LLM and deterministic participants
- Responsible for money, identity, authorization, safety, or irreversible actions
- Dependent on ordering constraints or authoritative shared state
- Expected to evolve without silently weakening previous guarantees

It is deliberately more engineering than a prose prompt. For one-shot questions,
single-tool lookups, low-consequence assistants, or disposable prototypes, that work
may not be justified. A good prompt can be the right solution. Contracts become
valuable when the cost of an unexamined path is greater than the cost of proving and
enforcing the important ones.

## Where to begin

- **Understand the wager:** [Contracts, Not Prompts](docs/contracts-not-prompts.md)
  gives the shortest conceptual introduction.
- **Follow the full argument:** [The three-part essay series](docs/medium-articles/README.md)
  develops the Why, the single-agent method, and its composition at system scale.
- **See the complete map:** [Documentation Map](docs/README.md) offers
  question-driven routes, while the [Corpus Table of Contents](docs/corpus-table-of-contents.md)
  provides the full reading order.
- **Learn the method:** [Practitioner Learning Path](docs/learning-path/README.md)
  provides an orientation, workshop, knowledge check, and role-specific paths.
- **Trace contract to code:** [From Contract to Enforcement](docs/contract-assessment/README.md)
  follows the six coordinated contract sections into Python enforcement and tests.
- **Study a complete system:**
  [Clinic Appointments: An End-to-End Case Study](docs/case-studies/clinic-appointments/README.md)
  reconstructs the architecture, contracts, implementation, runtime, and evidence.
- **Examine the theory:** [The Promise-Driven Agent](docs/why-promise-driven-agents.md)
  develops the Promise Theory foundation and assurance rubric.
- **Review the interpretation and its limits:**
  [Promise Theory Interpretation and Open Questions](docs/promise-theory-interpretation.md)
  distinguishes canonical principles from project-specific mappings and frames the
  questions on which expert correction is invited.
- **Build with the kit:** [Scaffold a new agent](skeleton/README.md) or inspect the
  complete [worked examples](examples/).

## License

Licensed under [Apache-2.0](LICENSE).

---

*This is a living methodology kit. Contributions, corrections, and challenges to its
claims are welcome.*
