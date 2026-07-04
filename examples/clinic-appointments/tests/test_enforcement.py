"""Enforcement-twin tests — the code half of the contract's invariants.

Every FizzBee `always assertion` in the contracts has a code twin in
`clinic.services`. These tests exercise those twins directly (no LLM, no ADK, no
creds): they prove the invariants hold even when a caller *tries* to violate
them — which is exactly the assurance model-checking alone cannot give, because
model-checking proves the spec, not the stochastic agent's behavior.
"""

from __future__ import annotations

import pytest

from clinic import services


@pytest.fixture(autouse=True)
def fresh_world():
    services.reset()
    yield


def _verify_ada() -> str:
    r = services.registry.verify_identity(name="Ada Lovelace", dob="1990-01-01")
    assert r["ok"], r
    return r["patient"]["id"]


# ---- book_appointment invariants ----

def test_no_double_book():
    """NoDoubleBook: committing a taken slot is refused."""
    pid = _verify_ada()
    first = services.schedule.commit_booking(
        pid, "PR1", "S1", "dermatology", eligibility_ok=True, confirmed=True
    )
    assert first["ok"], first
    again = services.schedule.commit_booking(
        pid, "PR1", "S1", "dermatology", eligibility_ok=True, confirmed=True
    )
    assert again["ok"] is False
    assert again["refusal"] == "slot_taken"
    assert again["unmet"] == "slot_available"


def test_eligibility_before_booking():
    """EligibilityBeforeBooking / CoveredOrSelfPay: no eligibility clearance -> refused."""
    pid = _verify_ada()
    res = services.schedule.commit_booking(
        pid, "PR1", "S1", "dermatology", eligibility_ok=False, confirmed=True
    )
    assert res["ok"] is False
    assert res["unmet"] == "eligibility_checked"


def test_confirm_before_booking():
    """ConfirmBeforeBooking: no confirmation -> refused."""
    pid = _verify_ada()
    res = services.schedule.commit_booking(
        pid, "PR1", "S1", "dermatology", eligibility_ok=True, confirmed=False
    )
    assert res["ok"] is False
    assert res["unmet"] == "booking_confirmed"


# ---- manage_appointment invariants ----

def test_cancel_requires_ownership():
    """CancelRequiresOwnership: cancelling another patient's appointment is refused."""
    # A1 belongs to Ada (P1). Verify Grace (P2) and try to cancel it.
    r = services.registry.verify_identity(name="Grace Hopper", dob="1985-05-05")
    assert r["ok"], r
    grace = r["patient"]["id"]
    res = services.schedule.cancel_booking(grace, "A1")
    assert res["ok"] is False
    assert res["refusal"] == "not_owned"
    assert res["unmet"] == "owns_appointment"


def test_owner_can_cancel_and_slot_is_freed():
    pid = _verify_ada()
    res = services.schedule.cancel_booking(pid, "A1")
    assert res["ok"], res
    # the freed slot S6 is open again
    open_slots = {s["id"] for s in services.schedule.list_open_slots("PR1")["slots"]}
    assert "S6" in open_slots


def test_reschedule_no_double_book():
    """RescheduleNoDoubleBook: moving onto a taken slot is refused."""
    ada = _verify_ada()
    # Book S1 for Ada, then try to reschedule Ada's existing A1 onto S1 (now taken).
    booked = services.schedule.commit_booking(
        ada, "PR1", "S1", "dermatology", eligibility_ok=True, confirmed=True
    )
    assert booked["ok"], booked
    res = services.schedule.reschedule_booking(ada, "A1", "S1", confirmed=True)
    assert res["ok"] is False
    assert res["unmet"] == "new_slot_available"


def test_reschedule_requires_confirmation():
    ada = _verify_ada()
    res = services.schedule.reschedule_booking(ada, "A1", "S2", confirmed=False)
    assert res["ok"] is False
    assert res["unmet"] == "change_confirmed"


# ---- registry isolation ----

def test_record_isolation():
    """A patient only ever sees their own appointments."""
    ada = _verify_ada()
    ada_appts = services.schedule.list_appointments(ada)["appointments"]
    assert all(a["patientId"] == ada for a in ada_appts)
    assert any(a["id"] == "A1" for a in ada_appts)  # Ada owns the seeded appointment
    grace = services.registry.verify_identity(name="Grace Hopper", dob="1985-05-05")["patient"]["id"]
    grace_appts = services.schedule.list_appointments(grace)["appointments"]
    assert grace_appts == []  # Grace has none; Ada's A1 is not visible to her


# ---- eligibility verdicts ----

def test_eligibility_covered_vs_not():
    ada = _verify_ada()  # PLAN_A covers dermatology, not cardiology
    assert services.eligibility.check(ada, "dermatology")["eligible"] is True
    not_covered = services.eligibility.check(ada, "cardiology")
    assert not_covered["eligible"] is False
    assert not_covered["estimatedSelfPay"] == 300
