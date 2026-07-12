# Promise Theory Interpretation and Open Questions

## Purpose and status

This note prepares the promise-driven-agentic-kit for review by readers with deep
Promise Theory expertise. It distinguishes three things that the rest of the corpus can
otherwise make sound more settled than they are:

1. **Canonical principle** — a concept drawn directly from Promise Theory.
2. **Engineering interpretation** — how this kit maps that concept into XML, FizzBee,
   Python, tests, and runtime evidence.
3. **Proposed extension** — a useful mechanism introduced by the kit whose fidelity to
   Promise Theory remains open to review.

This is not a claim of conformance. It is an account of the kit authors' present
reasoning, known simplifications, and questions on which expert correction is invited.

## Canonical foundations used by the kit

| Promise Theory concept | Principle used here | Kit representation |
| --- | --- | --- |
| Autonomy | An agent can promise only its own behavior. Another agent may request cooperation but cannot promise on its behalf. | Each LLM workflow, deterministic service, shared-state boundary, external party, and superagent exterior is modeled as a distinct participant. |
| Promise structure | A promise has a promiser, promisee, body, and scope. | XML offers and uses name participants and bodies. Direct participants are represented; scope is not yet first-class. |
| Polarity | Cooperation requires a compatible promise to offer `+b` and promise to accept or use `-b`. | `<offer>` and `<use>` declarations are matched by stable identifiers. |
| Conditional and assisted promises | A promise may depend on a condition, and a promiser may promise to acquire assistance that quenches the condition. | `<condition ref="...">` identifies the condition; `<use quenches="...">` identifies an accepted dependency. |
| Assessment | Whether a promise was kept is a local judgment made by an assessor with available evidence. | Runtime records name the assessor, promiser, promise, condition, evidence, and local result. |
| Trust | Trust is derived from prior assessments and affects future reliance; it does not create obligation. | The runtime guide permits scoped trust signals but prohibits them from bypassing authoritative guards. |
| Superagency | A society of agents may present an exterior identity and make collective promises that depend on interior cooperation. | A superagent manifest publishes exterior offers and names interior offers proposed as their support. |

