# Knowledge Check

Complete the questions without consulting the answer key. The purpose is to reveal
which responsibility boundaries are still blurry, not to produce a score for its own
sake.

## Questions

### 1. Agent boundary

A deterministic scheduling service owns appointment state and rejects conflicting
writes. Does it qualify as an agent in this methodology, and which document would it
normally use?

### 2. Contract terminology

What is the difference between an **agent contract** and its
`<verifiable-behavior>` section?

### 3. Assurance claim

FizzBee reports that `NoUnsafeCommit` holds. Which claim is justified?

A. The LLM will never request an unsafe commit.

B. The Python implementation enforces every modeled guard.

C. No reachable state represented by the checked model violates the invariant.

D. The whole deployed system is safe.

### 4. Guard and invariant

Why does a guarded action still need an invariant?

### 5. Promise composition

The consumer declares `<use id="evidence" from="provider">`. Another agent also
offers `evidence`, but `provider` does not. Is the use bound?

### 6. Condition identity

An offer requires `<condition ref="review_complete">`, while its accepted dependency
uses `quenches="review_evidence"`. What must the reviewer determine?

### 7. Enforcement twin

A test calls the boundary with an unmet condition and asserts only
`result["ok"] is False`. What essential evidence is missing?

### 8. Refusal assessment

The boundary refuses because `review_complete` is false and protected state remains
unchanged. Give the likely operational outcome and two possible promise assessments.

### 9. Failure versus refusal

A database connection raises before the boundary can determine whether the write
committed. Should the result be translated into a structured refusal?

### 10. Unknown outcome

What must happen before retrying a consequential operation whose result is unknown?

### 11. External party

Why should an absent local manifest not automatically cause a participant to be
classified as external?

### 12. Contract evolution

Renaming `precondition_met` changes no prose meaning. Name at least four artifact
locations that may still require updates.

### 13. Package review

Every automated gate is green, but runtime assessment records cannot be tied to a
contract version. Which review category and outcome are appropriate?

### 14. Trust

A provider has a high historical keep rate. May that trust score satisfy a current
authorization guard?

### 15. Scenario

Review this sequence:

```python
def publish_record(*, review_complete: bool) -> dict:
    store.publish()
    if not review_complete:
        return refusal("review_required", "review_complete")
    return {"ok": True}
```

Identify the primary defect, its likely review severity, and the minimum test needed to
demonstrate the repair.

---

## Answer key

### 1

Yes. It is a deterministic agent because it owns authoritative state and an autonomous
accept-or-refuse boundary. It normally publishes a `manifest_<agent>.xml`.

### 2

The agent contract is the entire six-section runtime instruction artifact. The
`<verifiable-behavior>` section is only its embedded model-checkable FizzBee behavior.

### 3

**C.** The invariant holds over every reachable state represented by the checked
model. The result does not prove the LLM, Python, model completeness, or whole system.

### 4

A guard states when one action is enabled. An invariant states what must remain true
across every reachable modeled state, including paths involving other actions or future
changes.

### 5

No. Binding resolves the exact `(from, id)` pair. An identically named offer on a
different provider does not satisfy the declared use.

### 6

The reviewer must determine whether the names represent accidental identity drift or
two intentionally distinct facts connected by a modeled transformation. Without that
relationship, `review_complete` is unquenched.

### 7

The test must assert the refusal code, exact unmet condition, and most importantly that
authoritative protected state did not change. A permitted-path test is also needed to
show the guard does not block everything.

### 8

The operational outcome is `refused`. The safety promise can be assessed `kept`, while
the conditional publish capability can be assessed `not-applicable`.

### 9

No. This is a failure or possibly an unknown outcome, not normal non-cooperation.
Relabeling it as refusal would hide the need for reconciliation or repair.

### 10

Use the idempotency key, receipt lookup, or authoritative resource state to reconcile
whether the operation committed. Do not retry blindly.

### 11

External status is a governance decision with a narrow verifier exemption. A locally
governed deterministic provider may simply have a missing manifest, which is a package
defect rather than evidence that it is external.

### 12

Possible locations include FizzBee state and guards, `<condition ref>`,
`<use quenches>`, Python authoritative checks, refusal `unmet`, tests, runtime
assessment records, callers, metrics, documentation, and diagrams.

### 13

This is a **P1 assurance gap** because required version traceability is absent. The
package outcome is **Changes required** until records identify the specification in
force.

### 14

No. Trust may change reliance strategy, such as requiring fresher evidence or choosing
another provider. It cannot satisfy a guard, grant authorization, or bypass current
authoritative assessment.

### 15

The function mutates authoritative state before evaluating the guard. This is a **P0
blocking defect**. Move the guard before `store.publish()`, then test the forbidden call
by asserting structured refusal and unchanged store state. Also test that a reviewed
record can publish.

## Interpreting the result

- Revisit the [orientation](orientation.md) if questions 1-4 are unclear.
- Revisit [Composing Promises](../promise-graph/README.md) for questions 5-6 and 11.
- Revisit [From Contract to Enforcement](../contract-assessment/README.md) for questions
  7 and 15.
- Revisit [Runtime Assessment and Evidence](../runtime-assessment/README.md) for
  questions 8-10 and 14.
- Revisit [Evolving an Agent Contract](../contract-evolution/README.md) and
  [Reviewing a Contract Package](../reviewing-contract-packages/README.md) for questions
  12-13.
