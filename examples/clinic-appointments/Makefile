.PHONY: gate test fizz-check promise-check help

help:
	@echo "Targets: gate (all) | test | fizz-check | promise-check"

gate: test fizz-check promise-check
	@echo "Gate passed."

test:
	uv run pytest -q

fizz-check:
	uv run python scripts/verify_fizzbee_contracts.py

promise-check:
	uv run python scripts/verify_promise_graph.py
