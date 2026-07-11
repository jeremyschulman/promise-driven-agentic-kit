# A Contract-Driven Agent as a System of Promising Agents

**An architecture analysis of this kit's clinic-appointment example (and the Trials of the Holy Grail) through Promise Theory.**

*Grounded in the runnable examples in this kit ([`examples/clinic-appointments/`](../examples/clinic-appointments/), [`examples/holy-grail-trials/`](../examples/holy-grail-trials/)) and in Bergstra & Burgess, "Promise Theory: Principles and Applications" (2nd ed.).*

---

## 1. The agents

The clinic agent is a multi-agent system. Its agents, as they exist in the example:

| # | Agent | Kind | Lives in |
|---|-------|------|----------|
| 1 | **`clinic_orchestrator`** | LLM (root) | `agent_contracts/agent_clinic_orchestrator.xml` |
| 2 | **`book_appointment`** | LLM (subagent) | `agent_contracts/agent_book_appointment.xml` |
| 3 | **`manage_appointment`** | LLM (subagent) | `agent_contracts/agent_manage_appointment.xml` |
| 4 | **`provider_schedule`** | service (non-LLM) | `manifest_provider_schedule.xml` + `src/clinic/services/schedule.py` |
| 5 | **`insurance_eligibility`** | service (non-LLM) | `manifest_insurance_eligibility.xml` + `services/eligibility.py` |
| 6 | **`patient_registry`** | state (non-LLM) | `manifest_patient_registry.xml` + `services/registry.py` |

Each publishes a **promise manifest** (the `<promises>` block) and — for the LLM agents — a model-checked FizzBee `<verifiable-behavior>` section. The non-LLM agents have no state machine (they are deterministic) but are full participants in the promise graph.

## 2. Ground rules from Promise Theory

From Bergstra & Burgess, the tenets this analysis uses:

- **Autonomy** — "Agents are autonomous. They can only make promises about their own behaviour. No other agent can impose a promise upon them." (ch. 1.3–1.4)
- **Polarity** — `A ──(+b)──▶ B` ("I offer *b*") and `A ──(−b)──▶ B` ("I accept/use *b*"). Cooperation *binds* only when a `+b` meets a matching `−b` (§3.11).
- **Imposition** — an attempt to induce behavior without an invited promise to accept (a command, a hint). Autonomous agents cannot be commanded, only promised to.
- **Conditional promise** `b|c` — "*b* given *c*" (§3.4). Combined with a promise to *acquire* `c` from a third party, it reduces to an **assisted promise** (Def. 31, Law 4). Satisfying a condition is **quenching** it.
- **Assessment** — "a decision about whether a promise has been kept… Every agent makes its own." Promises are intent; keeping them is never guaranteed (§2.13).
- **Superagents** — a cluster that makes collective promises outward is itself an agent; "we may choose the boundary of an agent wherever we please" (fig. 4.4).

An LLM is *literally* an autonomous, stochastic agent — so these are engineering facts about the system, not metaphors.

## 3. The agents restated as promisers

Notation: `π: Agent ──±body──▶ promisee`.

#### `book_appointment` (the richest case)

| Pol. | Promise body | Promisee |
|------|-------------|----------|
| + | `book_appointment ⟶ {appointment}` \| `patient_verified ∧ eligibility_checked ∧ slot_available ∧ booking_confirmed` | orchestrator, patient |
| + | `offer_alternate_slot` when the chosen slot is taken — never silently rebook (fallback promise) | patient |
| + | `never_double_book` (invariant, kept in `provider_schedule` code) | patient, compliance |
| − | `active_patient` from `patient_registry` (quenches `patient_verified`) | patient_registry |
| − | `eligibility_check` from `insurance_eligibility` (quenches `eligibility_checked`) | insurance_eligibility |
| − | `open_slots` / `commit_booking` from `provider_schedule` (quenches `slot_available`) | provider_schedule |
| − | `confirmation` from the patient (quenches `booking_confirmed`) | patient |

The conditions in the first promise are exactly the FizzBee guards on `CreateBooking`. The contract *is* the conditional-promise body; the manifest publishes it so the promisees can rely on and assess it.

#### `clinic_orchestrator`

