# Contracts, Not Prompts: Model-Checked XML + FizzBee Instructions for LLM Agents

> _Reproduced from the Penny reference implementation. File paths and code references below point into Penny's source tree, which is not part of this kit._


*Concepts and implementation by Jeremy Schulman*
<br/>*Article is AI generated*.

*A pattern for instructing stateful LLM agents, with a worked example from "Penny," an SAP Concur expense agent. Audience: engineers deciding how to instruct and constrain agents. No formal-methods background assumed. ~18 minute read.*

---

## TL;DR — the wager

Most LLM agents are instructed with a prose system prompt: *"You are a helpful expense assistant. Always authenticate the user before creating anything…"* Prose is easy to write and impossible to verify. For a one-shot Q&A bot that's fine. For a **stateful, multi-step, safety-sensitive agent**, it leaves a question you cannot answer: *can this agent ever reach a bad state — like creating an expense report before the user is authenticated?*

The pattern in this article answers that question with a flat "no, provably." The agent's instructions **are** a formal state machine — written in [FizzBee](https://fizzbee.io), wrapped in XML, and **model-checked offline before deployment**. The same artifact is read by three consumers: the **LLM** (as operating instructions), a **model checker** (which proves invariants hold across every reachable state), and the **developer** (as the single source of truth that the enforcement code and tests trace back to).

The verdict, up front so you can decide whether to keep reading: **worth it for stateful, multi-step, safety-sensitive agents; overkill for one-shot or single-tool assistants.**

---

## Why prose prompts break down

A system prompt is a *description of intent*. An LLM is a *stochastic executor*. The gap between the two is where production incidents live.

Consider the real requirements Penny had to satisfy:

- No workflow (create a report, add an expense) may run until the user's Concur account is connected.
- When an executive assistant is acting on behalf of an executive, the "active traveler" must be resolved **before** any workflow starts, or the EA will file expenses under the wrong person.
- If the user pivots mid-task ("actually, first do X"), the agent may suspend the current task — but only **one** task may be suspended at a time, or the conversation state becomes unrecoverable.

You *can* write those as prose bullet points. But three problems follow:

1. **No coverage guarantee.** Prose describes the happy path and a few edge cases the author thought of. It says nothing about the states the author *didn't* think of. Can the agent end up with two suspended tasks? With a prose prompt, the honest answer is "probably not, but I can't prove it."
2. **No single source of truth.** The prompt says one thing, the tool-wrapper code enforces another, the tests assume a third. They drift.
3. **No verification loop.** You change the prompt, ship it, and find out in production whether you introduced a contradiction.

The insight is that a multi-step agent is a **state machine** whether you acknowledge it or not. Prose leaves that machine implicit and unchecked. This pattern makes it explicit and checks it.

---

## What the approach actually is

Each Penny agent's *entire* instruction set is an XML document with four sections, each with a distinct job:

```
<agent-instructions>
  <objective>       — what this agent is for (natural language)
  <contract>        — the FizzBee state machine: state, actions, guards, invariants
  <step-guidance>   — per-action prose: LLM judgment, tool bindings, phrasing
  <enforcement>     — invariants the server enforces in code, independent of the LLM
  <responses>       — message templates for key replies
</agent-instructions>
```

The center of gravity is `<contract>`. Here is the authentication rule from Penny's orchestrator, verbatim:

```
atomic action EnsureAuth:
    require not concur_authenticated
    require active_workflow == NO_WORKFLOW
    concur_authenticated = oneof [True, False]

always assertion AuthBeforeWorkflow:
    return active_workflow == NO_WORKFLOW or concur_authenticated
```

Read it in plain English:

- **`action`** is something the agent can do. **`require`** clauses are *guards* — preconditions that must hold for the action to be legal. `EnsureAuth` may only run when the user is not yet authenticated and no workflow is active.
- **`oneof [True, False]`** models a nondeterministic outcome: the login attempt might succeed or fail. (More on this reinterpretation below.)
- **`always assertion`** is an **invariant** — a property that must be true in *every* reachable state. `AuthBeforeWorkflow` says: either no workflow is active, or the user is authenticated. There is no legal state where a workflow runs without auth.

FizzBee is a specification language in the lineage of TLA+ and PlusCal — the tools engineers use to design distributed protocols — but with Python-like syntax that reads approachably. You don't need to know that lineage to read the snippet above; that's the point.

### Model-checking: proving the invariants

Here's the part prose can't do. A **model checker** (`fizz`) explores *every reachable combination of state variables* the actions can produce, and checks that no invariant is ever violated. Penny runs this offline in CI (`scripts/verify_fizzbee_contracts.py`) across all three contracts:

```
[PASS] orchestrator
[PASS] create_expense_report
[PASS] add_expense
3/3 contract(s) passed model checking.
```

