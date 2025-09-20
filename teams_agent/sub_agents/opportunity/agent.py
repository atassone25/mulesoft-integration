# teams_agent/sub_agents/opportunity/agent.py

import os
from google.adk.agents import Agent
from teams_agent.prompt import OPPORTUNITY_PROMPT
from teams_agent.tools.salesforce_tools import oportunidades_tool

ADK_MODEL = os.getenv("MODEL", "gemini-2.0-flash")


opportunity_agent = Agent(
    model=ADK_MODEL,
    name="opportunity_agent",
    description="Register and manage business opportunities in Salesforce via A2A protocol",
    instruction=OPPORTUNITY_PROMPT,
    tools=[oportunidades_tool],
)
