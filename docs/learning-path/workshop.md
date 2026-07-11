# 90-Minute Guided Workshop

This workshop builds one complete promise chain for a small, domain-neutral workflow.
It can be completed on paper, in a shared document, or by adapting the repository
skeleton. The checkpoints show the intended shape; learners should attempt each task
before reading them.

## Workshop outcome

By the end, the learner will have designed:

- One LLM workflow agent
- Two deterministic participants
- One conditional capability promise
- One FizzBee safety invariant
- One provider dependency that quenches the condition
- One authoritative Python boundary
- Forbidden-path and permitted-path tests
- One structured refusal and assessment record
- One package-review decision

## Scenario

An LLM-assisted workflow prepares a record for publication. Publishing is
consequential and may occur only after an independent review service has completed its
review.

The participants are:

| Participant | Role | Representation |
| --- | --- | --- |
| `authoring_agent` | Interprets the request and proposes publication | `agent_authoring.xml` |
| `review_service` | Publishes authoritative review evidence | `manifest_review_service.xml` |
| `publication_service` | Owns published state and the final decision | `manifest_publication_service.xml` plus Python |
| `requester` | Requests and assesses the result | External party |

The target behavior is:

> Publish the record only when `review_complete` is true. Otherwise refuse with
> `review_required`, identify `review_complete` as unmet, and leave published state
> unchanged.

## Minute 0-10: identify the promise and authority

### Task

Answer four questions before writing XML:

1. What capability is being offered?
2. What fact gates it?
3. Who is authoritative for that fact?
4. Who owns the irreversible state change?

### Checkpoint

| Question | Answer |
| --- | --- |
| Capability | `publish_record` |
| Condition | `review_complete` |
| Condition authority | `review_service` supplies `review_evidence` |
| Commit authority | `publication_service` |

The LLM does not own either fact. It may decide when to propose publication, but it
cannot declare the review complete or write published state directly.

Choose the identities now:

```text
Action:      PublishRecord
Safety:      NoUnreviewedPublish
Condition:   review_complete
Capability:  publish_record
Offer:       reviewed_publish
Dependency:  review_evidence
Refusal:     review_required
```

## Minute 10-25: model the forbidden state

### Task

Start with this unsafe FizzBee model:

```python
action Init:
    review_complete = oneof [True, False]
    published = False

atomic action PublishRecord:
    require not published
    published = True

always assertion NoUnreviewedPublish:
    return (not published) or review_complete
```

Predict the counterexample before running a checker. Then make the forbidden state
unreachable without weakening the invariant.

### Expected counterexample

```text
Init(review_complete=False, published=False)
PublishRecord
state(review_complete=False, published=True)
NoUnreviewedPublish violated
```

### Checkpoint

```python
atomic action PublishRecord:
    require review_complete
    require not published
    published = True
```

The guard controls the action. The invariant remains as the package-wide safety claim
checked over every reachable modeled state.

Record the model boundary: it represents review status and publication state, but not
review quality, storage availability, authorization, or concurrent transactions.
Those omitted facts require separate promises or runtime duties if the real system
claims them.

## Minute 25-40: declare cooperation

### Task

Complete the workflow agent's promise manifest so the conditional offer has a declared
path to satisfaction.

```xml
<promises>
  <tools>
    <tool name="publish_record"/>
  </tools>

  <offer id="reviewed_publish" type="workflow" to="requester">
    <body>Publish the requested record only after independent review completes.</body>
    <condition ref="review_complete"/>
  </offer>

  <offer id="no_unreviewed_publish" type="invariant"
         to="requester compliance">
    <body>No record is published before independent review completes.</body>
  </offer>

  <use id="review_evidence" from="review_service"
       quenches="__________">
    <body>Use authoritative review evidence before proposing publication.</body>
  </use>

  <use id="publish_record" from="publication_service">
    <body>Use the publication service for the authoritative commit decision.</body>
  </use>
</promises>
```

### Checkpoint

The blank is `review_complete`. The provider publishes the exact offer used by the
consumer:

```xml
<agent-manifest agent="review_service" version="1.0">
  <description>Owns independent review status.</description>
  <promises>
    <offer id="review_evidence" type="session-state"
           to="authoring_agent publication_service">
      <body>Provide the current authoritative review result for a record.</body>
    </offer>
  </promises>
</agent-manifest>
```

The publication boundary also publishes what the workflow uses:

```xml
<agent-manifest agent="publication_service" version="1.0">
  <description>Owns published state and the final publication decision.</description>
  <promises>
    <offer id="publish_record" type="workflow" to="authoring_agent">
      <body>Publish only when current authoritative review evidence permits it.</body>
      <condition ref="review_complete"/>
    </offer>
    <use id="review_evidence" from="review_service"
         quenches="review_complete">
      <body>Reassess current review evidence at the publication boundary.</body>
    </use>
  </promises>
</agent-manifest>
```

The graph relationship is now:

```text
review_service +review_evidence -> authoring_agent
authoring_agent -review_evidence, quenches review_complete
authoring_agent +reviewed_publish | review_complete -> requester
review_service +review_evidence -> publication_service
publication_service -review_evidence, quenches review_complete
publication_service +publish_record -> authoring_agent
authoring_agent -publish_record -> publication_service
```

## Minute 40-50: complete the six-section intent

### Task

Write the runtime judgment, enforcement traceability, and refusal language.

### Checkpoint

```xml
<step-guidance action="PublishRecord">
  <binding>
    Obtain current review evidence, then call publish_record. Relay the service
    result without claiming publication before a commit receipt is returned.
  </binding>
</step-guidance>

<enforcement>
  <rule id="NoUnreviewedPublish">
    publication_service refuses unless review_complete is authoritative and true.
  </rule>
</enforcement>

<responses>
  <review-required>
    I cannot publish this record until independent review is complete.
  </review-required>
  <published>The reviewed record was published.</published>
</responses>
```

