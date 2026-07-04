# Clinic Appointments — a live, contract-driven agent

The worked example for the [promise-driven-agentic-kit](../../README.md): a
**runnable** multi-agent clinic assistant built on Google's ADK, where every
safety guarantee is a model-checked contract *and* a code-enforced twin.

It books, reschedules, cancels, and lists clinic appointments, and answers
insurance-eligibility questions — and it is **provably unable** to book before
the patient is verified, to double-book a slot, to book without confirmation, or
to touch an appointment the patient doesn't own.

> This example is deliberately richer than the kit's `skeleton/` toy (one agent):
> it has six agents, so it shows the part of Promise Theory that matters most —
> **composition**. It is still small enough to read in a sitting.

## The promise graph

```mermaid
flowchart TB
    patient["patient (human)"]
    subgraph CLINIC["clinic superagent"]
        orch["clinic_orchestrator<br/>verify identity · classify · route"]
        book["book_appointment<br/>eligibility · slot · confirm · commit"]
        manage["manage_appointment<br/>cancel · reschedule"]
        reg["patient_registry<br/>identity · active patient"]
        sched["provider_schedule<br/>slots · bookings (enforces NoDoubleBook)"]
        elig["insurance_eligibility<br/>coverage verdict"]
    end
    patient -->|"requests"| orch
    orch -->|"−patient_identity"| reg
    orch -->|"−book_appointment"| book
    orch -->|"−cancel / −reschedule"| manage
    book -->|"−active_patient"| reg
    book -->|"−eligibility_check"| elig
    book -->|"−open_slots / −commit_booking"| sched
    manage -->|"−appointment_record / −open_slots"| sched
    manage -->|"−active_patient"| reg
    elig -->|"−active_patient"| reg
    sched -->|"−active_patient"| reg
```

Every edge is a declared `−use` bound to a matching `+offer`; the whole graph is
verified offline (`scripts/verify_promise_graph.py`).

## The agents and their guarantees

| Agent | Kind | Flagship invariant(s) — *proven by `fizz`, enforced in `services/`* |
| --- | --- | --- |
| `clinic_orchestrator` | LLM (root) | **PatientVerifiedBeforeWorkflow**, RuleOfOne |
| `book_appointment` | LLM subagent | **EligibilityBeforeBooking**, **NoDoubleBook**, ConfirmBeforeBooking |
| `manage_appointment` | LLM subagent | **CancelRequiresOwnership**, RescheduleNoDoubleBook |
| `provider_schedule` | service | keeps **NoDoubleBook** in code — refuses a taken slot |
| `insurance_eligibility` | service | honest promiser: verdict is point-in-time, not a guarantee |
| `patient_registry` | state | per-patient record isolation |

**The showcase:** `NoDoubleBook` is *promised* by the LLM `book_appointment`
agent and *kept* by `provider_schedule`'s code, which refuses to commit a taken
slot no matter what the model does. That LLM-promise + code-assessment pair is
the whole methodology in one place (see the kit's
[whitepaper](../../docs/why-promise-driven-agents.md)).

## Run it

Two layers — the **offline gate needs no credentials**, the **live agent needs
Vertex** (see [GETTING-STARTED.md](GETTING-STARTED.md)).

```bash
uv sync

# offline — no Google credentials required:
make gate            # schema + fizz model-check + promise-graph + enforcement tests

# live — needs a Google service-account JSON (see GETTING-STARTED.md):
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
uv run python -m clinic smoke     # scripted verify -> list -> book demo
uv run python -m clinic chat      # interactive (Rich: Markdown replies + a "thinking" spinner)
```

`adk web` also works — point it at `src/clinic`.

## Layout

| Path | What it is |
| --- | --- |
| `agent_contracts/` | 3 `agent_*.xml` (LLM) + 3 `manifest_*.xml` (services/state) |
| `schema/` | the kit's XSDs (vendored) |
| `src/clinic/contracts/` | contract loader, `fizz` runner, promise-manifest reader |
| `src/clinic/services/` | **pure-Python domain + enforcement twins — no ADK, no LLM** |
| `src/clinic/tools.py` | thin ADK tool wrappers over the services |
| `src/clinic/agents/` | `build_*_agent()` — constructs ADK `LlmAgent`s from the contracts |
| `src/clinic/env.py` | Vertex bootstrap (derives project from the SA file) |
| `src/clinic/__main__.py` | the `chat` / `smoke` / `once` CLI |
| `tests/` | schema-validate + model-check + promise-graph + **enforcement-twin** tests |

The clean separation is the point: everything in `services/` (where the
invariants are *kept*) has no ADK dependency, so the entire gate runs green with
no model, no keys, and no network. The LLM is a thin, replaceable shell on top.
