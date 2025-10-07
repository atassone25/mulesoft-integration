# teams_agent/sub_agents/opportunity/agent.py

import os
from google.adk.agents import Agent
from ...tools.salesforce_tools import oportunidades_tool
from ... import prompt

ADK_MODEL = os.getenv("MODEL", "gemini-2.5-flash")


opportunity_agent = Agent(
    model=ADK_MODEL,
    name="opportunity_agent",
    description="Register and manage business opportunities in Salesforce via A2A protocol",
    instruction=prompt.OPPORTUNITY_PROMPT,
    tools=[oportunidades_tool],
)
