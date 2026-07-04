"""In-memory world for the Trials of the Holy Grail — deterministic, no deps.

Knights of the Round Table (each with a professed quest, a true favourite
colour, and a shrubbery budget), the Bridgekeeper's three questions, and Roger
the Shrubber's market. Progress (which trials each knight has passed) lives here,
keyed per knight.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Knight:
    id: str
    name: str
    quest: str
    favourite_colour: str
    shrubbery_budget: int  # "not too expensive" is measured against this


@dataclass
class Shrubbery:
    id: str
    name: str
    niceness: int  # 1..10
    price: int


# A shrubbery must be at least this nice to satisfy the Knights Who Say Ni.
NICENESS_BAR = 5

# The Bridgekeeper's canonical three (the airspeed-of-a-swallow line is his flourish).
BRIDGE_QUESTIONS = [
    "What... is your name?",
    "What... is your quest?",
    "What... is your favourite colour?",
]


class GrailStore:
    def __init__(self) -> None:
        self.knights: dict[str, Knight] = {
            "K1": Knight("K1", "Sir Lancelot", "to seek the Holy Grail", "blue", 50),
            "K2": Knight("K2", "Sir Robin", "to seek the Holy Grail", "yellow", 25),
            "K3": Knight("K3", "Arthur, King of the Britons", "to seek the Holy Grail", "red", 80),
        }
        self.shrubberies: dict[str, Shrubbery] = {
            "SH1": Shrubbery("SH1", "a modest sprig", 2, 10),
            "SH2": Shrubbery("SH2", "a lovely laurel", 8, 40),
            "SH3": Shrubbery("SH3", "an ornate topiary", 9, 90),
            "SH4": Shrubbery("SH4", "a sad little twig", 1, 5),
        }
        self.niceness_bar = NICENESS_BAR
        self.questions = list(BRIDGE_QUESTIONS)
        # The verified knight for this session.
        self.active_knight_id: str | None = None
        # Per-knight trial progress (isolated). {knight_id: {"bridge": bool, "ni": bool}}
        self.progress: dict[str, dict[str, bool]] = {}
