"""Enforcement-twin tests — the code half of the contracts' invariants.

Exercised directly (no LLM, no framework, no creds): they prove the trials'
gates hold even when a caller tries to violate them — the assurance
model-checking alone cannot give.
"""

from __future__ import annotations

import pytest

from grail import services


@pytest.fixture(autouse=True)
def fresh_world():
    services.reset()
    yield


def _verify_lancelot() -> str:
    r = services.registry.verify_knight("Sir Lancelot", "to seek the Holy Grail")
    assert r["ok"], r
    return r["knight"]["id"]


# ---- Bridge of Death: NoCrossingWithWrongAnswer / ThreeQuestionsBeforeCrossing ----

def test_no_crossing_with_wrong_answer():
    kid = _verify_lancelot()  # true favourite colour is "blue"
    res = services.bridgekeeper.judge_crossing(kid, "Sir Lancelot", "to seek the Holy Grail", "green")
    assert res["ok"] and res["crossed"] is False
    assert services.registry.quest_progress(kid)["bridge"] is False  # not recorded


def test_crossing_with_correct_answers():
    kid = _verify_lancelot()
    res = services.bridgekeeper.judge_crossing(kid, "Sir Lancelot", "to seek the Holy Grail", "blue")
    assert res["ok"] and res["crossed"] is True
    assert services.registry.quest_progress(kid)["bridge"] is True


def test_three_questions_required():
    kid = _verify_lancelot()
    res = services.bridgekeeper.judge_crossing(kid, "Sir Lancelot", "to seek the Holy Grail", "")
    assert res["crossed"] is False
    assert services.registry.quest_progress(kid)["bridge"] is False


# ---- Knights Who Say Ni: ShrubberyMustBeAcceptable ----

def test_shrubbery_too_expensive():
    kid = _verify_lancelot()  # budget 50; SH3 costs 90
    res = services.shrubbery.judge_shrubbery(kid, "SH3")
    assert res["acceptable"] is False and "expensive" in res["reason"]
    assert services.registry.quest_progress(kid)["ni"] is False


def test_shrubbery_too_plain():
    kid = _verify_lancelot()  # SH4 niceness 1 < bar 5
    res = services.shrubbery.judge_shrubbery(kid, "SH4")
    assert res["acceptable"] is False and "nice" in res["reason"]


def test_acceptable_shrubbery_passes():
    kid = _verify_lancelot()  # SH2 niceness 8, price 40 <= budget 50
    res = services.shrubbery.judge_shrubbery(kid, "SH2")
    assert res["acceptable"] is True
    assert services.registry.quest_progress(kid)["ni"] is True


# ---- Marshal: GrailRequiresBothTrials (assisted promise) ----

def test_grail_requires_both_trials():
    kid = _verify_lancelot()
    assert services.registry.may_seek_grail(kid) is False
    services.bridgekeeper.judge_crossing(kid, "Sir Lancelot", "to seek the Holy Grail", "blue")
    assert services.registry.may_seek_grail(kid) is False  # only one trial
    services.shrubbery.judge_shrubbery(kid, "SH2")
    assert services.registry.may_seek_grail(kid) is True   # both passed


# ---- Registry: progress isolation ----

def test_progress_isolation():
    kid = _verify_lancelot()
    services.bridgekeeper.judge_crossing(kid, "Sir Lancelot", "to seek the Holy Grail", "blue")
    # Sir Robin's progress is untouched by Lancelot's crossing.
    robin = services.registry.verify_knight("Sir Robin", "to seek the Holy Grail")["knight"]["id"]
    assert services.registry.quest_progress(robin)["bridge"] is False
    assert services.registry.quest_progress(kid)["bridge"] is True