If someone adds an action that could set `active_workflow` while `concur_authenticated` is false, the checker finds the exact sequence of steps that reaches the bad state and fails the build. The "can it ever…?" question is answered by exhaustive search, at design time, before an LLM or a user is anywhere near it.

The orchestrator's other proven invariants are just as concrete:

```
# Rule of one: never two suspended tasks.
always assertion RuleOfOne:
    return (not pending_pivot) or (suspended_workflow == NO_WORKFLOW)

# EA-delegate: no workflow starts before the traveler is resolved.
always assertion TravelerBeforeWorkflow:
    return (active_workflow == NO_WORKFLOW) or (scenario == STANDARD) or traveler_resolved
```

### The crucial reinterpretation: `runtime-instructions` mode

There's a subtlety that makes this work as *instructions* and not just a spec. In classic model checking, `oneof [A, B]` means "explore **both** branches" — the checker tries everything. But when the same document is handed to the LLM as instructions, `oneof` means "**you, the agent, select exactly one** path at runtime based on the conversation."

Penny's contract declares this explicitly: `<fizzbee mode="runtime-instructions">`. One artifact, two readings:

- **Model checker's reading:** explore all branches → prove no branch violates an invariant.
- **LLM's reading:** choose one branch → the invariants describe the box you must stay inside.

That dual reading is the whole trick. The checker proves the *space of allowed behavior* is safe; the LLM navigates within it.

### The other three sections

The contract is deliberately not the whole story:

- **`<step-guidance>`** is where fuzzy judgment lives — how to classify intent, which tool to call, how to phrase a handoff. This is prose, because "is this message a greeting or a request?" is not a formal property.
- **`<enforcement>`** restates the invariants as rules the *server code* enforces, independent of the model. Every FizzBee invariant has a code twin and a pytest test.
- **`<responses>`** are message templates so critical replies (the auth link, the "which report?" prompt) are consistent.

The division of labor matters: **the formal part constrains structure (state transitions, ordering, invariants); the prose part guides judgment (classification, wording).** Don't try to formalize the fuzzy parts — you'll fail — and don't leave the structural parts to prose — you'll drift.

---

## Architecture: an orchestrator and its subagents

The contract pattern shapes the system architecture, so it's worth seeing how Penny is put together.

Penny is a single agent exposed to Gemini Enterprise, but internally it's an **orchestrator** plus **workflow subagents**:

- **`penny_orchestrator`** is the sole entry point. It owns every turn: authenticate, resolve the active traveler (the EA-delegate case), classify intent, and route. It also handles *cross-cutting, read-only* operations directly — listing reports, switching the active traveler — because those don't need a multi-turn workflow.
- **`penny_create_expense_report`** and **`penny_add_expense`** are subagents, each owning exactly one multi-step workflow, each with its **own** XML+FizzBee contract (e.g., `add_expense` proves `CreateRequiresReadableReceipt`, `CreateRequiresSupportedType`).

Why this split, and the tradeoffs we accepted:

- **Cross-cutting state belongs to the orchestrator, not a subagent.** The "active traveler" is shared state *every* workflow consumes. We deliberately did **not** make traveler management its own subagent; it's an orchestrator-owned capability. A subagent that owned shared state would force every other subagent to negotiate with it.
- **One workflow per subagent keeps each contract small enough to model-check and reason about.** The orchestrator's contract is about *routing and safety*; a subagent's contract is about *one job done correctly*. Neither has to understand the other's internals.
- **Read-only vs. stateful is an explicit design axis.** "List my open reports" is a single tool call with no workflow state — the orchestrator handles it inline (`ListReports` changes no `active_workflow`). "Create a report" is a multi-turn commitment — it gets a subagent. Encoding that distinction in the state machine keeps the pivot logic honest.
- **We collapsed the state space when the product allowed it.** An early design let a user attach a receipt to an existing line *or* create a new line. A rule change — "a submitted receipt always creates an expense, if and only if the photo is readable" — removed an entire branch from the `add_expense` contract. Fewer states, fewer invariants, less to prove, less to break.
- **We consolidated two A2A agents into one.** A separate "receipt intake" agent was folded into the orchestrator. Every entry point is a contract you must maintain; one is cheaper than two.

The orchestrator/subagent boundary is also a **hand-off boundary**, which turns out to be exactly what the next section is about.

---

## The Promise Theory lens

