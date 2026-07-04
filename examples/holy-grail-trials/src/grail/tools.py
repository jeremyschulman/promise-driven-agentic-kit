"""Tool functions — thin wrappers over the pure-Python services.

Bound to agents by name (each agent's ``<tools>`` list). They resolve the active
knight and delegate to ``grail.services``, whose code keeps the invariants.
Returns are plain JSON-serializable dicts. References ``services.<x>`` at call
time so a test's ``services.reset()`` is picked up.
"""

from __future__ import annotations

from grail import services


def _active() -> str | None:
    return services.store.active_knight_id


# ---- Marshal ----
def verify_knight(name: str = "", quest: str = "") -> dict:
    """Verify a seeker as a Knight of the Round Table (name + professed quest) and set them active."""
    return services.registry.verify_knight(name=name or None, quest=quest or None)


def get_quest_progress() -> dict:
    """Which trials the verified knight has passed, and whether they may seek the Grail."""
    kid = _active()
    if kid is None:
        return services.registry.get_active()
    return services.registry.quest_progress(kid)


# ---- shared / trial leaf tools ----
def get_active_knight() -> dict:
    """The verified knight this trial acts for (name, quest, favourite colour, shrubbery budget)."""
    return services.registry.get_active()


def get_bridge_questions() -> dict:
    """The Bridgekeeper's three questions."""
    return services.bridgekeeper.get_questions()


def judge_crossing(name: str = "", quest: str = "", favourite_colour: str = "") -> dict:
    """Judge the knight's three answers in code; records a crossing only if all three are correct."""
    kid = _active()
    if kid is None:
        return services.registry.get_active()
    return services.bridgekeeper.judge_crossing(kid, name=name, quest=quest, favourite_colour=favourite_colour)


def browse_shrubberies() -> dict:
    """List Roger the Shrubber's shrubberies (name, niceness, price) and the niceness bar."""
    return services.shrubbery.list_shrubberies()


def judge_shrubbery(shrubbery_id: str) -> dict:
    """Judge a chosen shrubbery in code; grants Ni passage only if nice enough AND within the knight's budget."""
    kid = _active()
    if kid is None:
        return services.registry.get_active()
    return services.shrubbery.judge_shrubbery(kid, shrubbery_id)
