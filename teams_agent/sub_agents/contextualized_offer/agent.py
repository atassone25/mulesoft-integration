# teams_agent/sub_agents/contextualized_offer/agent.py

import os
from google.adk.agents import Agent
from teams_agent.prompt import CONTEXTUALIZED_OFFER_PROMPT
from teams_agent.tools.salesforce_tools import (
    buscar_historico_tool,
    buscar_produto_tool,
    oportunidades_tool
)

ADK_MODEL = os.getenv("MODEL", "gemini-2.0-flash")


contextualized_offer_agent = Agent(
    model=ADK_MODEL,
    name="contextualized_offer_agent",
    description="Generate contextualized business offers using Salesforce API (powered by A2A protocol) for client history, product search, and opportunity management",
    instruction=CONTEXTUALIZED_OFFER_PROMPT,
    tools=[buscar_historico_tool, buscar_produto_tool, oportunidades_tool],
)