Primary sources include Bergstra and Burgess, *Promise Theory: Principles and
Applications*, Burgess, *Thinking in Promises*, and Burgess's
[Promise Theory resources](https://markburgess.org/promises.html).

## The central interpretation: contract, proposal, and adoption

The word **contract** in this kit names a structured engineering artifact. It does not
mean an obligation imposed on an autonomous agent, and writing the XML does not by
itself cause an LLM to make or keep a promise.

An engineer or AI coding assistant authors the XML outside the runtime LLM. From a
strict Promise Theory viewpoint, that artifact may initially be better understood as a
**promise proposal** and an instruction offered to the eventual runtime agent. The
runtime assembly is configured to read it, expose the declared capabilities, and attempt
to behave accordingly. Its behavior supplies evidence about whether the proposal was
adopted and whether the resulting promises were kept.

An unresolved modeling choice is where to draw the promiser boundary:

- Around the bare LLM invocation
- Around the LLM, system instructions, tools, and runtime wrapper
- Around the LLM and the authoritative service as a larger superagent

The kit currently uses **LLM agent** as practical shorthand, while its guarantees
usually belong to the larger engineered boundary. Expert review is requested on which
boundary best preserves autonomy without hiding the stochastic component.

## One safety case decomposed into separate promises

Consider a request to commit an action only when `precondition_met` is true.

| Agent | What it controls | Promise it may make | Assessment or evidence |
| --- | --- | --- | --- |
| Workflow LLM | Its proposed tool call and response | Propose `commit_action` only when the contract's stated condition applies | The authority service or requester may assess the proposal against authoritative facts. |
| Authority service | Whether authoritative state changes | Never commit the action unless its own guard observes `precondition_met` | Its decision, receipt, refusal, and state transition provide evidence about its promise. |
| Requester | Its reliance and interpretation | Accept or use a successful result under its own conditions | It independently assesses whether the externally visible promise was kept. |
| Combined workflow boundary | The capability presented to the requester | Provide a safe conditional commit capability | The exterior assessment depends on both the proposal path and the authority service outcome. |

If the LLM proposes an unsafe commit and the service refuses it, at least two distinct
statements may be true:

- The LLM's proposal promise was assessed as **not kept**.
- The authority service's no-unsafe-commit promise was assessed as **kept**.

The service did not keep the LLM's promise on its behalf. It assessed the proposal and
kept its own boundary promise. The combined system may still keep its exterior safety
promise because the consequential state transition was refused.

The kit uses **enforcement** for this authoritative accept-or-refuse boundary. The word
does not mean forcing the LLM to behave. It means the service controls its own state and
keeps its own promise about the conditions under which that state may change.

## FizzBee as an engineering mapping

The embedded FizzBee model is not Promise Theory notation and the model checker does
not prove that an LLM will keep a promise. The kit makes the following engineering
mapping:

- A FizzBee guard represents a state precondition associated with a conditional
  promise.
- A FizzBee assertion represents a safety claim that the contract publishes as a
  promised outcome.
- Stable identifiers connect the model claim to the XML promise, Python boundary, test,
  refusal, and runtime assessment.
- Model checking determines whether the specified state machine satisfies that claim
  for all reachable states under the model's assumptions.

This is a design-time coherence check. It is not a proof of the LLM, generated Python,
dependencies, infrastructure, or real-world outcome. Those require separate evidence.

## Promise-graph and superagent limits

The current promise-graph verifier establishes structural properties:

- Every declared use has a matching offer.
- Every condition is linked to a proposed quencher or marked for local assessment.
- Every `entailed-by` reference names an existing interior offer.

It does not prove that two agents interpret a body identically, that an offered service
will be available when needed, or that referenced interior promises semantically entail
an exterior superagent promise. Human review currently decides semantic adequacy.

Promise Theory also permits irreducible promises that emerge only at the superagent
scale. The kit's reference-based entailment is therefore a conservative traceability
mechanism, not a complete calculus of collective agency.

## Scope and observer limits

Promise Theory scope identifies the agents that know about a promise. The current XML
names direct promisers, promisees, providers, and assessors but does not represent scope
as a separate first-class structure. In many examples, the practical default is the
promiser, promisee, and named engineering or compliance observers.

That simplification may become inadequate when promises cross organizations, when
different interior and exterior audiences see different bodies, or when a superagent
boundary intentionally hides interior detail. Whether scope belongs in the schema is an
explicit design question.

## Applicability to autonomous business-process automation

### Working hypothesis

The methodology is intended for complex, stateful business processes whose important
outcomes can be expressed as promises among identifiable participants and whose
consequential state changes pass through authoritative boundaries.

This likely covers a broad class of present and legacy business processes. Many such
processes already contain latent states, transitions, responsibilities, dependencies,
preconditions, refusals, and forbidden outcomes even when those elements exist only in
runbooks or institutional knowledge.

That does **not** establish that every business process should be represented as a
finite workflow, that every part should be formalized, or that this kit spans the full
generality of Promise Theory. The method deliberately formalizes consequential
structure while leaving interpretation, judgment, and language in prose.

### Conditions that make a process a strong fit

- Participants and authoritative state owners can be identified.
- Consequential operations can be intercepted before commitment.
- Important preconditions and forbidden outcomes are stable enough to name.
- Success, refusal, failure, and unknown outcomes can produce observable evidence.
- Dependencies can be represented as offers, uses, and conditions.
- The process can be decomposed into bounded state machines without pretending to
  formalize all human judgment.
- The cost of an unsafe or untraceable path justifies model, enforcement, and review
  work.

### Shapes that may exceed the present kit

| Process shape | Why the mapping may fail or require another method |
| --- | --- |
| Open-ended discovery, research, or creative work | Goals, states, and success criteria emerge during the work rather than preceding it. Promises may still model cooperation, but a fixed workflow contract can create false precision. |
| Processes with no authoritative commit boundary | If no participant can observe and refuse a consequential transition, deterministic safeguarding cannot provide the claimed protection. |
| Unobservable or disputed outcomes | Assessment cannot be made reliable when evidence is unavailable, incompatible, or controlled entirely by an untrusted party. |
| Continuously changing participants or runtime-discovered capabilities | The current graph verifier assumes a mostly static, offline-known set of contracts and identifiers. Dynamic promise negotiation needs additional machinery. |
| Highly continuous, probabilistic, or real-time control | A finite-state abstraction may omit dynamics that require probabilistic, hybrid-system, control-theoretic, or timing analysis. |
| Emergent collective outcomes | Some superagent promises cannot be reduced to named interior offers. Structural `entailed-by` references may be insufficient. |
| Adversarial interaction without voluntary cooperation | Promise Theory can describe the parties, but this method cannot manufacture a promise, evidence, or authoritative boundary where none exists. |
| Human social processes expressed as imposed requirements | Encoding what management wants another party to do as that party's promise would violate autonomy and create a category error. |
| Low-consequence, single-turn tasks | The method may work, but its proof and governance costs are unlikely to be justified. |
| Long-running distributed sagas with unresolved partial failure | The method needs richer temporal, reconciliation, compensation, and unknown-outcome models than the current examples demonstrate. |

These are limits of the current engineering profile, not necessarily limits of Promise
Theory itself.

## Questions for Mark Burgess

### Agency and promise formation

1. Is a developer-authored LLM contract best understood as a promise proposal, an
   imposition that the runtime agent may accept, or a promise made by a larger engineered
   agent boundary?
2. Where would you draw the most useful agent boundary: around the LLM invocation, the
   LLM plus runtime wrapper and tools, or the LLM plus authoritative services as a
   superagent?
3. Does the separation between an LLM's proposal promise and an authority service's
   no-unsafe-commit promise correctly preserve autonomy and assessment locality?

### Formal and compositional mapping

4. Is mapping FizzBee guards and assertions to conditions and promised safety outcomes
   a faithful engineering interpretation, provided the model is not presented as a
   Promise Theory proof?
5. Does `<use quenches="condition">` adequately represent assisted quenching, or does
   it collapse distinctions that should remain explicit?
6. Is reference-based superagent entailment a useful conservative check, and what would
   be required to reason about irreducible collective promises more faithfully?
7. Should Promise Theory scope become a first-class part of the XML schema, especially
   across organizational and superagent boundaries?

### Applicability and category boundaries

8. Does **autonomous business-process automation** fit naturally within Promise Theory,
   or does treating most legacy business processes as societies of promising agents
   overextend the theory?
9. What observable properties would justify the claim that this method can represent
   most presently known business processes? What counterexamples should define its
   boundary?
10. When does an activity cease to be a workflow in the useful engineering sense and
    become an adaptive network, open-ended search, market, negotiation, or other system
    shape requiring a different representation?
11. Which process characteristics make this contract-and-assessment profile unsuitable
    even when Promise Theory remains an appropriate analytical lens?
12. What category errors are most likely when converting a human or legacy business
    process into agents, promises, conditions, and authoritative boundaries?
13. How should the method handle endogenous goals, dynamically appearing agents, and
    promises negotiated only at runtime?

### Language and claims

14. Is **contract** a defensible name if it is explicitly separated from obligation,
    or would another term preserve the voluntary nature of promises more clearly?
15. Which claims in this corpus should be described as applications of Promise Theory,
    and which should be labeled project-specific hypotheses or extensions?

## What expert review may change

Answers to these questions may change the chosen agent boundary, terminology, XML
schema, promise-graph rules, superagent representation, or stated applicability of the
method. They should not be treated as requests for endorsement. The purpose of review
is to discover where the method is sound, where it is merely useful, and where it has
made a category error.
