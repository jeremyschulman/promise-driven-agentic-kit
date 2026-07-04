# Getting started — Clinic Appointments

Two layers, set up independently:

- **The offline gate** (contracts, model-checking, promise graph, enforcement
  tests) needs only Python + `uv` + `fizz`. **No Google credentials.**
- **The live agent** additionally needs **Vertex AI** access via a Google
  **service-account JSON** (not an API key).

## 1. Prerequisites

| Tool | Why | Install |
| --- | --- | --- |
| Python 3.13+ | runtime | `uv python install 3.13` |
| **uv** | env + deps | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **fizz** (FizzBee) | model-checks contracts | `brew tap fizzbee-io/fizzbee && brew install fizzbee` |

```bash
uv sync
make gate          # should be GREEN with no credentials at all
```

`make gate` runs: schema validation, `fizz` model-check of all three LLM
contracts, promise-graph verification, and the enforcement-twin unit tests.

## 2. Live agent — Vertex AI via a service account

Auth uses **Application Default Credentials from a service-account JSON**. The
required Google environment variables (the standard Vertex convention):

| Variable | Purpose | Notes |
| --- | --- | --- |
| `GOOGLE_APPLICATION_CREDENTIALS` | path to the service-account JSON | **required** |
| `GOOGLE_CLOUD_PROJECT` | GCP project id | auto-derived from the SA file's `project_id` if unset |
| `GOOGLE_CLOUD_LOCATION` | Vertex region | defaults to `global` (where current Gemini models are served) |
| `GOOGLE_GENAI_USE_VERTEXAI` | use Vertex, not the Gemini API | set to `True` automatically |
| `CLINIC_AGENT_MODEL` | model id | defaults to `gemini-3.5-flash` |

The service account needs the **Vertex AI User** role (`roles/aiplatform.user`)
on a project with the **Vertex AI API** enabled.

```bash
cp .env.example .env        # then edit, OR just export the vars:
export GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json
# GOOGLE_CLOUD_PROJECT is derived from the file; GOOGLE_CLOUD_LOCATION defaults to global.

uv run python -m clinic smoke     # scripted: verify identity -> list -> start a booking
uv run python -m clinic chat      # interactive REPL  (type 'exit' to quit)
uv run python -m clinic once "I'm Ada Lovelace, DOB 1990-01-01. What do I have booked?"
```

> **Never commit the service-account JSON.** Keep it outside the repo (e.g. in
> `~/.config/gcloud/`) and reference it by path. `.gitignore` also blocks `.env`
> and stray `*-service-account.json` files as a backstop.

### Try it

The seed data has two patients — **Ada Lovelace** (DOB `1990-01-01`, plan
covers dermatology) and **Grace Hopper** (DOB `1985-05-05`) — providers Dr. Chen
(dermatology) and Dr. Patel (cardiology), and one existing appointment for Ada.
Ask to book a cardiology visit as Ada to watch the eligibility gate offer
self-pay; ask to cancel Grace's appointment as Ada to watch ownership enforcement.

## 3. `adk web` (optional)

ADK's dev UI works too:

```bash
uv run adk web src/clinic
```

## The rule that makes it safe

Model-checking proves the *contract* cannot reach a bad state; it does **not**
prove the LLM obeys the contract. That's why every invariant also has a code
twin in `src/clinic/services/` with a test. If you extend this agent, keep that
pairing — see the bundled authoring skill (`.claude/skills/authoring-agent-contracts`).
