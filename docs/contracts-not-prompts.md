# Contracts, Not Prompts: Model-Checked XML + FizzBee Instructions for LLM Agents

*A pattern for instructing stateful LLM agents, with two runnable worked examples in this kit: a clinic-appointment agent ([`examples/clinic-appointments/`](../examples/clinic-appointments/)) and the Trials of the Holy Grail ([`examples/holy-grail-trials/`](../examples/holy-grail-trials/)). Audience: engineers deciding how to instruct and constrain agents. No formal-methods background assumed.*

---

## TL;DR — the wager

Most LLM agents are instructed with a prose system prompt: *"You are a helpful clinic assistant. Always verify the patient before booking anything…"* Prose is easy to write and impossible to verify. For a one-shot Q&A bot that's fine. For a **stateful, multi-step, safety-sensitive agent**, it leaves a question you cannot answer: *can this agent ever reach a bad state — like booking an appointment before the patient is verified, or double-booking a slot?*

The pattern in this article answers that with a flat "no, provably." The agent's instructions **are** a formal state machine — written in [FizzBee](https://fizzbee.io), wrapped in XML, and **model-checked offline before deployment**. The same artifact is read by three consumers: the **LLM** (as operating instructions), a **model checker** (which proves invariants hold across every reachable state), and the **developer** (the single source of truth that the enforcement code and tests trace back to).

The verdict, up front: **worth it for stateful, multi-step, safety-sensitive agents; overkill for one-shot or single-tool assistants.**

---

## Why prose prompts break down

A system prompt is a *description of intent*. An LLM is a *stochastic executor*. The gap between the two is where production incidents live.

Consider the real requirements of the clinic agent in this kit:

- No workflow (book, cancel, reschedule) may run until the patient's identity is verified.
- An appointment may never be booked before insurance eligibility is checked (or self-pay is chosen).
- A slot may never be double-booked, and an appointment may never be modified by someone who doesn't own it.

You *can* write those as prose bullets. But three problems follow:

1. **No coverage guarantee.** Prose describes the happy path and a few edge cases the author imagined. It says nothing about the states the author *didn't* imagine.
2. **No single source of truth.** The prompt says one thing, the tool-wrapper code enforces another, the tests assume a third. They drift.
3. **No verification loop.** You change the prompt, ship it, and find out in production whether you introduced a contradiction.

A multi-step agent is a **state machine** whether you acknowledge it or not. Prose leaves that machine implicit and unchecked. This pattern makes it explicit and checks it.

---

## What the approach actually is

Each LLM agent's *entire* instruction set is an XML document with six sections (validated by [`schema/agent-contract.xsd`](../schema/agent-contract.xsd)):

```
<agent-instructions>
  <objective>       — what this agent is for (natural language)
  <contract>        — the FizzBee state machine: state, actions, guards, invariants
  <promises>        — the Promise Theory manifest: description, tools, +offers, −uses
  <step-guidance>   — per-action prose: LLM judgment, tool bindings, phrasing
  <enforcement>     — invariants the server enforces in code, independent of the LLM
  <responses>       — message templates for key replies
</agent-instructions>
```

The center of gravity is `<contract>`. Here is the verification rule from the clinic orchestrator, verbatim ([`agent_clinic_orchestrator.xml`](../examples/clinic-appointments/agent_contracts/agent_clinic_orchestrator.xml)):

```python
atomic action VerifyPatient:
    require not patient_verified
    require active_workflow == NO_WORKFLOW
    patient_verified = oneof [True, False]

always assertion PatientVerifiedBeforeWorkflow:
    return active_workflow == NO_WORKFLOW or patient_verified
```

Read it in plain English:

- **`action`** is something the agent can do; **`require`** clauses are *guards* — preconditions that must hold. `VerifyPatient` may run only when the patient is not yet verified and no workflow is active.
- **`oneof [True, False]`** models a nondeterministic outcome: verification might succeed or fail.
- **`always assertion`** is an **invariant** — a property that must be true in *every* reachable state. `PatientVerifiedBeforeWorkflow` says: either no workflow is active, or the patient is verified. There is no legal state where a workflow runs unverified.

FizzBee is a specification language in the TLA+/PlusCal lineage, with Python-like syntax that reads approachably.

### Model-checking: proving the invariants

A **model checker** (`fizz`) explores *every reachable combination of state variables* and checks that no invariant is ever violated. Each example runs it offline in CI (`scripts/verify_fizzbee_contracts.py`):

```
[PASS] book_appointment
[PASS] clinic_orchestrator
[PASS] manage_appointment
3/3 contract(s) passed model checking.
```

**This is not hypothetical.** The Trials of the Holy Grail example has a Quest Marshal that grants the Grail only after both trials are passed (`GrailRequiresBothTrials`). Its *first draft failed model-checking*: a knight could re-attempt an already-passed trial and flip it back to failed *after* the Grail was granted — violating the invariant. The checker returned the exact sequence of steps to the bad state, and the fix (making a passed trial sticky) was mechanical. The "can it ever…?" question was answered by exhaustive search, at design time, before an LLM or a user was anywhere near it.

### The crucial reinterpretation: `runtime-instructions` mode

In classic model checking, `oneof [A, B]` means "explore **both** branches." When the same document is handed to the LLM as instructions, `oneof` means "**you, the agent, select exactly one** path at runtime based on the conversation."

