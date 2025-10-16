"""Orchestrator Agent - Two-level hierarchy with A2A communication"""
import logging
import os
import asyncio
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

# Configure ADK for Vertex AI
from orchestrator.config import configure_adk_for_vertexai
configure_adk_for_vertexai()

from orchestrator import prompts
from orchestrator.remote_agent_connection import get_remote_connections

logger = logging.getLogger(__name__)

# Global remote connections instance
_connections = None

async def send_message_to_agent(agent_name: str, message: str) -> str:
    """
    Send a message to a remote A2A agent.
    
    Args:
        agent_name: Name of the agent (e.g., "Data AI Agent", "Product Search Agent")
        message: Message to send
        
    Returns:
        Response from the remote agent
    """
    global _connections
    
    try:
        # Initialize connections if needed
        if _connections is None:
            _connections = get_remote_connections()
            await _connections.initialize()
        
        logger.info(f"📨 Sending message to {agent_name}")
        response = await _connections.send_message(agent_name, message)
        logger.info(f"✅ Received response from {agent_name}: {len(response)} chars")
        return response
        
    except Exception as e:
        logger.error(f"Error in send_message_to_agent: {e}", exc_info=True)
        return f"Error communicating with {agent_name}: {str(e)}"

# Create send_message tool
send_message_tool = FunctionTool(func=send_message_to_agent)

def create_orchestrator():
    """Create the orchestrator agent with 2-level hierarchy"""
    
    # Get model from environment
    model = os.getenv("MODEL") or os.getenv("ADK_MODEL", "gemini-2.5-flash")
    
    # Sub-agent: ContextualizedOfferAgent
    # This agent uses send_message tool to communicate with remote A2A agents
    contextualized_offer_agent = Agent(
        name="ContextualizedOfferAgent",
        model=model,
        description="Creates contextualized offers by querying remote A2A agents for product information",
        instruction=prompts.CONTEXTUALIZED_OFFER_AGENT_PROMPT,
        tools=[send_message_tool],
    )
    
    # Root agent: Coordinator
    coordinator_agent = Agent(
        name="coordinator_agent",
        model=model,
        description="Coordinates offer creation and routes to sub-agents",
        instruction=prompts.COORDINATOR_PROMPT,
        sub_agents=[contextualized_offer_agent],
    )
    
    logger.info(f"✅ Orchestrator created with model: {model}")
    logger.info(f"   - Coordinator Agent")
    logger.info(f"   - ContextualizedOfferAgent (with send_message tool)")
    
    return coordinator_agent

# Create root agent instance
root_agent = create_orchestrator()

