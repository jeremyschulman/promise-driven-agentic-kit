# Promise-Driven Agentic Kit: Corpus Table of Contents

This is the master contents map for the promise-driven-agentic-kit corpus. It presents
the methodology as a learning and practice sequence rather than mirroring the
repository tree. Detailed inventories of examples, illustrations, schemas, and
reusable assets appear in the appendices.

The corpus contains several kinds of material:

| Kind | Purpose |
| --- | --- |
| **Chapter** | Primary narrative or practitioner guidance intended to be read |
| **Companion asset** | Illustration, code sample, exercise, or template supporting a chapter |
| **Normative reference** | Schema or controlled vocabulary defining an accepted document shape |
| **Authoring aid** | Skill, checklist, skeleton, or generated-project guidance used while building |
| **Runnable example** | Complete package demonstrating contracts, services, verification, and framework integration |
| **Draft article** | Unpublished narrative treatment intended for an external audience |

## Suggested Reading Routes

| Reader or goal | Route |
| --- | --- |
| New practitioner | Chapters 1 → 2 → 3 → 5 → 6 → 7 |
| Software engineer | Chapters 1 → 3 → 4 → 5 → 6 → 7 |
| Software architect | Chapters 2 → 3 → 4 → 6 → 7 |
| Formal-methods reviewer | Chapters 2 → 3 → 4 → 6 → 7 |
| Runtime or operations engineer | Chapters 5 → 6 → 7 |
| Engineering leader evaluating adoption | Chapters 1 → 2 → 5 → 6 → 8 |
| Article reader | Chapter 8, followed by Chapters 1 and 2 |
| Complete corpus | Chapters 1-9 in order, consulting appendices as needed |

---

# Section I: Orientation and Foundations

## Chapter 1: Enter the Methodology

Start with the problem the methodology addresses, learn how the corpus is organized,
and see how contracts connect the familiar Design → Build → Run development cycle.

**Primary reading, in order:**

- [Top-Level README](../README.md) — methodology, lifecycle, kit layout, and quick start
- [Contracts, Not Prompts](contracts-not-prompts.md) — concise conceptual introduction
- [From Contract to Enforcement](contract-assessment/README.md) — visual end-to-end orientation
- [Documentation Map](README.md) — choose the next route through the corpus

**Continue by role:**

- [Practitioner Learning Path](learning-path/README.md)
- [30-Minute Orientation](learning-path/orientation.md)
- [Role-Specific Learning Paths](learning-path/role-paths.md)

## Chapter 2: Theory, Architecture, and Vocabulary

Develop the conceptual foundation for autonomy, promises, conditions, assessment,
trust, and composition, then establish a shared vocabulary for the rest of the corpus.

**Primary reading, in order:**

- [The Promise-Driven Agent](why-promise-driven-agents.md) — full methodology whitepaper
- [Glossary and Naming Conventions](glossary/README.md) — consolidate the terminology
  and identity chains
- [A Contract-Driven Agent as a System of Promising Agents](promise-theory-architecture.md)
  — apply Promise Theory to the architecture
- [Promise Theory Interpretation and Open Questions](promise-theory-interpretation.md)
  — review the engineering mappings, applicability limits, and unresolved questions

---

# Section II: Practitioner's Guide

Follow the methodology through Design → Build → Run → Assess. The chapters in this
section move from participant boundaries and contract structure through executable
enforcement, runtime evidence, and assurance of the complete contract package.

## Chapter 3: Design Participants, Boundaries, and Contract Structure

Identify the promising parties and authoritative boundaries, choose the right document
type, and author the six-section XML contract that carries intent into implementation.

**Primary reading, in order:**

- [Choosing a Participant and Document Type](participant-types/README.md) — identify
  the promiser and select the correct document form
- [Authoring an Agent Contract](authoring-workflow/README.md) — develop the contract
  through the Design, Build, and Run workflow
- [Contract anatomy](../skills/authoring-agent-contracts/references/contract-anatomy.md) —
  inspect each XML structure in detail
- [Authoring checklist](../skills/authoring-agent-contracts/references/authoring-checklist.md)
  — confirm the completed package is coherent

**Normative references:**

- [LLM agent-contract schema](../schema/agent-contract.xsd)
- [Deterministic agent-manifest schema](../schema/agent-manifest.xsd)
- [Shared Promise Theory vocabulary](../schema/promise-common.xsd)

## Chapter 4: Design Behavior, Composition, and Change

Use formal behavior to test consequential claims, connect promises across participants,
and evolve the resulting network without silently breaking identities or evidence.

**Primary reading, in order:**

- [Composing Promises](promise-graph/README.md) — connect local promises into a system-level graph
- [Debugging a FizzBee Counterexample](counterexample-debugging/README.md) — repair
  behavior that fails its formal claim
