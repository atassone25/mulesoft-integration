# /home/nrubinstein/projects/mulesoft-integration/teams_agent/agent.py
# Copyright 2025
# Licensed under the Apache License, Version 2.0

"""Teams agent that coordinates business opportunities and delegates to sub-agents."""

from __future__ import annotations

import os
from google.adk.agents import Agent
from google.adk.memory import InMemoryMemoryService, VertexAiMemoryBankService

from . import prompt
from .sub_agents.contextualized_offer.agent import contextualized_offer_agent


# ---- Memory service (defaults to in-memory; enable Vertex via env vars) ----
def _build_memory_service():
    use_vertex = os.getenv("USE_VERTEX_MEMORY", "").lower() in ("1", "true", "yes")
    if not use_vertex:
        return InMemoryMemoryService()

    project = os.getenv("VERTEX_PROJECT") or os.getenv("PROJECT_ID")
    location = os.getenv("VERTEX_LOCATION") or os.getenv("LOCATION")
    agent_engine_id = os.getenv("AGENT_ENGINE_ID")  # e.g. ".../agentEngines/<ID>" → pass just <ID>

    if project and location and agent_engine_id:
        return VertexAiMemoryBankService(
            project=project,
            location=location,
            agent_engine_id=agent_engine_id,
        )

    # Fallback if required env vars are missing
    return InMemoryMemoryService()


MEMORY_SERVICE = _build_memory_service()


# ---- Model + sub-agents ----
ADK_MODEL = os.getenv("MODEL", "gemini-2.0-flash")

SUB_AGENTS = [contextualized_offer_agent]
# Optional: include additional sub-agents if present
try:
    from .sub_agents.opportunity.agent import opportunity_agent  # noqa: F401

    SUB_AGENTS.append(opportunity_agent)  # type: ignore[name-defined]
except Exception:
    pass


# ---- Coordinator (root) agent ----
coordinator_agent = Agent(
    model=ADK_MODEL,
    name="coordinator_agent",
    description="Coordinate decisions about business opportunities and handle team communication",
    instruction=prompt.COORDINATOR_PROMPT,
    sub_agents=SUB_AGENTS,
    # If your ADK Agent supports a memory_service parameter, uncomment the next line:
    # memory_service=MEMORY_SERVICE,
)

# Expose as entry point
root_agent = coordinator_agent