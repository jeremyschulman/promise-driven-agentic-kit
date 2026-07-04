"""Run the clinic agent.

Usage:
    python -m clinic chat     # interactive REPL (default)
    python -m clinic smoke    # scripted multi-turn conversation (a quick live check)
    python -m clinic once "your message here"

Requires Google/Vertex env (see GETTING-STARTED.md): a service-account JSON in
GOOGLE_APPLICATION_CREDENTIALS. `adk web` also works — point it at src/clinic.
"""

from __future__ import annotations

import asyncio
import sys

APP = "clinic"
USER = "cli-user"
SESSION = "cli-session"


async def _make_runner():
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService

    from clinic.agents.build import build_clinic_agent
    from clinic.env import init_google_env, require_google_env

    init_google_env()
    problems = require_google_env()
    if problems:
        print("Environment not ready:")
        for p in problems:
            print(f"  - {p}")
        print("See GETTING-STARTED.md.")
        raise SystemExit(2)

    agent = build_clinic_agent()
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP, user_id=USER, session_id=SESSION)
    return Runner(agent=agent, app_name=APP, session_service=session_service)


async def _turn(runner, text: str) -> str:
    from google.genai import types

    message = types.Content(role="user", parts=[types.Part(text=text)])
    reply = ""
    async for event in runner.run_async(user_id=USER, session_id=SESSION, new_message=message):
        if event.is_final_response() and event.content and event.content.parts:
            reply = "".join(p.text or "" for p in event.content.parts)
    return reply


async def chat() -> None:
    runner = await _make_runner()
    print("Clinic appointment agent. Type 'exit' to quit.\n")
    while True:
        try:
            text = await asyncio.to_thread(input, "you> ")
        except (EOFError, KeyboardInterrupt):
            break
        if text.strip().lower() in {"exit", "quit"}:
            break
        print(f"penny-clinic> {await _turn(runner, text)}\n")


async def once(text: str) -> None:
    runner = await _make_runner()
    print(await _turn(runner, text))


async def smoke() -> None:
    """A scripted conversation that exercises verify -> list -> book flow live."""
    runner = await _make_runner()
    turns = [
        "Hi! I'm Ada Lovelace, date of birth 1990-01-01.",
        "What appointments do I currently have?",
        "I'd like to book a dermatology visit with Dr. Chen. What's open?",
    ]
    for t in turns:
        print(f"\n>>> {t}")
        print(f"<<< {await _turn(runner, t)}")


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "chat"
    if mode == "smoke":
        asyncio.run(smoke())
    elif mode == "once":
        asyncio.run(once(" ".join(sys.argv[2:]) or "hello"))
    else:
        asyncio.run(chat())


if __name__ == "__main__":
    main()