The contracts declare this: `<fizzbee mode="runtime-instructions">`. One artifact, two readings:

- **Model checker's reading:** explore all branches → prove no branch violates an invariant.
- **LLM's reading:** choose one branch → the invariants describe the box you must stay inside.

The checker proves the *space of allowed behavior* is safe; the LLM navigates within it.

### The other sections

- **`<step-guidance>`** is where fuzzy judgment lives — how to classify intent, which tool to call, how to phrase a reply. This is prose, because "is this message a greeting or a booking request?" is not a formal property.
- **`<enforcement>`** restates the invariants as rules the *server code* enforces, independent of the model. Every FizzBee invariant has a code twin and a test.
- **`<responses>`** are templates so critical replies are consistent.

The rule: **formalize structure and ordering; leave judgment and phrasing to prose.**

---

## Architecture: an orchestrator and its subagents

The clinic agent is one system exposed to a user, but internally it's an **orchestrator** plus **workflow subagents** plus **service/state agents**:

- **`clinic_orchestrator`** is the sole entry point. It verifies the patient, classifies intent, and routes. Read-only intents (list appointments, check eligibility) it handles directly.
- **`book_appointment`** and **`manage_appointment`** are subagents, each owning one multi-step workflow with its own contract (`book_appointment` proves `EligibilityBeforeBooking`, `NoDoubleBook`, `ConfirmBeforeBooking`).
- **`provider_schedule`**, **`insurance_eligibility`**, **`patient_registry`** are non-LLM service/state agents.

One workflow per subagent keeps each contract small enough to model-check and reason about. Shared state (the active patient) belongs to the registry agent, not smuggled between subagents.

---

## The Promise Theory lens

[Promise Theory](http://markburgess.org/promises.html), developed by Mark Burgess, reasons about systems built from **autonomous** parts. An LLM is *literally* such a part: you cannot impose behavior on it, only elicit a promise and then assess whether it was kept. So:

- **The contract is the agent's published promise.** `NoDoubleBook` is `book_appointment` promising *"I will never book a slot that's already taken."*
- **The enforcement code is the assessment.** Because the promiser is stochastic, the promisee must verify: `provider_schedule.commit_booking` refuses a taken slot **in code**, no matter what the model does. This LLM-promise + code-assessment pair is the whole methodology in one place — and it is why the code layer is **mandatory, not belt-and-suspenders**.
- **The system is a composition of promises.** "The clinic will book your appointment" is an *assisted promise*: kept only when identity, eligibility, an open slot, and confirmation all hold, each provided by a different agent.

---

## Framework independence

The methodology lives in the contracts and the enforcement code — **not** in any agent framework. This kit proves that with two examples that share the *same* contracts-and-enforcement shape but run on *different* runtimes: the clinic on **Google ADK**, the [Trials of the Holy Grail](../examples/holy-grail-trials/) on **Pydantic AI**. The only meaningful difference between them is one file (`agents/build.py`). Everything that makes them *safe* is identical.

---

## When to use it (and when not)

**Reach for it** when there are multi-step workflows, ordering or safety constraints that must hold, money/identity/irreversible actions, and a need to evolve without regressions.

**Skip it** for one-shot Q&A, a single-tool lookup, or a prototype where a wrong turn is cheap to undo. There, a good prose prompt is the right tool.

The biggest caveat: **model-checking proves the spec, not the LLM's behavior.** The model can still mis-classify intent or skip a step. That is exactly why the enforcement code is non-negotiable — model-checking the state machine does not make the LLM obey it.

---

## How it compares

| Approach | Multi-step ordering | Provable invariants | Single source of truth |
|---|---|---|---|
| Plain system prompt | implicit, unchecked | no | no (prompt/code/tests drift) |
| ReAct / free tool loop | model decides ad hoc | no | no |
| Guardrails / structured output | validates *outputs*, not the *process* | partial | partial |
| Code state-machine graph (e.g. LangGraph) | explicit, in code | not model-checked | code is truth; prompt separate |
| **XML + FizzBee contract (this pattern)** | explicit *and* model-checked | **yes** | **yes — one artifact for LLM, checker, devs** |

---

## Takeaways

- A multi-step agent is a state machine whether you write it down or not. Writing it down *formally* lets you prove things a prose prompt can only assert.
- Make one artifact serve the LLM, the model checker, and the developer.
- Treat the LLM as an autonomous agent that makes *promises*, not one that takes *commands*. The contract is the promise; the enforcement code is the assessment; the model check proves the promise is coherent. **Never ship the contract without the assessment layer.**
- Formalize structure and ordering; leave judgment and phrasing to prose.

## Further reading

- **[The Promise-Driven Agent](why-promise-driven-agents.md)** — the full whitepaper (this article is its short on-ramp).
- **[Promise Theory architecture analysis](promise-theory-architecture.md)** — the clinic system re-analyzed agent-by-agent through Promise Theory.
- [FizzBee](https://fizzbee.io) — the specification language and model checker.
- [Mark Burgess, *Promise Theory: Principles and Applications*](http://markburgess.org/promises.html) and *Thinking in Promises* (O'Reilly).
- In this kit: [`examples/clinic-appointments/`](../examples/clinic-appointments/), [`examples/holy-grail-trials/`](../examples/holy-grail-trials/), [`schema/`](../schema/).
