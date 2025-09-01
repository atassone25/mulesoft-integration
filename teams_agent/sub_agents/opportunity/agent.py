"""Opportunity agent for evaluating and logging business opportunities."""

import os
from datetime import datetime
from google.adk.agents import Agent

from . import prompt

ADK_MODEL = os.getenv("MODEL", "gemini-2.0-flash")

def log_opportunity(opportunity):
    """Log a valuable opportunity to a file."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"opportunity_{timestamp}.log")
    
    with open(log_file, "w") as f:
        f.write(f"Opportunity logged at: {datetime.now()}\n")
        f.write("=" * 50 + "\n")
        for key, value in opportunity.items():
            f.write(f"{key}:\n{value}\n\n")

opportunity_agent = Agent(
    model=ADK_MODEL,
    name="opportunity_agent",
    description="Evaluate business offers and log valuable opportunities",
    instruction=prompt.OPPORTUNITY_PROMPT,
)