- [Evolving an Agent Contract](contract-evolution/README.md) — change the proven and composed system safely

**Model artifacts:**

- [Unsafe FizzBee model](counterexample-debugging/unsafe-commit.fizz)
- [Repaired FizzBee model](counterexample-debugging/repaired-commit.fizz)

## Chapter 5: Build Executable Enforcement

Carry contract identities into Python assessment boundaries, enforcement twins, and a
working package. This is where an AI coding assistant consumes the XML contract to
help generate implementation and pytest evidence without becoming the authority for
the promised outcome.

**Primary reading, in order:**

- [From Contract to Enforcement](contract-assessment/README.md) — understand how
  contract identities reach Python and tests
- [Authoring Agent Contracts skill](../skills/authoring-agent-contracts/SKILL.md) —
  follow the coding assistant's implementation procedure
- [Skeleton Guide](../skeleton/README.md) — generate and explore a complete working package

**Supporting source:**

- [Rich code-rendering source](contract-assessment/render_code_snippets.py)

## Chapter 6: Run, Assess, and Assure

Observe operational outcomes, assess individual promises, review the complete evidence
chain, and carry resulting changes coherently into the next design cycle.

**Primary reading, in order:**

- [Runtime Assessment and Evidence](runtime-assessment/README.md) — assess promises and preserve operational evidence
- [Five Questions, Five Kinds of Evidence](assurance-model/README.md) — understand
  what each assurance layer can establish
- [Reviewing a Contract Package](reviewing-contract-packages/README.md) — apply
  those distinctions to a complete package review
- [Evolving an Agent Contract](contract-evolution/README.md) — feed assessment
  findings into the next Design, Build, and Run cycle

**Reusable artifact:**

- [Generic assessment-record JSON Schema](runtime-assessment/assessment-record.schema.json)

**Practice and reusable artifacts:**

- [Worked review: The Unsafe Commit Package](reviewing-contract-packages/worked-review.md)
- [Contract-package review report template](reviewing-contract-packages/review-report-template.md)

---

# Section III: Learning

## Chapter 7: Learn Through Complete Examples

Move from guided exercises to a complete architectural reconstruction, then inspect or
run two framework-specific packages that demonstrate the same methodology.

**Learning sequence:**

- [Practitioner Learning Path](learning-path/README.md)
- [30-Minute Orientation](learning-path/orientation.md)
- [90-Minute Guided Workshop](learning-path/workshop.md)
- [Role-Specific Learning Paths](learning-path/role-paths.md)
- [Knowledge Check and Answer Key](learning-path/knowledge-check.md)

**End-to-end case study:**

- [Case Studies Index](case-studies/README.md)
- [Clinic Appointments: An End-to-End Case Study](case-studies/clinic-appointments/README.md)
- [Clinic file-level artifact index](case-studies/clinic-appointments/artifact-index.md)

**Runnable packages:**

- [Clinic Appointments — Google ADK](../examples/clinic-appointments/)
- [Trials of the Holy Grail — Pydantic AI](../examples/holy-grail-trials/)

---

# Section IV: Essays and Reference

## Chapter 8: Essays and Long-Form Treatments

Read the methodology as an external-facing narrative, then use the whitepaper and
architecture analysis as deeper companions.

**Draft article series:**

- [Medium Article Series](medium-articles/README.md)
- [Part 1: Promises, Promises — Why Do I Believe?](medium-articles/medium-part-1-why-do-i-believe.md)
- [Part 2: Everybody Wants to Rule the World](medium-articles/medium-part-2-everybody-wants-to-rule-the-world.md)
- [Part 3: Games Without Frontiers](medium-articles/medium-part-3-games-without-frontiers.md)

**Long-form companions:**

- [The Promise-Driven Agent whitepaper](why-promise-driven-agents.md)
- [Promise Theory architecture analysis](promise-theory-architecture.md)

## Chapter 9: Schemas, Skills, Templates, and Reusable Assets

Use these materials while authoring, generating, reviewing, or extending a contract
package.

**Canonical schemas:**

- [Agent contract XSD](../schema/agent-contract.xsd)
- [Agent manifest XSD](../schema/agent-manifest.xsd)
- [Promise common XSD](../schema/promise-common.xsd)

**Authoring and scaffolding:**

- [Authoring Agent Contracts skill](../skills/authoring-agent-contracts/SKILL.md)
- [Contract anatomy reference](../skills/authoring-agent-contracts/references/contract-anatomy.md)
- [Authoring checklist](../skills/authoring-agent-contracts/references/authoring-checklist.md)
- [Skeleton package](../skeleton/README.md)
- [Complete generated-project template](../skeleton/template/)

