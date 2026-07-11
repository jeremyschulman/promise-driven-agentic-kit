# Role-Specific Learning Paths

Every path begins with the [30-minute orientation](orientation.md). The specialization
describes the responsibility being performed, not a permanent job title; one person may
need several paths.

## Software engineer

**Objective:** Author and implement a complete promise with deterministic enforcement.

1. [Authoring an Agent Contract](../authoring-workflow/README.md)
2. [From Contract to Enforcement](../contract-assessment/README.md)
3. [Composing Promises](../promise-graph/README.md)
4. [Debugging a FizzBee Counterexample](../counterexample-debugging/README.md)
5. [90-minute guided workshop](workshop.md)
6. [Clinic Appointments end-to-end case study](../case-studies/clinic-appointments/README.md)
7. [Authoring checklist](../../skills/authoring-agent-contracts/references/authoring-checklist.md)

**Completion evidence:** Produce one contract package whose forbidden and permitted
paths pass the complete gate.

## Software architect

**Objective:** Choose participant boundaries and evaluate system-level composition and
assurance claims.

1. [Choosing a Participant and Document Type](../participant-types/README.md)
2. [Composing Promises](../promise-graph/README.md)
3. [Promise Theory Architecture](../promise-theory-architecture.md)
4. [Five Questions, Five Kinds of Evidence](../assurance-model/README.md)
5. [Reviewing a Contract Package](../reviewing-contract-packages/README.md)
6. [Evolving an Agent Contract](../contract-evolution/README.md)

**Completion evidence:** Draw the participant and promise boundaries for a proposed
workflow and defend which facts are authoritative at each consequential operation.

## Formal-methods reviewer

**Objective:** Evaluate model scope, reachability, invariants, counterexamples, and the
limits of formal claims.

1. [Contract anatomy reference](../../skills/authoring-agent-contracts/references/contract-anatomy.md)
2. [Authoring an Agent Contract](../authoring-workflow/README.md), Design sections
3. [Debugging a FizzBee Counterexample](../counterexample-debugging/README.md)
4. [Five Questions, Five Kinds of Evidence](../assurance-model/README.md)
5. [Worked package review](../reviewing-contract-packages/worked-review.md)
6. [Clinic Appointments end-to-end case study](../case-studies/clinic-appointments/README.md)
7. Both complete examples under [`examples/`](../../examples/)

**Completion evidence:** Review an invariant and state precisely what the successful
model result establishes, which assumptions remain, and which runtime duties require
independent evidence.

## Runtime and operations engineer

**Objective:** Operate authoritative boundaries and preserve useful, private evidence.

1. [From Contract to Enforcement](../contract-assessment/README.md), Run section
2. [Runtime Assessment and Evidence](../runtime-assessment/README.md)
3. [Generic assessment-record schema](../runtime-assessment/assessment-record.schema.json)
4. [Evolving an Agent Contract](../contract-evolution/README.md), Run compatibility
5. [Reviewing a Contract Package](../reviewing-contract-packages/README.md), Run review

**Completion evidence:** Define receipt, refusal, failure, unknown, idempotency,
reconciliation, privacy, and retention behavior for one consequential operation.

## Engineering leader or adoption sponsor

**Objective:** Evaluate where the method adds assurance, what it costs, and what claims
the organization may honestly make.

1. [Contracts, Not Prompts](../contracts-not-prompts.md)
2. [From Contract to Enforcement](../contract-assessment/README.md)
3. [Five Questions, Five Kinds of Evidence](../assurance-model/README.md)
4. [The Promise-Driven Agent](../why-promise-driven-agents.md), Parts VIII-X
5. [Reviewing a Contract Package](../reviewing-contract-packages/README.md), outcomes

**Completion evidence:** Select a bounded pilot workflow, identify its consequential
operation and authoritative owner, and define success without claiming universal agent
correctness.

## Suggested team sequence

| Session | Participants | Material | Team output |
| --- | --- | --- | --- |
| 1 | All roles | Orientation and knowledge check | Shared vocabulary and misconception list |
| 2 | Engineers, architect, reviewer | Guided workshop | One complete generic contract trace |
| 3 | Architect, reviewer, operations | Worked package review | Independent findings and approval decision |
| 4 | Pilot team and sponsor | Domain mapping | Candidate workflow, boundaries, risks, and evidence plan |

Return to the [Practitioner Learning Path](README.md) for the common completion
criteria.
