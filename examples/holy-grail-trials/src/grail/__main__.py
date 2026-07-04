"""Run the Trials of the Holy Grail agent (Pydantic AI on Vertex).

Usage:
    python -m grail chat     # interactive REPL (Rich-rendered on a TTY)
    python -m grail smoke    # scripted multi-turn conversation (a quick live check)
    python -m grail demo     # scripted arc for recording (Rich)
    python -m grail once "your message"

Requires Google/Vertex env (see GETTING-STARTED.md): a service-account JSON in
GOOGLE_APPLICATION_CREDENTIALS.
"""

from __future__ import annotations

import asyncio
import sys


def _make_agent():
    from grail.agents.build import build_grail_agent
    from grail.env import init_google_env, require_google_env

    init_google_env()
    problems = require_google_env()
    if problems:
        print("Environment not ready:")
        for p in problems:
            print(f"  - {p}")
        print("See GETTING-STARTED.md.")
        raise SystemExit(2)
    return build_grail_agent()


async def _turn(agent, text: str, history):
    result = await agent.run(text, message_history=history)
    return result.output, result.all_messages()


# ---- interactive ----
async def chat() -> None:
    agent = _make_agent()
    if sys.stdout.isatty():
        await _chat_rich(agent)
    else:
        await _chat_plain(agent)


async def _chat_rich(agent) -> None:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.prompt import Prompt

    console = Console()
    console.print("[bold]The Trials of the Holy Grail[/]  [dim](type 'exit' to quit)[/]\n")
    history = None
    while True:
        try:
            text = await asyncio.to_thread(Prompt.ask, "[bold cyan]seeker[/]")
        except (EOFError, KeyboardInterrupt):
            break
        if text.strip().lower() in {"exit", "quit"}:
            break
        with console.status("[dim]the Marshal considers…[/]", spinner="dots"):
            reply, history = await _turn(agent, text, history)
        console.print("[bold green]marshal[/]")
        console.print(Markdown(reply))
        console.print()


async def _chat_plain(agent) -> None:
    print("The Trials of the Holy Grail. Type 'exit' to quit.\n")
    history = None
    while True:
        try:
            text = await asyncio.to_thread(input, "seeker> ")
        except (EOFError, KeyboardInterrupt):
            break
        if text.strip().lower() in {"exit", "quit"}:
            break
        reply, history = await _turn(agent, text, history)
        print(f"marshal> {reply}\n")


# ---- scripted / one-shot ----
async def once(text: str) -> None:
    agent = _make_agent()
    reply, _ = await _turn(agent, text, None)
    print(reply)


_DEMO_TURNS = [
    "I am Sir Lancelot, and my quest is to seek the Holy Grail.",
    "I shall brave the Bridge of Death. My name is Sir Lancelot, my quest is to seek the Holy Grail, and my favourite colour is... green.",
    "Blue! My favourite colour is blue!",
    "Now I approach the Knights Who Say Ni. What shrubberies are on offer?",
    "I present the ornate topiary.",
    "Then I offer the lovely laurel instead.",
    "Both trials are behind me — may I now seek the Holy Grail?",
]


async def smoke() -> None:
    agent = _make_agent()
    history = None
    for t in _DEMO_TURNS:
        print(f"\n>>> {t}")
        reply, history = await _turn(agent, t, history)
        print(f"<<< {reply}")


async def demo() -> None:
    from rich.console import Console
    from rich.markdown import Markdown

    agent = _make_agent()
    console = Console()
    console.print("[bold]The Trials of the Holy Grail[/]  [dim](demo)[/]\n")
    history = None
    for t in _DEMO_TURNS:
        console.print(f"[bold cyan]seeker[/]: {t}")
        with console.status("[dim]the Marshal considers…[/]", spinner="dots"):
            reply, history = await _turn(agent, t, history)
        console.print("[bold green]marshal[/]")
        console.print(Markdown(reply))
        console.print()
        await asyncio.sleep(1.2)


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "chat"
    if mode == "smoke":
        asyncio.run(smoke())
    elif mode == "demo":
        asyncio.run(demo())
    elif mode == "once":
        asyncio.run(once(" ".join(sys.argv[2:]) or "hello"))
    else:
        asyncio.run(chat())


if __name__ == "__main__":
    main()
