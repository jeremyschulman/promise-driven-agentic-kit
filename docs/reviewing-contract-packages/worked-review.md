# Worked Review: The Unsafe Commit Package

This exercise presents a deliberately flawed, domain-neutral contract package. Review
the excerpts before reading the findings. The package is illustrative and is not
intended to validate or run.

## Scenario

`workflow_agent` offers `safe_action` to a requester. It may call
`authority_service.commit_action`, but only when `precondition_met` is true. The safety
promise says no commit may occur while the precondition is false.

The author reports that:

- The XML is complete.
- The model is “verified.”
- The Python function returns a structured refusal.
- The enforcement test passes.
- The runtime record says protected state did not change.

Your task is to decide whether the package is ready and write findings that identify
the unsupported claims.

## Artifact A: behavior model and enforcement declaration

```xml
<verifiable-behavior>
  <fizzbee mode="runtime-instructions">
    action Init:
        precondition_met = oneof [True, False]
        committed = False

    atomic action CommitAction:
        require not committed
        committed = True

    always assertion NoUnsafeCommit:
        return (not committed) or precondition_met
  </fizzbee>
</verifiable-behavior>

<enforcement>
  <rule id="NoUnsafeCommit">
    commit_action refuses unless precondition_met is true.
  </rule>
</enforcement>
```

## Artifact B: promise manifest

```xml
<promises>
  <tools>
    <tool name="commit_action"/>
  </tools>

  <offer id="safe_action" type="workflow" to="requester">
    <body>Commit only after the required evidence is present.</body>
    <condition ref="precondition_met"/>
  </offer>

  <offer id="no_unsafe_commit" type="invariant" to="requester compliance">
    <body>No action is committed before its precondition holds.</body>
  </offer>

  <use id="evidence" from="evidence_provider" quenches="evidence_ready">
    <body>Use provider evidence before committing.</body>
  </use>
</promises>
```

The provider publishes `<offer id="evidence">` to `workflow_agent`.

## Artifact C: Python enforcement

```python
def commit_action(*, precondition_met: bool) -> dict:
    apply_change()

    if not precondition_met:
        return {
            "ok": False,
            "refusal": "precondition_required",
            "unmet": "evidence_ready",
            "message": "The precondition must hold.",
        }

    return {"ok": True, "committed": True}
```

## Artifact D: enforcement test

```python
def test_no_unsafe_commit():
    result = commit_action(precondition_met=False)

    assert result["ok"] is False
    assert result["refusal"] == "precondition_required"
```

The test passes.

## Artifact E: runtime assessment record

```json
{
  "schemaVersion": "1.0",
  "assessmentId": "asm-104",
  "occurredAt": "2026-07-11T19:10:00Z",
  "correlationId": "req-82",
  "assessor": {"agent": "authority_service"},
  "promiser": {"agent": "workflow_agent"},
  "promise": {
    "id": "no_unsafe_commit",
    "polarity": "offer",
    "type": "invariant",
    "safetyIdentity": "NoUnsafeCommit",
    "contractDocument": "agent_safe_workflow.xml",
    "contractVersion": "0.9"
  },
  "operation": {
    "name": "commit_action",
    "requestId": "op-82"
  },
  "decision": {
    "outcome": "refused",
    "refusalCode": "precondition_required",
    "unmet": "evidence_ready",
    "stateChanged": false
  },
  "assessment": {
    "status": "kept",
    "basis": "Request for jordan@example.test was safely refused."
  },
  "evidence": [
    {"kind": "refusal", "ref": "result://op-82"}
  ],
  "privacy": {
    "classification": "public",
    "redactedFields": []
  }
}
```

The XML package under review declares version `1.0`.

## Review worksheet

Before continuing, record:

1. The review outcome: Approved, Approved with follow-up, Changes required, or Unable
   to assess.
2. Every safety, condition, capability, and promise identity you can trace.
3. At least one finding in each affected severity category.
4. The gate or evidence that would verify each repair.

---

## Findings

### P0: The model permits the forbidden commit

**Evidence:** Artifact A, `CommitAction` and `NoUnsafeCommit`.

`Init` explores `precondition_met=False`, but `CommitAction` requires only that the
operation has not already committed. The action can set `committed=True` while the
precondition is false, violating `NoUnsafeCommit`.

**Consequence:** The modeled safety claim is false. A current FizzBee run should return
a counterexample, so an unqualified “verified” label is stale, incorrect, or attached
to a different model.

**Required change:** Guard `CommitAction` with `require precondition_met` and run the
checker against the exact reviewed artifact. Preserve the counterexample as evidence
until the repair is verified.

