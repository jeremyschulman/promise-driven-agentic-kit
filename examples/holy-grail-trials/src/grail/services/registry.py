"""Round Table Registry — knight identity, the active knight, and trial progress.

Enforces progress isolation: a knight's progress is keyed to that knight and
never leaks or writes across knights.
"""

from __future__ import annotations

from .refusals import ok, refusal
from .store import GrailStore


class RoundTableRegistry:
    def __init__(self, store: GrailStore) -> None:
        self._store = store

    def verify_knight(self, name: str | None = None, quest: str | None = None) -> dict:
        """Match a seeker to an enrolled Knight of the Round Table and set active.

        Requires name AND a professed quest that matches the roster. Returns a
        refusal when no knight matches — the Marshal turns them away.
        """
        if not name or not quest:
            return refusal(
                "identity_incomplete",
                "knight_verified",
                "Declare both your name and your quest.",
            )
        n, q = name.strip().lower(), quest.strip().lower()
        for k in self._store.knights.values():
            if k.name.lower() == n and k.quest.lower() == q:
                self._store.active_knight_id = k.id
                self._store.progress.setdefault(k.id, {"bridge": False, "ni": False})
                return ok(knight={"id": k.id, "name": k.name, "quest": k.quest})
        return refusal(
            "not_a_knight",
            "knight_verified",
            "No such Knight of the Round Table is enrolled with that quest.",
        )

    def get_active(self) -> dict:
        kid = self._store.active_knight_id
        if kid is None:
            return refusal("no_active_knight", "knight_verified", "No knight is verified yet.")
        k = self._store.knights[kid]
        return ok(knight={"id": k.id, "name": k.name, "quest": k.quest,
                          "favouriteColour": k.favourite_colour, "shrubberyBudget": k.shrubbery_budget})

    def record_trial(self, knight_id: str, trial: str) -> dict:
        """Record a trial as passed for exactly this knight (isolation)."""
        if trial not in ("bridge", "ni"):
            return refusal("unknown_trial", "trial_valid", f"No such trial: {trial}.")
        if knight_id not in self._store.knights:
            return refusal("unknown_knight", "knight_verified", "No such knight.")
        self._store.progress.setdefault(knight_id, {"bridge": False, "ni": False})[trial] = True
        return ok(recorded=trial)

    def quest_progress(self, knight_id: str) -> dict:
        p = self._store.progress.get(knight_id, {"bridge": False, "ni": False})
        return ok(
            bridge=p["bridge"],
            ni=p["ni"],
            maySeekGrail=(p["bridge"] and p["ni"]),
            remaining=[t for t in ("bridge", "ni") if not p[t]],
        )

    def may_seek_grail(self, knight_id: str) -> bool:
        p = self._store.progress.get(knight_id, {"bridge": False, "ni": False})
        return p["bridge"] and p["ni"]