[Promise Theory](http://markburgess.org/promises.html), developed by Mark Burgess, is a way of reasoning about systems built from autonomous parts. Three ideas carry the weight here, and none require a math background:

1. **Agents are autonomous.** An agent controls only its own behavior. No agent can make a promise *on behalf of* another.
2. **You cannot impose behavior — you can only obtain a promise.** Commanding an autonomous agent to do something doesn't make it happen; the agent must voluntarily promise, and then you *assess* whether it kept the promise.
3. **Cooperation is composed from promises.** System behavior emerges from many small promises fitting together, plus the assessments that keep them honest.

This is not a metaphor for LLM agents — it is a startlingly literal description of them. **An LLM is an autonomous, stochastic agent. You genuinely cannot impose behavior on it.** No prompt *guarantees* an action; it can only elicit a promise to behave a certain way. Once you accept that, the whole design falls out:

- **The contract is the agent's published promise.** `AuthBeforeWorkflow` is Penny promising: *"I will not run a workflow unless you're authenticated."* Written formally so both humans and the model can read it, and model-checked so the promise is at least *self-consistent* — the agent isn't promising something impossible.
- **The enforcement code and tests are the assessment.** Because the promiser is stochastic and may break its promise on any given turn, the promisee must *verify*. Penny's server re-checks every invariant in code before invoking a subagent. This is why the code layer is **mandatory, not belt-and-suspenders**: Promise Theory tells you that a promise from an unreliable agent is worthless without independent assessment.
- **Subagents are autonomous.** The orchestrator does not reach inside a subagent and drive its steps. It makes a **(+) promise to provide** context (the active traveler, the target report) and the subagent makes a **(−) promise to use** it and to return a result. The hand-off is voluntary cooperation between autonomous parts — not a function call that dictates internal behavior.
- **The system is a composition of promises.** Orchestrator promises (auth-first, rule-of-one) compose with subagent promises (readable-receipt-required) into the guarantees the whole system offers.

The practical punchline: teams that treat prompts as *commands* are surprised when the LLM "disobeys." Teams that treat prompts as *promises requiring assessment* build the verification layer from day one. This pattern bakes that stance into the architecture — the contract is the promise, the code is the assessment, and the model checker proves the promise is coherent before anyone relies on it.

---

## Why it's good

- **Precision where it counts.** Ordering and safety constraints ("auth before write," "resolve traveler before routing," "one suspended task") are stated exactly, not implied.
- **Provable invariants before deploy.** The model checker answers "can it ever reach a bad state?" by exhaustive search. That is a categorically stronger guarantee than reading a prompt and hoping.
- **Defense in depth, from one source.** The FizzBee invariant, the enforcement code, and the pytest test all trace to the same statement. When they agree, you have three independent reasons to trust the behavior; when they disagree, a test fails.
- **Safe evolution.** Adding `INTENT_SELECT_REPORT` meant adding one action and one guard to the state machine, updating the matching prose and code, and re-running the checker — which confirmed the new action couldn't violate an existing invariant. Change is a mechanical, checkable process, not a prompt-tweak-and-pray.
- **Readable by everyone involved.** The same document onboards a new engineer, instructs the model, and feeds the verifier. There is no separate design doc to fall out of date.

---

## Where it costs you (and when not to use it)

Honesty is the point of a "good *or* bad" evaluation. The costs are real:

- **Authoring and maintenance overhead.** A formal contract is more work than a paragraph. It pays off only when the flow is genuinely stateful and the cost of a wrong state is high.
- **Token cost per turn.** The contract rides in the context window on every request. For a large contract that's non-trivial spend.
- **The model check proves the *spec*, not the *behavior*.** This is the biggest caveat and the easiest to get wrong. Model-checking proves the *state machine* is sound — that no legal sequence of actions violates an invariant. It does **not** prove the LLM follows the state machine. The LLM can still mis-classify intent or skip a step. **That is exactly why the enforcement code is non-negotiable.** If you ship the contract as a prompt and skip the code layer, you've bought false confidence.
- **The fuzzy parts stay fuzzy.** Intent classification, tone, and judgment live in prose and remain as reliable as any prompt. Formalism doesn't rescue them; it just quarantines them so they can't corrupt the structural guarantees.
- **Skill and tooling.** Your team needs to read a state machine, run a model checker in CI, and maintain spec/code/test parity. That's a real, if learnable, investment.

**When to reach for it:** multi-step workflows, ordering or safety constraints that must hold, money or identity or irreversible actions in play, multiple interacting sub-flows, and a need to evolve the agent without regressions. Penny — which authenticates, acts on behalf of others, and writes to a financial system of record — is squarely in this zone.

**When to skip it:** one-shot Q&A, a single-tool "look this up" assistant, a prototype, or anything where a wrong turn is cheap to undo. There, a good prose prompt is the right tool, and a formal contract is ceremony.

---

## How it compares to common approaches

| Approach | Multi-step ordering | Provable invariants | Single source of truth | Best for |
|---|---|---|---|---|
| **Plain system prompt (prose)** | Implicit, unchecked | No | No (prompt/code/tests drift) | One-shot / simple assistants |
| **Few-shot / example-driven** | Taught by example; brittle | No | No | Narrow, well-bounded tasks |
| **ReAct / free tool-calling loop** | Model decides ad hoc | No | No | Exploratory, low-stakes tool use |
| **Guardrails / structured-output validators** | Validates *outputs*, not the *process* | Partial (output shape) | Partial | Enforcing response format |
| **Code state-machine graph (e.g. LangGraph)** | Explicit, in code | Not model-checked | The code is the truth (LLM prompt separate) | Deterministic orchestration |
| **Deterministic workflow engine (LLM as leaf)** | Fully explicit | Via code, not the model | Yes, but rigid | Low-flexibility pipelines |
| **XML + FizzBee contract (this pattern)** | Explicit *and* model-checked | **Yes** | **Yes — one artifact for LLM, checker, devs** | Stateful, safety-sensitive agents |

A few honest distinctions:

- **Versus a plain prompt:** same delivery mechanism (text in the context window), categorically more structure and a verification loop. This is the direct upgrade path.
- **Versus code state-machine graphs (LangGraph and friends):** the closest cousin, and a strong choice in its own right. The graph encodes the machine *in code*. Two differences: that graph typically isn't *model-checked* (you don't get "no reachable state violates X"), and it isn't the *LLM's instructions* — the prompt is a separate artifact that can drift from the graph. This pattern's distinctive property is **one artifact, three consumers**: the LLM's instructions, the model checker's input, and the developer's contract are literally the same document.
- **Versus guardrails/structured output:** complementary, not competing. Those validate the *shape of a response*; this governs the *sequence of steps and the invariants across them*. Penny uses both — structured output for OCR extraction, contracts for flow.
- **Versus a deterministic workflow engine:** if you can eliminate the LLM from the control flow entirely, do — it's the safest option. Penny can't; conversational routing and intent classification need the model. This pattern is the middle path: a formal machine as the *contract*, the LLM as the *executor* inside it, code as the *backstop*.