### P0: The conditional promise has no declared quencher

**Evidence:** Artifact B, `condition ref="precondition_met"` and
`quenches="evidence_ready"`.

The provider offer `evidence` can bind to the use by `(from, id)`, but the use quenches
a different condition. `precondition_met` remains unsatisfied in the declared promise
graph.

**Consequence:** The package has no compositionally complete path for keeping
`safe_action`. A graph verifier should reject it.

**Required change:** Make the use quench `precondition_met`, or introduce and model an
intentional transformation between distinct facts. Re-run promise-graph verification.

### P0: Python mutates protected state before evaluating the guard

**Evidence:** Artifact C, `apply_change()` precedes the condition check.

The function returns a refusal after performing the forbidden change. Structured
refusal wording does not reverse the mutation or keep `NoUnsafeCommit`.

**Consequence:** The production boundary can execute the exact unsafe state transition
the contract forbids.

**Required change:** Derive the condition from authoritative state and return before
`apply_change()` when it is false. Verify the decision and mutation are atomic enough
for concurrent callers.

### P1: Refusal evidence drifts from the condition identity

**Evidence:** Artifacts B, C, and E.

The conditional promise uses `precondition_met`, while Python and the assessment record
emit `evidence_ready` as the unmet condition.

**Consequence:** Reviewers and callers cannot reliably join the runtime decision to the
contract condition. Metrics or trust calculations may group unlike facts.

**Required change:** Emit `precondition_met` in the structured refusal and assessment
record. Keep `evidence` as the provider capability identity rather than renaming the
condition after it.

### P1: The enforcement twin proves only that a dictionary says no

**Evidence:** Artifact D.

The test checks the refusal flag and code but never inspects protected state. It passes
even though `apply_change()` executed.

**Consequence:** The passing suite creates false confidence about the implementation
duty the test is supposed to assess.

**Required change:** Snapshot or query authoritative state before and after the call,
assert no forbidden change, and add a permitted-path test showing that valid operations
still commit.

### P0: Runtime evidence contradicts executable behavior

**Evidence:** Artifacts C and E, `stateChanged`.

The assessment record says `stateChanged=false`, while the function mutates state before
returning the refusal.

**Consequence:** The record materially misrepresents the boundary decision. A ledger
built from this field would be false evidence, not merely incomplete telemetry.

**Required change:** Derive assessment evidence from the authoritative transaction
result rather than hard-coded outcome fields. Add an integration test that compares the
record with persisted state.

### P1: The assessment record cannot resolve to the reviewed version

**Evidence:** Artifact E reports contract version `0.9`; the package is version `1.0`.

**Consequence:** The record cannot support a claim about the specification under
review. It may describe an older meaning of the same identifiers.

**Required change:** Stamp records from the loaded contract or manifest version and
test that construction, enforcement, and evidence use one release identity.

### P1: Public evidence contains unnecessary personal data

**Evidence:** Artifact E places an email address in `assessment.basis` while declaring
the record `public` with no redactions.

**Consequence:** The ledger can disclose personal data to readers who need only the
promise and decision identities.

**Required change:** Use a non-identifying basis statement, classify before persistence,
and test redaction at the evidence writer.

## Review decision

**Changes required.** The package contains four P0 blocking defects and four P1
assurance gaps. The passing unit test and structured refusal do not compensate for the
unsafe model, incomplete graph, pre-guard mutation, or false runtime evidence.

## Corrected trace

The minimum corrected identities are:

```text
Safety:     NoUnsafeCommit
Condition:  precondition_met
Capability: commit_action
Promise:    safe_action / no_unsafe_commit / evidence
Version:    1.0 across contract, code release, and assessment
```

The key repairs should have this shape:

```python
def commit_action(*, precondition_met: bool) -> dict:
    if not precondition_met:
        return {
            "ok": False,
            "refusal": "precondition_required",
            "unmet": "precondition_met",
            "message": "The precondition must hold.",
        }

    apply_change()
    return {"ok": True, "committed": True}
```

```python
def test_no_unsafe_commit():
    before = authoritative_state_snapshot()
    result = commit_action(precondition_met=False)

    assert result["ok"] is False
    assert result["unmet"] == "precondition_met"
    assert authoritative_state_snapshot() == before
```

Approval still requires the complete package gate: schema validation, a clean model
check, a coherent promise graph, the full test suite, and a runtime assessment record
that agrees with authoritative state.

Use the [review-report template](review-report-template.md) to rewrite these findings
as a formal package review.
