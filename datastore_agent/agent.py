# /home/emmanueltassone/globo/mulesoft-integration/datastore_agent/agent.py
# Copyright 2025
# Licensed under the Apache License, Version 2.0

"""Simple datastore agent for testing Vertex AI Search integration."""

from __future__ import annotations

import os
import logging
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool

# Configure ADK logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Configuration from environment variables
ADK_MODEL = os.getenv("MODEL", "gemini-2.0-flash")

# DataStore configuration
# DATASTORE_ID = "projects/205867137421/locations/us/collections/default_collection/dataStores/ma014-datastore-oferta_b2b"
DATASTORE_ID = "projects/205867137421/locations/us/collections/default_collection/dataStores/ma014-datastore-develop-oferta_b2b"

# Create Vertex AI Search tool using built-in tool with regular Agent class
logger.info(f"Initializing Vertex AI Search tool with datastore: {DATASTORE_ID}")

# Initialize the Vertex AI Search tool 
datastore_search_tool = VertexAiSearchTool(
    data_store_id=DATASTORE_ID
)

# Simple agent prompt
AGENT_PROMPT = """You are a helpful assistant that can search for B2B offers and business information.

Your main capability is to search through a datastore of business offers using the Vertex AI Search tool.

When users ask questions about:
- B2B offers
- Business products  
- Services
- Pricing information
- Product specifications
- Any business-related queries

Use the Vertex AI Search tool to find relevant information and provide helpful responses.

Always be clear about what information you found and provide specific details from the search results.
"""

# Create the datastore agent using regular Agent class (like working teams_agent)
datastore_agent = Agent(
    model=ADK_MODEL,
    name="datastore_agent", 
    description="Simple agent for testing Vertex AI Search datastore connectivity",
    instruction=AGENT_PROMPT,
    tools=[datastore_search_tool],
)

# Expose as entry point
root_agent = datastore_agent

logger.info(f"✅ Datastore agent initialized successfully")
logger.info(f"  Model: {ADK_MODEL}")
logger.info(f"  Datastore: {DATASTORE_ID}")
logger.info(f"  Tools: {[tool.name for tool in datastore_agent.tools]}")
