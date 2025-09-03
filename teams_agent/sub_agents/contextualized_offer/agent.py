"""Contextualized offer agent for generating business offers based on context."""

import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext, FunctionTool

from teams_agent.prompt import CONTEXTUALIZED_OFFER_PROMPT

ADK_MODEL = os.getenv("MODEL", "gemini-2.0-flash")

async def read_context_tool(tool_context: ToolContext) -> dict:
    """Tool for reading context from files in the context directory."""
    try:
        context_data = {}
        base_path = os.path.join(os.path.dirname(__file__), "context")
        files = {
            "user_history": "user_history.txt",
            "products": "commercial_products.txt",
            "demands": "business_demands.txt"
        }
        
        for key, filename in files.items():
            filepath = os.path.join(base_path, filename)
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    context_data[key] = f.read()
                    
        return {
            "status": "success",
            "context_data": context_data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading context files: {str(e)}"
        }

# Create the tool instance
read_context_tool_instance = FunctionTool(func=read_context_tool)

contextualized_offer_agent = Agent(
    model=ADK_MODEL,
    name="contextualized_offer_agent", 
    description="Generate contextualized business offers based on user history, products, and demands",
    instruction=CONTEXTUALIZED_OFFER_PROMPT,
    tools=[read_context_tool_instance]
)
