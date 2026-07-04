"""Every LLM-agent contract model-checks cleanly under ``fizz``.

Skipped (loudly) when ``fizz`` is not installed — but the authoritative gate,
``scripts/verify_fizzbee_contracts.py``, fails hard in that case, so CI still
catches a missing model checker.
"""

from __future__ import annotations

import pytest

from grail.contracts.contract_doc import iter_contract_docs
from grail.contracts.fizz_check import fizz_available, model_check


@pytest.mark.skipif(
    not fizz_available(),
    reason="fizz not installed; run scripts/verify_fizzbee_contracts.py after installing FizzBee",
)
def test_all_contracts_model_check() -> None:
    docs = list(iter_contract_docs())
    assert docs, "expected at least one agent_*.xml contract"
    for doc in docs:
        result = model_check(doc)
        assert result.passed, f"{doc.workflow_id} failed model checking:\n{result.output}"
