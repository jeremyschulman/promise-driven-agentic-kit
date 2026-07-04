"""Pure-Python services for the Trials — the deterministic domain + enforcement.

No framework, no LLM, no network. Every invariant the contracts declare is kept
here in code, so the full gate runs green offline. ``reset()`` gives tests a
fresh world.
"""

from __future__ import annotations

from .bridgekeeper import Bridgekeeper
from .refusals import ok, refusal
from .registry import RoundTableRegistry
from .shrubbery import ShrubberyMarket
from .store import GrailStore

__all__ = [
    "GrailStore",
    "RoundTableRegistry",
    "Bridgekeeper",
    "ShrubberyMarket",
    "ok",
    "refusal",
    "store",
    "registry",
    "bridgekeeper",
    "shrubbery",
    "reset",
]

store = GrailStore()
registry = RoundTableRegistry(store)
bridgekeeper = Bridgekeeper(store, registry)
shrubbery = ShrubberyMarket(store, registry)


def reset() -> None:
    global store, registry, bridgekeeper, shrubbery
    store = GrailStore()
    registry = RoundTableRegistry(store)
    bridgekeeper = Bridgekeeper(store, registry)
    shrubbery = ShrubberyMarket(store, registry)
