# teams_agent/sub_agents/contextualized_offer/agent.py

import os
from google.adk.agents import Agent
from ...tools.salesforce_tools import buscar_produto_tool
from ...tools.data_ai_tool import data_and_ai_tool
from ... import prompt

ADK_MODEL = os.getenv("MODEL", "gemini-2.5-flash")

# --- Individual Agents for Interactive Workflow ---

# Product Fetcher Agent - Gets products from Data & AI system
product_fetcher_agent = Agent(
    model=ADK_MODEL,
    name="ProductFetcherAgent",
    description="Fetches available products from Data & AI system and asks for user confirmation",
    instruction=prompt.PRODUCT_FETCHER_PROMPT,
    tools=[data_and_ai_tool],
)

# Product Verifier Agent - Verifies products using buscar_produto
product_verifier_agent = Agent(
    model=ADK_MODEL,
    name="ProductVerifierAgent", 
    description="Verifies products from Data & AI using Salesforce buscar_produto and asks for user confirmation",
    instruction=prompt.PRODUCT_VERIFIER_PROMPT,
    tools=[buscar_produto_tool],
)

# Offer Generator Agent - Creates the final contextualized offer
offer_generator_agent = Agent(
    model=ADK_MODEL,
    name="OfferGeneratorAgent",
    description="Generates contextualized offers using verified products",
    instruction=prompt.OFFER_GENERATOR_PROMPT,
    tools=[],  # No tools needed, just uses verified data
)

# --- Main Contextualized Offer Agent ---
# This agent coordinates the workflow with user confirmation steps
contextualized_offer_agent = Agent(
    model=ADK_MODEL,
    name="ContextualizedOfferAgent",
    sub_agents=[product_fetcher_agent, product_verifier_agent, offer_generator_agent],
    description="Coordinates contextualized offer creation with user confirmation at each step",
    instruction=prompt.CONTEXTUALIZED_OFFER_COORDINATOR_PROMPT,
)
