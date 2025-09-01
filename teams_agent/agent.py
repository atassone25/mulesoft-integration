# Copyright 2025
# Licensed under the Apache License, Version 2.0

"""Teams agent that handles business opportunities through context analysis."""

from google.adk.agents import Agent

from . import prompt
from .sub_agents.contextualized_offer import contextualized_offer_agent
from .sub_agents.opportunity import opportunity_agent
from os import getenv

ADK_MODEL = getenv("MODEL", "gemini-2.0-flash")

coordinator_agent = Agent(
    model=ADK_MODEL,
    name="coordinator_agent",
    description=(
        "Coordinate decisions about business opportunities and handle team communication"
    ),
    instruction=prompt.COORDINATOR_PROMPT,
    sub_agents=[
        contextualized_offer_agent,
        opportunity_agent,
    ],
)

root_agent = coordinator_agent
