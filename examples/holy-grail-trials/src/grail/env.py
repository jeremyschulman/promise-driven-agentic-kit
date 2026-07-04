"""Google / Vertex AI environment bootstrap (service-account auth, not an API key).

Same convention as the clinic example: read ``GOOGLE_APPLICATION_CREDENTIALS``,
derive ``GOOGLE_CLOUD_PROJECT`` from the service-account file if unset, default
the location, and turn on the Vertex backend. Only ``project_id`` is read from
the credentials file.
"""

from __future__ import annotations

import json
import os

_DEFAULT_LOCATION = "global"  # current Gemini models serve from the global Vertex endpoint
_DEFAULT_MODEL = "gemini-3.5-flash"
_MODEL_ENV = "GRAIL_AGENT_MODEL"


def init_google_env() -> None:
    cred = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if cred and os.path.exists(cred) and not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        try:
            with open(cred, encoding="utf-8") as fh:
                project_id = json.load(fh).get("project_id")
            if project_id:
                os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        except (OSError, ValueError):
            pass
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", _DEFAULT_LOCATION)
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


def resolve_model() -> str:
    return os.environ.get(_MODEL_ENV) or _DEFAULT_MODEL


def require_google_env() -> list[str]:
    problems: list[str] = []
    cred = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred:
        problems.append("GOOGLE_APPLICATION_CREDENTIALS is not set (path to service-account JSON).")
    elif not os.path.exists(cred):
        problems.append(f"GOOGLE_APPLICATION_CREDENTIALS points to a missing file: {cred}")
    if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        problems.append("GOOGLE_CLOUD_PROJECT is not set and could not be derived from the credentials file.")
    return problems
