# /home/nrubinstein/projects/mulesoft-integration/teams_agent/agent.py
# Copyright 2025
# Licensed under the Apache License, Version 2.0

"""Teams agent that coordinates business opportunities and delegates to sub-agents."""

from __future__ import annotations

import os
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
# from google.adk.memory import InMemoryMemoryService, VertexAiMemoryBankService
# from google.adk.tools import load_memory
from google.genai import types
from typing import Optional

from . import prompt
from .sub_agents.contextualized_offer.agent import contextualized_offer_agent


# Configure ADK logging
import logging

# Set up basic logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)


# ---- Memory service configuration ----
# Based on ADK documentation: https://google.github.io/adk-docs/sessions/memory/
# def _build_memory_service():
#     """Build memory service based on environment configuration."""
#     use_vertex = os.getenv("USE_VERTEX_MEMORY", "").lower() in ("1", "true", "yes")
    
#     if not use_vertex:
#         logger.info("Using InMemoryMemoryService (USE_VERTEX_MEMORY not enabled)")
#         return InMemoryMemoryService()

#     project = os.getenv("GOOGLE_CLOUD_PROJECT")
#     location = os.getenv("GOOGLE_CLOUD_LOCATION")
#     agent_engine_id = os.getenv("AGENT_ENGINE_ID")

#     if not (project and location and agent_engine_id):
#         logger.warning(
#             f"Missing required environment variables for VertexAiMemoryBankService: "
#             f"GOOGLE_CLOUD_PROJECT={project}, GOOGLE_CLOUD_LOCATION={location}, "
#             f"AGENT_ENGINE_ID={agent_engine_id}. Falling back to InMemoryMemoryService."
#         )
#         return InMemoryMemoryService()

#     try:
#         logger.info(f"Initializing VertexAiMemoryBankService with project={project}, location={location}, agent_engine_id={agent_engine_id}")
#         return VertexAiMemoryBankService(
#             project=project,
#             location=location,
#             agent_engine_id=agent_engine_id,
#         )
#     except Exception as e:
#         logger.error(f"Failed to initialize VertexAiMemoryBankService: {e}. Falling back to InMemoryMemoryService.")
#         return InMemoryMemoryService()

# # Memory service instance - this will be used by the Runner
# MEMORY_SERVICE = _build_memory_service()


# ---- Model + sub-agents ----
ADK_MODEL = os.getenv("MODEL", "gemini-2.0-flash")

SUB_AGENTS = [contextualized_offer_agent]

# Include opportunity agent
try:
    from .sub_agents.opportunity.agent import opportunity_agent
    SUB_AGENTS.append(opportunity_agent)
    logger.info("✅ Added Opportunity Agent to coordinator")
except Exception as e:
    logger.warning(f"⚠️ Could not load Opportunity Agent: {e}")


# ---- Coordinator (root) agent ----
coordinator_agent = Agent(
    model=ADK_MODEL,
    name="coordinator_agent",
    description="Coordinate decisions about business opportunities and handle team communication",
    instruction=prompt.COORDINATOR_PROMPT,
    sub_agents=SUB_AGENTS,
    # tools=[load_memory],  # Add memory search capability
)

# Expose as entry point
root_agent = coordinator_agent