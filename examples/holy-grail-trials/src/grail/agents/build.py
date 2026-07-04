"""Build Pydantic AI agents from the contract documents.

Same contracts as any agent in this kit; only the runtime shell differs from the
clinic's ADK. Each agent's ``description`` and bound ``tools`` come from its
``<promises>`` manifest, and the whole XML is the agent's ``instructions``.

Composition uses Pydantic AI **agent delegation**: the Marshal calls each trial
agent through a delegation tool (there is no built-in "sub-agent" primitive) —
the promise graph is identical, only the wiring changes. Typed trial verdicts
would be a natural next step via ``output_type``; here trials return text the
Marshal relays.

Importing this module requires ``pydantic-ai`` + ``google-genai``; the services
and the offline gate do not.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET

from pydantic_ai import Agent, RunContext

from grail import tools as tools_mod
from grail.contracts.contract_doc import load_contract_doc
from grail.env import resolve_model


class AgentConstructionError(RuntimeError):
    """Raised when a contract names a tool that does not exist."""


def _make_model():
    from google import genai
    from pydantic_ai.models.google import GoogleModel
    from pydantic_ai.providers.google import GoogleProvider

    client = genai.Client(
        vertexai=True,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
    )
    return GoogleModel(resolve_model(), provider=GoogleProvider(client=client))


def _description_and_tool_names(xml_text: str) -> tuple[str, list[str]]:
    root = ET.fromstring(xml_text)
    promises = root.find("promises")
    description = (promises.findtext("description") or "").strip() if promises is not None else ""
    tools_el = promises.find("tools") if promises is not None else None
    names = [t.get("name") for t in tools_el.findall("tool")] if tools_el is not None else []
    return description, names


def _build(workflow_id: str, model, extra_tools: dict | None = None) -> Agent:
    doc = load_contract_doc(workflow_id)
    description, names = _description_and_tool_names(doc.xml_text)
    extra_tools = extra_tools or {}
    tools = []
    missing = []
    for name in names:
        if name in extra_tools:
            tools.append(extra_tools[name])
        elif hasattr(tools_mod, name):
            tools.append(getattr(tools_mod, name))
        else:
            missing.append(name)
    if missing:
        raise AgentConstructionError(f"contract tools not found in grail.tools: {missing}")
    return Agent(model, name=workflow_id, instructions=doc.instruction_text, tools=tools, output_type=str)


def build_grail_agent(model=None) -> Agent:
    """Build the Marshal wired (via agent delegation) to the two trial agents."""
    model = model or _make_model()
    bridge = _build("bridge_of_death", model)
    ni = _build("knights_who_say_ni", model)

    async def attempt_bridge_of_death(ctx: RunContext, knights_answers: str) -> str:
        """Delegate the Bridge of Death trial. Pass the knight's three answers as free text."""
        result = await bridge.run(knights_answers, usage=ctx.usage)
        return result.output

    async def approach_knights_who_say_ni(ctx: RunContext, knights_request: str) -> str:
        """Delegate the Knights Who Say Ni trial. Pass the knight's shrubbery choice/request as free text."""
        result = await ni.run(knights_request, usage=ctx.usage)
        return result.output

    return _build(
        "grail_quest_marshal",
        model,
        extra_tools={
            "attempt_bridge_of_death": attempt_bridge_of_death,
            "approach_knights_who_say_ni": approach_knights_who_say_ni,
        },
    )
