# promise-driven-agentic-kit

**A portable methodology kit for building agentic systems from model-checked,
Promise-Theoretic contracts rather than relying on prose prompts alone.**

An LLM is an autonomous, stochastic agent: you cannot command it, you can only
elicit a *promise* and then *assess* whether it was kept. This kit packages a
methodology that takes that fact seriously.

Each LLM agent is described by one XML **agent contract** with six coordinated
sections. Its `<verifiable-behavior>` section contains the FizzBee state machine;
`<promises>` declares what the agent offers (`+`), uses (`−`), and depends on;
the remaining sections carry purpose, runtime guidance, enforcement traceability,
and response language. The whole artifact is the contract.

The same contract moves through a **Design → Build → Run** lifecycle:

- **Design:** validate the XML, model-check reachable behavior, and verify the
  Promise Theory graph.
- **Build:** use the verified contract to implement agent wiring, independent
  Python enforcement, and matching tests.
- **Run:** give the whole contract to the LLM, then reassess consequential
  operations against authoritative state before committing them.

Model checking proves the *specified behavior model*, not the stochastic LLM or
the Python implementation. Deterministic enforcement and its test twin close that
gap at the software boundary; judgment remains in prose where it belongs.

## Start here

- **See the method:** [From Contract to Enforcement](docs/contract-assessment/README.md)
  maps all six XML sections through Design, Build, Run, Python assessment, and
  executable evidence.
- **Author a contract:** [Authoring an Agent Contract](docs/authoring-workflow/README.md)
  walks from an intended promise to XML, Python enforcement, tests, and a green gate.
- **Understand the theory:** [The Promise-Driven Agent](docs/why-promise-driven-agents.md)
  develops the Promise Theory foundation and an eight-point rubric for agentic
  systems.
- **Build with the kit:** [Scaffold a new agent](skeleton/README.md) or inspect the
  complete [worked examples](examples/).

## What's in the kit

| Folder | Purpose | Link |
| --- | --- | --- |
| `docs` | The methodology, practical authoring and assurance guides, illustrations, whitepaper, architecture analysis, and draft Medium series. | [Documentation map](docs/README.md) |
| `schema` | XSD schemas defining and validating the two contract-document formats — `agent_*.xml` (LLM agents) and `manifest_*.xml` (non-LLM agents). Each is heavily annotated and doubles as a spec. | [schema/](schema/) |
| `skeleton` | A [copier](https://copier.readthedocs.io/) template that scaffolds a brand-new contract-driven agent repo (uv-managed) with a working toy "barista" agent and the full three-part verification gate — green out of the box. | [skeleton/](skeleton/) |
| `skills` | An agentic-coding skill (`authoring-agent-contracts`) that walks an engineer through writing, validating, and model-checking a new contract. Repos scaffolded from `skeleton/` already bundle it under `.claude/skills/`; for other projects, copy it into your `.claude/skills/` (or `~/.claude/skills/`). | [skills/](skills/) |
| `examples` | Complete, **runnable** worked examples whose distinct contracts apply the same verification and enforcement architecture across different domains and frameworks: **clinic-appointments** (Google ADK) and **holy-grail-trials** (Pydantic AI). | [examples/](examples/) |

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

## License

Licensed under [Apache-2.0](LICENSE).

---

*This is a living methodology kit. Contributions and corrections are welcome.*
