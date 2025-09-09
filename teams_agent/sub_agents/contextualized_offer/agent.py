# teams_agent/sub_agents/contextualized_offer/agent.py

import os
from google.adk.agents import Agent
from teams_agent.prompt import CONTEXTUALIZED_OFFER_PROMPT
from teams_agent.sub_agents.contextualized_offer.buscar_historico_tool import (
    buscar_historico_tool_instance,
)

ADK_MODEL = os.getenv("MODEL", "gemini-2.0-flash")



contextualized_offer_agent = Agent(
    model=ADK_MODEL,
    name="contextualized_offer_agent",
    description="Generate contextualized business offers using external client history via A2A",
    instruction=CONTEXTUALIZED_OFFER_PROMPT,
    tools=[buscar_historico_tool_instance],
)
