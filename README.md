# promise-driven-agentic-kit

**A portable kit for building agentic systems as model-checked, Promise-Theoretic contracts — not prose prompts.**

An LLM is an autonomous, stochastic agent: you cannot command it, you can only
elicit a *promise* and then *assess* whether it was kept. This kit packages a
methodology that takes that fact seriously. Each agent's instructions are a
single contract document that is read three ways:

- a **FizzBee state machine** a model checker proves can never reach a bad state,
- a **Promise Theory manifest** of what the agent offers (`+`) and uses (`−`), and
- the **natural-language guidance** the model follows at runtime.

Structural guarantees are *proven* offline and *re-enforced* in code; judgment
stays in prose. The reference implementation is **Penny**, an SAP Concur expense
agent — used throughout the docs as the worked example.

## Start here

📄 **[The Promise-Driven Agent](docs/why-promise-driven-agents.md)** — the whitepaper:
why this approach exists, the Promise Theory foundation, and an eight-point rubric
for agentic systems. If you read one thing, read this.

## What's in the kit

| Folder | Purpose | Link |
| --- | --- | --- |
| `docs` | The methodology: the whitepaper plus two companion articles ([contracts-not-prompts](docs/contracts-not-prompts.md) and the [Promise Theory architecture analysis](docs/penny-promise-theory-architecture.md)). | [docs/](docs/) |
| `schema` | XSD schemas defining and validating the two contract-document formats — `agent_*.xml` (LLM agents) and `manifest_*.xml` (non-LLM agents). Each is heavily annotated and doubles as a spec. | [schema/](schema/) |
| `skeleton` | A [copier](https://copier.readthedocs.io/) template that scaffolds a brand-new contract-driven agent repo (uv-managed) with a working toy "barista" agent and the full three-part verification gate — green out of the box. | [skeleton/](skeleton/) |
| `skills` | An agentic-coding skill (`authoring-agent-contracts`) that walks an engineer through writing, validating, and model-checking a new contract. Repos scaffolded from `skeleton/` already bundle it under `.claude/skills/`; for other projects, copy it into your `.claude/skills/` (or `~/.claude/skills/`). | [skills/](skills/) |
| `examples` | A complete, **runnable** worked example: a live ADK-backed clinic-appointment agent (6 agents) whose safety invariants are both model-checked and code-enforced. The best place to see the whole methodology at once — you can model-check it and talk to it. | [examples/](examples/) |

## Quick start — scaffold a new agent

```bash
# one-time: install the tooling
uv tool install copier                 # or: pipx install copier
brew tap fizzbee-io/fizzbee && brew install fizzbee   # the model checker

# generate a new repo from the skeleton
copier copy <path-to-this-repo>/skeleton my-new-agent
cd my-new-agent
uv sync
make gate     # tests + model-check + promise-graph verification — green immediately
```

See [skeleton/README.md](skeleton/README.md) for details, and each generated
project's own `GETTING-STARTED.md`.

## Validate a contract against the schema

```bash
xmllint --noout --schema schema/agent-contract.xsd  your-agent-contract.xml
xmllint --noout --schema schema/agent-manifest.xsd  your-agent-manifest.xml
```

## Provenance & license

Extracted from the Penny project, where the methodology was developed. Licensed
under [Apache-2.0](LICENSE).

---

*This is a living kit. Planned additions include an authoring skill for agentic
coding tools. Contributions and corrections welcome.*