---

## Takeaways

- A multi-step agent is a state machine whether you write it down or not. Writing it down — formally — lets you *prove* things a prose prompt can only assert.
- Make the same artifact serve the LLM, the model checker, and the developer. One source of truth is the feature.
- Treat the LLM as an autonomous agent that makes *promises*, not one that takes *commands*. The contract is the promise; the enforcement code is the assessment; the model check proves the promise is coherent. **Never ship the contract without the assessment layer** — model-checking the spec does not make the LLM obey it.
- Formalize structure and ordering; leave judgment and phrasing to prose. Don't cross the streams.
- Use it when state and safety matter; skip it when they don't. It is a power tool, not a default.

Penny went from "here is a receipt photo" to a fully populated, receipt-attached Concur expense line — through authentication, delegation, intent routing, and three restricted-scope APIs — without ever being able to reach a state where it files an expense for the wrong person or before you've logged in. Not because the prompt asked nicely, but because the contract made it provably impossible, and the code made sure.

---

## Further reading

**FizzBee and model checking**

- [FizzBee](https://fizzbee.io) — the specification language and model checker used here; the docs' tutorials are the fastest way to get from "reading a contract" to "writing one."
- [Leslie Lamport, *Specifying Systems*](https://lamport.azurewebsites.net/tla/book.html) — the TLA+ book; the intellectual lineage behind FizzBee. Free PDF; skim Part I for the mental model of states, actions, and invariants.
- [Hillel Wayne, *Learn TLA+*](https://learntla.com) — a gentler, example-driven on-ramp to the same ideas if the Lamport book is too dense.
- [Practical TLA+ (Hillel Wayne)](https://www.hillelwayne.com/post/business-case-formal-methods/) — "the business case for formal methods," useful for justifying the investment to a team.

**Promise Theory**

- [Mark Burgess, *Promise Theory: Principles and Applications*](http://markburgess.org/promises.html) — the primary source; start with the introductory essays before the book.
- [Mark Burgess, "Promises 101"](http://markburgess.org/treatise.html) — a short, readable introduction to autonomy, impositions vs. promises, and (+/−) promises.

**LLM agents and instruction patterns (for the comparison)**

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — the free tool-calling loop discussed in the comparison.
- [LangGraph](https://langchain-ai.github.io/langgraph/) — the code state-machine-graph approach; the closest cousin to this pattern.
- [Guardrails AI](https://www.guardrailsai.com/docs) — output-validation guardrails, complementary to flow contracts.
- [Anthropic, "Building effective agents"](https://www.anthropic.com/engineering/building-effective-agents) — a practical taxonomy of agent patterns (prompt chaining, routing, orchestrator-workers) that maps cleanly onto Penny's orchestrator/subagent split.

**In this repository**

- `agent_contracts/agent_orchestrator.xml` — the full orchestrator contract quoted throughout.
- `agent_contracts/agent_add_expense.xml`, `agent_contracts/agent_create_expense_report.xml` — the subagent contracts.
- `scripts/verify_fizzbee_contracts.py` — the CI step that model-checks all three.
