# teams_agent/sub_agents/contextualized_offer/agent.py

import os
from google.adk.agents import Agent
from teams_agent.prompt import CONTEXTUALIZED_OFFER_PROMPT
from teams_agent.tools.salesforce_tools import buscar_produto_tool
from teams_agent.tools.data_ai_tool import data_and_ai_tool

ADK_MODEL = os.getenv("MODEL", "gemini-2.0-flash")


contextualized_offer_agent = Agent(
    model=ADK_MODEL,
    name="contextualized_offer_agent",
    description="Generate contextualized business offers using Salesforce data and Data & AI products, requiring client name, strategy, and investment amount",
    instruction=CONTEXTUALIZED_OFFER_PROMPT,
    tools=[buscar_produto_tool, data_and_ai_tool],
)
