# Clinic Case Study Artifact Index

This index maps each case-study responsibility to the actual Clinic Appointments
artifact. Paths point into the runnable example.

## Contracts and manifests

| Artifact | Responsibility | Key identities |
| --- | --- | --- |
| [`agent_clinic_orchestrator.xml`](../../../examples/clinic-appointments/agent_contracts/agent_clinic_orchestrator.xml) | Verify identity, classify intent, route to subagents, manage one suspended workflow | `PatientVerifiedBeforeWorkflow`, `RuleOfOne`, `patient_verified`, `book_appointment`, `cancel_appointment`, `reschedule_appointment` |
| [`agent_book_appointment.xml`](../../../examples/clinic-appointments/agent_contracts/agent_book_appointment.xml) | Resolve provider, check eligibility, select and confirm a slot, attempt booking, offer alternates | `EligibilityBeforeBooking`, `CoveredOrSelfPay`, `NoDoubleBook`, `ConfirmBeforeBooking`, `slot_available`, `booking_confirmed` |
| [`agent_manage_appointment.xml`](../../../examples/clinic-appointments/agent_contracts/agent_manage_appointment.xml) | Resolve, cancel, or reschedule an owned appointment after confirmation | `CancelRequiresOwnership`, `ChangeRequiresConfirmation`, `RescheduleNoDoubleBook`, `owns_appointment`, `change_confirmed` |
| [`manifest_patient_registry.xml`](../../../examples/clinic-appointments/agent_contracts/manifest_patient_registry.xml) | Publish verified identity and active session state | `patient_identity`, `active_patient`, `record_isolation` |
| [`manifest_insurance_eligibility.xml`](../../../examples/clinic-appointments/agent_contracts/manifest_insurance_eligibility.xml) | Publish an honestly limited point-in-time coverage verdict | `eligibility_check`, `non_authoritative` |
| [`manifest_provider_schedule.xml`](../../../examples/clinic-appointments/agent_contracts/manifest_provider_schedule.xml) | Publish schedule reads and writes and own calendar consistency | `open_slots`, `commit_booking`, `cancel_slot`, `appointment_record`, `no_double_book` |

## Contract machinery

| Artifact | Responsibility |
| --- | --- |
| [`contract_doc.py`](../../../examples/clinic-appointments/src/clinic/contracts/contract_doc.py) | Locate and load LLM contracts, preserve full XML, extract FizzBee text |
| [`fizz_check.py`](../../../examples/clinic-appointments/src/clinic/contracts/fizz_check.py) | Write an extracted model to a temporary file and invoke `fizz` |
| [`promises.py`](../../../examples/clinic-appointments/src/clinic/contracts/promises.py) | Parse agents, offers, uses, conditions, and quenching tokens from both document families |
| [`verify_fizzbee_contracts.py`](../../../examples/clinic-appointments/scripts/verify_fizzbee_contracts.py) | Model-check all `agent_*.xml` documents and fail the gate on any error |
| [`verify_promise_graph.py`](../../../examples/clinic-appointments/scripts/verify_promise_graph.py) | Check offer/use binding and condition quenching across all six local agents |

## Runtime construction

| Artifact | Responsibility |
| --- | --- |
| [`agents/build.py`](../../../examples/clinic-appointments/src/clinic/agents/build.py) | Resolve contract descriptions and tools, construct ADK agents, attach booking and management subagents |
| [`tools.py`](../../../examples/clinic-appointments/src/clinic/tools.py) | Expose thin JSON-returning tool functions over deterministic services |
| [`env.py`](../../../examples/clinic-appointments/src/clinic/env.py) | Resolve and validate Google Vertex runtime configuration |
| [`__main__.py`](../../../examples/clinic-appointments/src/clinic/__main__.py) | Construct the ADK runner and provide chat, one-shot, smoke, and recorded-demo entry points |

## Deterministic services

| Artifact | Responsibility | Authoritative decisions |
| --- | --- | --- |
| [`store.py`](../../../examples/clinic-appointments/src/clinic/services/store.py) | Seeded in-memory patients, providers, slots, appointments, and active session identity | Current record and slot state for this teaching process |
| [`registry.py`](../../../examples/clinic-appointments/src/clinic/services/registry.py) | Match enrolled identity and publish active patient | Whether a supplied identity matches; which patient is active |
| [`eligibility.py`](../../../examples/clinic-appointments/src/clinic/services/eligibility.py) | Produce point-in-time plan coverage and self-pay estimate | Coverage according to the seeded plan table |
| [`schedule.py`](../../../examples/clinic-appointments/src/clinic/services/schedule.py) | List and mutate appointments and slots | Slot status, appointment ownership, sequential commit/refuse decision |
| [`refusals.py`](../../../examples/clinic-appointments/src/clinic/services/refusals.py) | Standardize success and refusal dictionaries | `ok`, refusal code, unmet condition, message |
| [`services/__init__.py`](../../../examples/clinic-appointments/src/clinic/services/__init__.py) | Construct the shared service objects and reset the test world | One module-level teaching runtime |

## Tests and gates

| Artifact | Responsibility |
| --- | --- |
| [`test_contracts_validate.py`](../../../examples/clinic-appointments/tests/test_contracts_validate.py) | Validate all contracts and manifests against their XSDs |
| [`test_gate.py`](../../../examples/clinic-appointments/tests/test_gate.py) | Run each embedded FizzBee model under pytest when `fizz` is available |
| [`test_enforcement.py`](../../../examples/clinic-appointments/tests/test_enforcement.py) | Exercise booking, management, isolation, and eligibility service paths without ADK or an LLM |
| [`Makefile`](../../../examples/clinic-appointments/Makefile) | Compose pytest, model checking, and graph verification into `make gate` |

## Primary booking trace

| Stage | Artifact location |
| --- | --- |
| Model action and invariants | `agent_book_appointment.xml`, lines 33-97 |
| Conditional offer and dependencies | `agent_book_appointment.xml`, lines 113-161 |
| LLM runtime guidance | `agent_book_appointment.xml`, lines 164-199 |
| Enforcement declarations | `agent_book_appointment.xml`, lines 201-206 |
| Tool binding | `tools.py`, lines 68-93 |
| Authoritative schedule decision | `schedule.py`, lines 53-100 |
| Double-book test | `test_enforcement.py`, lines 31-43 |
| Eligibility test | `test_enforcement.py`, lines 46-53 |
| Confirmation test | `test_enforcement.py`, lines 56-63 |

Return to the [Clinic end-to-end case study](README.md).