**Assessment and review shapes:**

- [Assessment-record schema](runtime-assessment/assessment-record.schema.json)
- [Contract-package review report](reviewing-contract-packages/review-report-template.md)
- [Unsafe-commit review exercise](reviewing-contract-packages/worked-review.md)
- [Clinic artifact index](case-studies/clinic-appointments/artifact-index.md)

---

# Appendix A: Complete Documentation Asset Index

| Subject | Primary document |
| --- | --- |
| Documentation navigation | [Documentation Map](README.md) |
| Conceptual introduction | [Contracts, Not Prompts](contracts-not-prompts.md) |
| Methodology whitepaper | [The Promise-Driven Agent](why-promise-driven-agents.md) |
| Promise Theory analysis | [Promise Theory Architecture](promise-theory-architecture.md) |
| Promise Theory interpretation and review questions | [Promise Theory Interpretation and Open Questions](promise-theory-interpretation.md) |
| Vocabulary | [Glossary and Naming Conventions](glossary/README.md) |
| Participant selection | [Choosing a Participant and Document Type](participant-types/README.md) |
| Contract authoring | [Authoring an Agent Contract](authoring-workflow/README.md) |
| Contract-to-code trace | [From Contract to Enforcement](contract-assessment/README.md) |
| Model debugging | [Debugging a FizzBee Counterexample](counterexample-debugging/README.md) |
| Promise composition | [Composing Promises](promise-graph/README.md) |
| Contract evolution | [Evolving an Agent Contract](contract-evolution/README.md) |
| Runtime evidence | [Runtime Assessment and Evidence](runtime-assessment/README.md) |
| Assurance | [Five Questions, Five Kinds of Evidence](assurance-model/README.md) |
| Package review | [Reviewing a Contract Package](reviewing-contract-packages/README.md) |
| Worked review | [The Unsafe Commit Package](reviewing-contract-packages/worked-review.md) |
| Review template | [Contract-Package Review Report](reviewing-contract-packages/review-report-template.md) |
| Practitioner education | [Practitioner Learning Path](learning-path/README.md) |
| Orientation module | [30-Minute Orientation](learning-path/orientation.md) |
| Workshop module | [90-Minute Guided Workshop](learning-path/workshop.md) |
| Role-based routes | [Role-Specific Learning Paths](learning-path/role-paths.md) |
| Knowledge assessment | [Knowledge Check and Answer Key](learning-path/knowledge-check.md) |
| Case study collection | [Case Studies Index](case-studies/README.md) |
| End-to-end case study | [Clinic Appointments](case-studies/clinic-appointments/README.md) |
| Case study artifact map | [Clinic Artifact Index](case-studies/clinic-appointments/artifact-index.md) |
| Draft article collection | [Medium Article Series](medium-articles/README.md) |

# Appendix B: Runnable Example Package Index

## Clinic Appointments — Google ADK

**Package and guidance:**

- [Complete package tree](../examples/clinic-appointments/)
- [Example overview](../examples/clinic-appointments/README.md)
- [Getting started](../examples/clinic-appointments/GETTING-STARTED.md)
- [Recorded demo GIF](../examples/clinic-appointments/media/demo.gif)
- [Recorded demo source](../examples/clinic-appointments/media/demo.cast)
- [Package configuration](../examples/clinic-appointments/pyproject.toml)
- [Gate Makefile](../examples/clinic-appointments/Makefile)
- [Dependency lock](../examples/clinic-appointments/uv.lock)

**Contracts, manifests, and verification:**

- [Clinic orchestrator contract](../examples/clinic-appointments/agent_contracts/agent_clinic_orchestrator.xml)
- [Book appointment contract](../examples/clinic-appointments/agent_contracts/agent_book_appointment.xml)
- [Manage appointment contract](../examples/clinic-appointments/agent_contracts/agent_manage_appointment.xml)
- [Patient registry manifest](../examples/clinic-appointments/agent_contracts/manifest_patient_registry.xml)
- [Insurance eligibility manifest](../examples/clinic-appointments/agent_contracts/manifest_insurance_eligibility.xml)
- [Provider schedule manifest](../examples/clinic-appointments/agent_contracts/manifest_provider_schedule.xml)
- [FizzBee verification script](../examples/clinic-appointments/scripts/verify_fizzbee_contracts.py)
- [Promise-graph verification script](../examples/clinic-appointments/scripts/verify_promise_graph.py)

**Implementation:**

