# Promise-Driven Agentic Kit

## Why this exists

**Organizations should be able to harness the transformational potential of AI in
consequential workflows without surrendering control, explainability, or operational
confidence.**

Many consequential workflows resist conventional automation because they cross
organizational boundaries, depend on institutional knowledge, accumulate exceptions,
and require judgment that cannot be fully specified in advance. LLMs change what is
reachable by interpreting language, recovering intent, and navigating ambiguity in
processes that once required a person at every step. But that capability creates a
different engineering problem: the component proposing actions is stochastic. A more
detailed prompt may improve its behavior, but cannot make it deterministic or enforce
an important business rule.

The question therefore changes:

> How do we build useful systems from agents we cannot command, without trusting them
> to police their own promises?

One promising approach draws on insights from my career at the intersection of
emerging technologies and business acceleration. I helped advance the network
automation movement as part of a passionate group of people around the world who set
out to change the industry, and did; I was part of the pioneering effort that brought
intent-based networking into practice; and today, I am applying those lessons to
autonomous business-process automation with AI. Across these efforts, the same pattern
has emerged: Promise Theory provides a way to reason about autonomous participants, an
intent-based design gives downstream systems a shared source of truth, and state
machines make complex workflows explicit. Together, these insights suggest a way to
use nondeterministic LLMs in consequential workflows: let them interpret and propose,
while explicit designs and deterministic boundaries govern which state transitions
may occur.

The result is a framework-independent kit for designing, building, running, and
assessing agentic workflows: structured contracts that serve as shared design
artifacts, model checks that verify selected behavioral properties, implementation
patterns that enforce consequential decisions, and runtime evidence that supports
assessment of whether promises were kept.

[![An LLM proposes an action, a deterministic boundary reassesses authoritative state,
the operation is committed or refused, and promise-specific evidence is
recorded](docs/runtime-assessment/runtime-assessment-flow.png)](docs/runtime-assessment/runtime-assessment-flow.svg)

*LLMs propose. Deterministic boundaries decide. Evidence records what happened.*

---

## The reframe: promise and assess

Promise Theory begins with autonomy: an agent can make promises only about its own
behavior. That description fits an LLM as an engineering fact. We can request behavior
through instructions, but the resulting promise has value only when its recipient can
assess whether it was kept.

This leads to the core discipline of the kit:

- Make each participant's promises explicit and assessable.
- Give each participant only the authority it needs.
- Model-check intended behavior and enforce consequential boundaries independently.
- Preserve runtime evidence, and compose systems only from promises their participants
  can keep.

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
  model-check it with FizzBee, and verify that every declared dependency has a
  provider.
- **Build:** Use the verified contract to implement framework wiring, authoritative
  enforcement, and tests for both allowed and refused operations.
- **Run:** Give the contract to the LLM as its instruction set, but reassess
  consequential operations against authoritative state before committing them.
- **Assess:** Preserve evidence of what was proposed, allowed, refused, or left unknown,
  and feed the findings into the next design cycle.

Model checking proves the specified behavior model. It does not prove the stochastic
LLM, the generated Python, or the production environment. Deterministic enforcement,
its test twin, composition checks, and runtime assessment address those separate
questions. No single layer is asked to prove more than it can.

## What this repository provides

This is a methodology kit you build with, not runtime software you deploy.

| Folder | What it provides |
| --- | --- |
| `docs` | The complete methodology: foundations, practitioner guidance, learning paths, end-to-end case studies, essays, and reference material. |
| `schema` | Annotated XSD schemas for LLM agent contracts, deterministic agent manifests, and their shared Promise Theory vocabulary. |
| `skills` | An AI-assisted authoring procedure for creating, validating, model-checking, enforcing, and reviewing contracts. |
| `skeleton` | A Copier template that scaffolds a new contract-driven agent package with a working example and verification gate. |
| `examples` | Two runnable systems using different agent frameworks but the same contract, verification, enforcement, and assessment architecture. |

The examples demonstrate the same contract and assurance method across Google ADK and
Pydantic AI.

## When to use it

This method is designed for workflows where incorrect behavior has consequences and
where "probably correct" is not a sufficient engineering claim. It is especially
relevant when a system is:

- Multi-step or stateful
- Composed from several LLM and deterministic participants
- Responsible for money, identity, authorization, safety, or irreversible actions
- Dependent on ordering constraints or authoritative shared state
- Expected to evolve without silently weakening previous guarantees

This rigor may not be justified for one-shot questions, simple lookups, or disposable
prototypes. Contracts become valuable when the cost of an unexamined path exceeds the
cost of specifying and enforcing the important ones.

## Where to begin

- **Choose a route:** The [Documentation Map](docs/README.md) offers question-driven
  paths, while the [Corpus Table of Contents](docs/corpus-table-of-contents.md) provides
  the complete reading order.
- **Understand the wager:** [Contracts, Not Prompts](docs/contracts-not-prompts.md)
  gives the shortest conceptual introduction.
- **Learn the method:** [Practitioner Learning Path](docs/learning-path/README.md)
  provides an orientation, workshop, knowledge check, and role-specific paths.
- **Study a complete system:**
  [Clinic Appointments: An End-to-End Case Study](docs/case-studies/clinic-appointments/README.md)
  reconstructs the architecture, contracts, implementation, runtime, and evidence.
- **Build with the kit:** [Scaffold a new agent](skeleton/README.md) or inspect the
  complete [worked examples](examples/).

## License

Licensed under [Apache-2.0](LICENSE).

---

*This is a living methodology kit. Contributions, corrections, and challenges to its
claims are welcome.*
