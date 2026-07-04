"""Shrubbery Market (Roger the Shrubber) — judges acceptability in code.

Keeps ShrubberyMustBeAcceptable: passage is recorded ONLY when a chosen
shrubbery is nice enough (>= the niceness bar) AND within the knight's budget
("one that looks nice, and not too expensive").
"""

from __future__ import annotations

from .refusals import ok, refusal
from .registry import RoundTableRegistry
from .store import GrailStore


class ShrubberyMarket:
    def __init__(self, store: GrailStore, registry: RoundTableRegistry) -> None:
        self._store = store
        self._registry = registry

    def list_shrubberies(self) -> dict:
        return ok(
            shrubberies=[
                {"id": s.id, "name": s.name, "niceness": s.niceness, "price": s.price}
                for s in self._store.shrubberies.values()
            ],
            nicenessBar=self._store.niceness_bar,
        )

    def judge_shrubbery(self, knight_id: str, shrubbery_id: str) -> dict:
        """Judge a chosen shrubbery; record Ni passage only if acceptable."""
        knight = self._store.knights.get(knight_id)
        if knight is None:
            return refusal("unknown_knight", "knight_verified", "No such knight.")
        sh = self._store.shrubberies.get(shrubbery_id)
        if sh is None:
            return refusal("unknown_shrubbery", "shrubbery_acceptable", "No such shrubbery.")
        nice = sh.niceness >= self._store.niceness_bar
        affordable = sh.price <= knight.shrubbery_budget
        if not (nice and affordable):
            reason = "it is not nice enough" if not nice else "it is too expensive"
            return ok(acceptable=False, reason=reason,
                      shrubbery={"id": sh.id, "name": sh.name, "niceness": sh.niceness, "price": sh.price})
        self._registry.record_trial(knight_id, "ni")
        return ok(acceptable=True,
                  shrubbery={"id": sh.id, "name": sh.name, "niceness": sh.niceness, "price": sh.price})