- [Contract machinery](../examples/clinic-appointments/src/clinic/contracts/)
- [ADK construction](../examples/clinic-appointments/src/clinic/agents/build.py)
- [Tool adapters](../examples/clinic-appointments/src/clinic/tools.py)
- [Deterministic services](../examples/clinic-appointments/src/clinic/services/)
- [CLI and runner](../examples/clinic-appointments/src/clinic/__main__.py)
- [Tests](../examples/clinic-appointments/tests/)
- [Vendored schemas](../examples/clinic-appointments/schema/)

## Trials of the Holy Grail — Pydantic AI

**Package and guidance:**

- [Complete package tree](../examples/holy-grail-trials/)
- [Example overview](../examples/holy-grail-trials/README.md)
- [Getting started](../examples/holy-grail-trials/GETTING-STARTED.md)
- [Recorded demo GIF](../examples/holy-grail-trials/media/demo.gif)
- [Recorded demo source](../examples/holy-grail-trials/media/demo.cast)
- [Package configuration](../examples/holy-grail-trials/pyproject.toml)
- [Gate Makefile](../examples/holy-grail-trials/Makefile)
- [Dependency lock](../examples/holy-grail-trials/uv.lock)

**Contracts, manifests, and verification:**

- [Grail quest marshal contract](../examples/holy-grail-trials/agent_contracts/agent_grail_quest_marshal.xml)
- [Bridge of Death contract](../examples/holy-grail-trials/agent_contracts/agent_bridge_of_death.xml)
- [Knights Who Say Ni contract](../examples/holy-grail-trials/agent_contracts/agent_knights_who_say_ni.xml)
- [Grail superagent manifest](../examples/holy-grail-trials/agent_contracts/manifest_grail_superagent.xml)
- [Round Table registry manifest](../examples/holy-grail-trials/agent_contracts/manifest_round_table_registry.xml)
- [Bridgekeeper questions manifest](../examples/holy-grail-trials/agent_contracts/manifest_bridgekeeper_questions.xml)
- [Shrubbery market manifest](../examples/holy-grail-trials/agent_contracts/manifest_shrubbery_market.xml)
- [FizzBee verification script](../examples/holy-grail-trials/scripts/verify_fizzbee_contracts.py)
- [Promise-graph and entailment verification](../examples/holy-grail-trials/scripts/verify_promise_graph.py)

**Implementation:**

- [Contract machinery](../examples/holy-grail-trials/src/grail/contracts/)
- [Pydantic AI construction](../examples/holy-grail-trials/src/grail/agents/build.py)
- [Tool adapters](../examples/holy-grail-trials/src/grail/tools.py)
- [Deterministic services](../examples/holy-grail-trials/src/grail/services/)
- [CLI and runner](../examples/holy-grail-trials/src/grail/__main__.py)
- [Tests](../examples/holy-grail-trials/tests/)
- [Vendored schemas](../examples/holy-grail-trials/schema/)

# Appendix C: Reusable Assets and Repository Context

## Skeleton Template

- [Complete generated-project template tree](../skeleton/template/)
- [Copier configuration](../skeleton/copier.yml)
- [Generated-project README template](../skeleton/template/README.md.jinja)
- [Generated-project getting-started template](../skeleton/template/GETTING-STARTED.md.jinja)
- [Generated-project package configuration](../skeleton/template/pyproject.toml.jinja)
- [Generated-project Makefile](../skeleton/template/Makefile)
- [Barista agent contract](../skeleton/template/agent_contracts/agent_barista.xml)
- [Machine manifest](../skeleton/template/agent_contracts/manifest_machine.xml)
- [Template agent-contract schema](../skeleton/template/schema/agent-contract.xsd)
- [Template agent-manifest schema](../skeleton/template/schema/agent-manifest.xsd)
- [Template shared vocabulary](../skeleton/template/schema/promise-common.xsd)
- [FizzBee verifier template](../skeleton/template/scripts/verify_fizzbee_contracts.py.jinja)
- [Promise-graph verifier template](../skeleton/template/scripts/verify_promise_graph.py.jinja)
- [Contract-validation test template](../skeleton/template/tests/test_contracts_validate.py.jinja)
- [Model-gate test template](../skeleton/template/tests/test_gate.py.jinja)
- [Contract loader package](../skeleton/template/src/{{package_name}}/contracts/)

## Repository Context

- [Repository README](../README.md)
- [Documentation Map](README.md)
- [Apache 2.0 License](../LICENSE)

Intentional schema copies live in the [skeleton template](../skeleton/template/schema/),
[Clinic example](../examples/clinic-appointments/schema/), and
[Holy Grail example](../examples/holy-grail-trials/schema/).

The corpus is living material. When adding a chapter or supporting artifact, place it
where a reader first needs it, add its detailed entry to the appropriate appendix, and
update both this contents map and the question-driven [Documentation Map](README.md).