The matching `NoUnreviewedPublish` name connects the model property to the expected
implementation duty. The prose guides the LLM; it does not enforce publication.

## Minute 50-65: implement the boundary

### Task

Identify both defects in this starter function:

```python
def publish_record(record_id: str, *, review_complete: bool) -> dict:
    store.mark_published(record_id)

    if not review_complete:
        return refusal(
            "review_required",
            "review_evidence",
            "Independent review must complete before publication.",
        )

    return {"ok": True, "published": record_id}
```

### Checkpoint

The function mutates before checking the guard, and the refusal emits the provider
capability instead of the condition identity. A corrected teaching shape is:

```python
def publish_record(record_id: str) -> dict:
    review_complete = review_store.is_complete(record_id)
    if not review_complete:
        return refusal(
            "review_required",
            "review_complete",
            "Independent review must complete before publication.",
        )

    store.mark_published(record_id)
    return {
        "ok": True,
        "published": record_id,
        "receipt": store.publication_receipt(record_id),
    }
```

The boundary derives the fact from authoritative state rather than accepting a boolean
chosen by the LLM. A production implementation must also make the final review check
and publication atomic enough for concurrent changes.

## Minute 65-75: build the enforcement twin

### Task

Write one forbidden-path test and one permitted-path test.

### Checkpoint

```python
def test_no_unreviewed_publish():
    record_id = store.create_draft(review_complete=False)
    before = store.snapshot(record_id)

    result = publish_record(record_id)

    assert result["ok"] is False
    assert result["refusal"] == "review_required"
    assert result["unmet"] == "review_complete"
    assert store.snapshot(record_id) == before


def test_reviewed_record_can_publish():
    record_id = store.create_draft(review_complete=True)

    result = publish_record(record_id)

    assert result["ok"] is True
    assert result["receipt"]
    assert store.is_published(record_id)
```

The forbidden test demonstrates safety for the exercised case. The permitted test
demonstrates that the repair did not make the capability impossible.

## Minute 75-83: classify the runtime result

### Task

For an unreviewed record, classify:

- Operational outcome
- `NoUnreviewedPublish` assessment
- `reviewed_publish` assessment
- Minimum evidence

### Checkpoint

```text
Operational outcome:        refused
NoUnreviewedPublish:         kept
reviewed_publish:            not-applicable
Condition evidence:          review_complete = false
Protected state:             unchanged
Correlation and version:     required
```

One assessment record can evaluate the safety promise:

```json
{
  "assessor": {"agent": "publication_service"},
  "promiser": {"agent": "authoring_agent"},
  "promise": {
    "id": "no_unreviewed_publish",
    "polarity": "offer",
    "type": "invariant",
    "safetyIdentity": "NoUnreviewedPublish",
    "contractDocument": "agent_authoring.xml",
    "contractVersion": "1.0"
  },
  "operation": {"name": "publish_record", "requestId": "op-17"},
  "decision": {
    "outcome": "refused",
    "refusalCode": "review_required",
    "unmet": "review_complete",
    "stateChanged": false
  },
  "assessment": {
    "status": "kept",
    "basis": "Publication was refused while review was incomplete."
  }
}
```

The repository's generic assessment schema requires additional record, correlation,
evidence, and privacy fields. The excerpt focuses on the identities being learned.

## Minute 83-90: review the package

### Task

Use the P0-P3 model to decide whether each issue blocks approval:

1. The model-check result references contract version `0.9`; the package is `1.0`.
2. The test checks refusal but not unchanged state.
3. Response prose says “review evidence is recommended” rather than required.
4. The code reads review status from a request argument rather than authoritative state.

### Checkpoint

| Issue | Severity | Reason |
| --- | --- | --- |
| Stale model evidence | P1 | The reviewed version lacks supporting proof. |
| Missing unchanged-state assertion | P1 | The enforcement claim is not demonstrated. |
| Misleading response prose | P3, or higher if it changes reliance | The requirement can be misunderstood. |
| Caller-supplied authoritative fact | P0 | The consequential boundary can be bypassed. |

The package outcome is **Changes required** because P0 and P1 findings remain.

## Complete gate

Before approval, the real package must produce current evidence from:

```bash
xmllint --noout --schema schema/agent-contract.xsd \
  agent_contracts/agent_authoring.xml

uv run python scripts/verify_fizzbee_contracts.py
uv run python scripts/verify_promise_graph.py
uv run pytest -q
```

The learner should be able to explain the distinct claim supported by every command.

## Facilitator notes

- Ask learners to predict the counterexample before showing it.
- Do not reveal the condition/capability identity mismatch too early.
- Require the unchanged-state assertion; it is the workshop's most important test
  detail.
- Ask one learner to assess the refusal as the publication service and another as the
  requester. Compare viewpoints without forcing one universal assessment.
- End with the package decision. A polished contract excerpt should not distract from
  missing evidence.

## Workshop completion evidence

- [ ] Promise statement identifies capability, condition, refusal, and protected state.
- [ ] FizzBee guard makes the unsafe state unreachable.
- [ ] Invariant remains explicit and model-checkable.
- [ ] Provider use quenches the exact condition.
- [ ] Publication service is visible as a deterministic participant.
- [ ] Python reads authoritative state and guards before mutation.
- [ ] Forbidden and permitted paths are tested.
- [ ] Runtime outcome and promise assessments are distinct.
- [ ] Package decision follows the highest unresolved finding.

Continue with the [knowledge check](knowledge-check.md), then choose a
[role-specific path](role-paths.md).
