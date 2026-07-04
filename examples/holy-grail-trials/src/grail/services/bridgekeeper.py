"""Bridgekeeper's Questions service — judges the three answers in code.

Keeps NoCrossingWithWrongAnswer: a crossing is recorded ONLY when all three
answers match the knight's registry record. The seeker asserting confidence
("Blue— no, yellow!") does not make an answer correct.
"""

from __future__ import annotations

from .refusals import ok, refusal
from .registry import RoundTableRegistry
from .store import GrailStore


class Bridgekeeper:
    def __init__(self, store: GrailStore, registry: RoundTableRegistry) -> None:
        self._store = store
        self._registry = registry

    def get_questions(self) -> dict:
        return ok(questions=list(self._store.questions))

    def judge_crossing(
        self,
        knight_id: str,
        name: str = "",
        quest: str = "",
        favourite_colour: str = "",
    ) -> dict:
        """Judge the three answers; record the crossing only if all are correct."""
        knight = self._store.knights.get(knight_id)
        if knight is None:
            return refusal("unknown_knight", "knight_verified", "No such knight.")
        # ThreeQuestionsBeforeCrossing: all three must actually be answered.
        if not (name.strip() and quest.strip() and favourite_colour.strip()):
            return ok(crossed=False, reason="All three questions must be answered.")
        correct = (
            name.strip().lower() == knight.name.lower()
            and quest.strip().lower() == knight.quest.lower()
            and favourite_colour.strip().lower() == knight.favourite_colour.lower()
        )
        if not correct:
            return ok(crossed=False, reason="That is the wrong answer. Into the Gorge!")
        self._registry.record_trial(knight_id, "bridge")
        return ok(crossed=True)
