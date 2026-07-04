#!/usr/bin/env python3
"""Model-check the FizzBee contract embedded in every ``agent_*.xml`` document.

For each contract this extracts the ``<fizzbee>`` block, writes it to a temp
``.fizz`` file, runs the ``fizz`` model checker, and reports PASS/FAIL. Exit code
is non-zero if any contract fails (or if ``fizz`` is missing), so it can gate CI.

Usage:
    python scripts/verify_fizzbee_contracts.py [--fizz-bin PATH] [--docs-dir DIR]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running directly (without installing the package) by putting src/ on the path.
_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from grail.contracts.contract_doc import iter_contract_docs  # noqa: E402
from grail.contracts.fizz_check import fizz_available, model_check  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fizz-bin", default="fizz", help="path to the fizz binary")
    parser.add_argument("--docs-dir", default=None, help="path to agent_contracts/")
    args = parser.parse_args(argv)

    if not fizz_available(args.fizz_bin):
        print(
            f"ERROR: '{args.fizz_bin}' not found on PATH. Install FizzBee "
            "(see GETTING-STARTED.md): brew tap fizzbee-io/fizzbee && brew install fizzbee",
            file=sys.stderr,
        )
        return 2

    total = 0
    passed = 0
    for doc in iter_contract_docs(args.docs_dir):
        total += 1
        result = model_check(doc, fizz_bin=args.fizz_bin)
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {doc.workflow_id}")
        if result.passed:
            passed += 1
        else:
            print(result.output)

    print(f"{passed}/{total} contract(s) passed model checking.")
    return 0 if total > 0 and passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
