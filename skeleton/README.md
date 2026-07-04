# Skeleton — a copier template for a new contract-driven agent

This folder is a [copier](https://copier.readthedocs.io/) template that scaffolds a
brand-new repository laid out like Penny: an `agent_contracts/` directory of
model-checked contract documents, the loader/verifier machinery that reads them,
a working **toy agent** (a "barista"), and the three-part CI gate — all wired to
`uv` and ready to run.

It is the "how do I start one of these?" companion to the rest of the [Contract
Kit](../README.md): [`schema/`](../schema/) defines the contract format and
[`docs/`](../docs/) explains the methodology.

## Generate a new project

```bash
# one-time: install the tools
uv tool install copier          # or: pipx install copier

# scaffold a new repo from this template
copier copy <path-to-promise-driven-agentic-kit>/skeleton my-new-agent
cd my-new-agent

# set up and prove the gate is green
uv sync
make gate
```

`copier` will prompt for the project name, package name, author, and Python
version (see [`copier.yml`](copier.yml)). A freshly generated repo is
**self-validating**: its toy contracts pass the XSD schemas and model-check
under `fizz`, so `make gate` is green immediately — that is the proof the
template works.

## What you get

```
my-new-agent/
├── GETTING-STARTED.md          # environment + fizz install + the gate
├── pyproject.toml              # uv-managed, Python ≥ 3.13
├── Makefile                    # `make gate` = tests + fizz-check + promise-check
├── schema/                     # vendored copy of the kit's XSDs
├── agent_contracts/
│   ├── agent_barista.xml       # toy LLM contract (never dispense before payment)
│   └── manifest_machine.xml    # toy non-LLM manifest (the espresso machine)
├── src/<package>/contracts/    # contract loader, fizz_check, promise loader
├── scripts/                    # verify_fizzbee_contracts.py, verify_promise_graph.py
├── tests/                      # schema validation + model-check gate
└── .claude/skills/authoring-agent-contracts/   # the authoring skill, ready to use in-repo
```

The toy barista exists to be replaced: it demonstrates the flagship pattern
(*a safety invariant proven by the model checker and re-enforced in code*) at
trivial scale. Rename it, gut it, and write your own agent — the machinery
around it is what you keep.

## Keeping the vendored schemas in sync

`template/schema/` is a **copy** of [`../schema/`](../schema/) so that generated
repos are standalone. If you evolve the canonical schemas in the kit, re-copy
them here:

```bash
cp ../schema/*.xsd template/schema/
```

The same applies to the bundled authoring skill — `template/.claude/skills/authoring-agent-contracts/`
is a copy of [`../skills/authoring-agent-contracts/`](../skills/authoring-agent-contracts/).
Re-copy it when the canonical skill changes:

```bash
rm -rf template/.claude/skills/authoring-agent-contracts
cp -R ../skills/authoring-agent-contracts template/.claude/skills/
```
