# Getting started — the Trials of the Holy Grail

Two layers, set up independently:

- **The offline gate** (contracts, model-checking, promise graph + card
  entailment, enforcement tests) needs only Python + `uv` + `fizz`. **No Google
  credentials.**
- **The live agent** additionally needs **Vertex AI** via a Google
  **service-account JSON** (not an API key). The runtime is **Pydantic AI**
  talking to Gemini on Vertex.

## 1. Prerequisites & the offline gate

| Tool | Why | Install |
| --- | --- | --- |
| Python 3.13+ | runtime | `uv python install 3.13` |
| **uv** | env + deps | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **fizz** (FizzBee) | model-checks contracts | `brew tap fizzbee-io/fizzbee && brew install fizzbee` |

```bash
uv sync
make gate          # GREEN with no credentials at all
```

`make gate` runs schema validation, `fizz` model-check of the three LLM
contracts, promise-graph verification **including the superagent card-entailment
check**, and the enforcement-twin unit tests.

## 2. Live agent — Vertex AI via a service account

Auth uses **Application Default Credentials from a service-account JSON** (same
convention as the clinic example):

| Variable | Purpose | Notes |
| --- | --- | --- |
| `GOOGLE_APPLICATION_CREDENTIALS` | path to the service-account JSON | **required** |
| `GOOGLE_CLOUD_PROJECT` | GCP project id | auto-derived from the SA file if unset |
| `GOOGLE_CLOUD_LOCATION` | Vertex region | defaults to `global` |
| `GOOGLE_GENAI_USE_VERTEXAI` | use Vertex, not the Gemini API | set to `True` automatically |
| `GRAIL_AGENT_MODEL` | model id | defaults to `gemini-3.5-flash` |

The service account needs **Vertex AI User** (`roles/aiplatform.user`) on a
project with the Vertex AI API enabled.

```bash
cp .env.example .env        # then edit, or just export:
export GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json

uv run python -m grail smoke      # scripted: verify -> Gorge -> cross -> "Ni!" -> pass -> Grail
uv run python -m grail chat       # interactive REPL (Rich)
uv run python -m grail once "I am Sir Lancelot; my quest is to seek the Holy Grail."
```

### Try it

Seed knights: **Sir Lancelot** (quest "to seek the Holy Grail", favourite colour
*blue*, shrubbery budget 50), **Sir Robin** (*yellow*, budget 25), **Arthur, King
of the Britons** (*red*, budget 80). Answer the Bridgekeeper's favourite-colour
question wrong and you're in the Gorge. Offer the ornate topiary (90) on
Lancelot's budget (50) and you'll hear "Ni!"; offer the lovely laurel (40) and
you'll pass.

## How this differs from the clinic example

Same contracts, same `services/` enforcement, same gate — the **only** real
difference is `src/grail/agents/build.py` (Pydantic AI + agent delegation)
versus the clinic's ADK `build.py`. That's framework-independence in one file.

## The rule that makes it safe

Model-checking proves the *contract* cannot reach a bad state (it caught a real
bug in the Marshal's first draft — see the README). It does **not** prove the
LLM obeys; that's why every invariant also has a code twin in
`src/grail/services/` with a test.