Under the autonomy tenet, the orchestrator **cannot** promise that a subagent will book anything — only its own behavior: verify identity, classify intent, relay to the matching offer, remember at most one suspended workflow, relay results verbatim. Routing is **selection among published offers** (`−use` of a subagent's conditional `+offer`), never a command. The user-facing "the clinic will book your appointment" is an **assisted promise** kept through the subagents' own conditional offers.

#### The services and state

- `patient_registry` **promotes shared state to an agent**: it publishes `+active_patient` (with the verified identity) and `+patient_identity`, and keeps `record_isolation`. Consumers declare `−use`, so a dependency that would otherwise be a hidden blackboard read becomes a *declared, checkable binding*.
- `insurance_eligibility` is an **honest promiser**: its promise body states the verdict is *point-in-time, not a guarantee of payment*, so `book_appointment` conditions its use on an explicit patient decision.
- `provider_schedule` keeps `NoDoubleBook` **in code** — the assessment behind the LLM's promise.

## 4. Conditional promises and quenching

Every FizzBee `require` maps to a condition; the dependency chain becomes a chain of conditions each agent quenches via a `−` promise to a third party (Law 4):

```
book ── +book_appointment | patient_verified ∧ eligibility_checked
                            ∧ slot_available ∧ booking_confirmed ──▶ orchestrator/patient
book ── −active_patient      ──▶ patient_registry       (quenches patient_verified)
book ── −eligibility_check   ──▶ insurance_eligibility  (quenches eligibility_checked)
book ── −open_slots          ──▶ provider_schedule      (quenches slot_available)
book ── −confirmation        ──▶ patient               (quenches booking_confirmed)
```

Because `book_appointment` promises both `book | slot_available` *and* `−open_slots`, the pair reduces to the assisted promise the patient actually experiences — while the graph preserves *who* quenches each prerequisite. What the theory adds over the guards alone: the guards say *when* the agent may act; the conditional promises say *who it relies on for each condition, and that the reliance is agreed*. An unquenched condition is a detectable defect — `scripts/verify_promise_graph.py` fails on it.

## 5. The promise graph vs. a naive call graph

Pairing every `−` with a `+` yields a bidirectional, typed graph, verified offline for:

1. **Binding completeness** — every `−use` meets a `+offer`. An agent consuming something no one promised is a build failure, not a runtime surprise.
2. **Condition quenching** — every `|c` is quenched by some offer or explicitly self-assessed.
3. **No ownership edges** — the orchestrator holds `−use` of the subagents' conditional offers; the subagents' own guards are the real gate, and the graph says so.
4. **Local failure semantics** — a subagent failing to keep its offer is assessed *independently* by the orchestrator (which promised only to relay) and by the user. No promise *obliges* anyone to compensate.

## 6. Assessment and trust

Promises are intent; keeping them is never guaranteed. The system assesses constantly:

- **Structured refusals** — services return `{"ok": false, "unmet": …}` (never raise across the boundary): non-cooperation as a first-class, testable outcome.
- **The eligibility verdict** — `book_appointment`'s assessment of coverage before it relies on it; the service's honest "point-in-time" caveat calibrates that assessment.
- **The enforcement twins + tests** — `provider_schedule`'s refusal of a taken slot, the ownership check in `manage_appointment`, the confirm gate: repeated code-level assessments of the stochastic promiser.
- **Model checking as *pre-assessment*** — `fizz` proves an agent's promise set is *coherent* before it is ever offered. In the Trials of the Holy Grail example, this caught a real defect: the Quest Marshal's first draft let a passed trial be un-passed, which would have let the Grail be granted without both trials. The checker produced the counterexample trace; the fix was mechanical. That is pre-assessment doing its job.

What a production system adds next is an **assessment ledger**: promise-specific,
append-only records from named assessors. Trust can then *modulate reliance* (for
example, tighter confirmations for a flaky dependency), never *create obligation*.
The [Runtime Assessment and Evidence](runtime-assessment/README.md) guide defines a
general record and the distinction between operational outcome and promise status.

## 7. Superagents

- **The two-member superagent.** `(book_appointment LLM + provider_schedule code)` is itself a superagent: the LLM half promises `NoDoubleBook`; the code half keeps it by refusing a taken slot. Their conjunction is what makes the promise keepable against a stochastic executor. **This is the atomic unit of the methodology** — never a stochastic promise alone, always paired with a deterministic assessment.
- **The external card.** The Trials of the Holy Grail example adds the outward face: `manifest_grail_superagent.xml` publishes `card`-typed offers whose `entailed-by` attribute names the interior offers that justify them, and the promise-graph verifier fails if any referenced offer doesn't exist. **No capability is advertised unless a member actually offers it** — the single-source-of-truth discipline applied one level up.

## 8. Framework independence

None of the above depends on the agent framework. The promise graph, the conditional promises, the assessment layer — all live in the contracts and the pure-Python `services/`. This kit demonstrates it directly: the clinic runs on **Google ADK**, the Trials of the Holy Grail on **Pydantic AI**, and the *only* meaningful difference is each example's `agents/build.py`. The promise-theoretic architecture is identical.

---

## Closing

The deepest finding: a contract-driven agent's *intra-agent* discipline is Promise Theory in disguise — each contract is a model-checked, code-enforced declaration about an agent's own behavior, with structured refusal as the non-cooperation path. The *inter-agent* half completes it: declared acceptances, conditions that name their quenchers, an external promise *derived from* rather than *asserted alongside* its members. The wager of [contracts-not-prompts](contracts-not-prompts.md) — *can this agent reach a bad state?* — extends to the system: *can this system of agents make a promise it has no way to keep?* Both are answered, before deployment, by exhaustive offline checking, on the same artifacts the model reads at runtime. See [the whitepaper](why-promise-driven-agents.md) for the full argument.
