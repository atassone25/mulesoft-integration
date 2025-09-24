# teams_agent/sub_agents/contextualized_offer/agent.py

import os
from google.adk.agents import Agent
from teams_agent.tools.salesforce_tools import buscar_produto_tool
from teams_agent.tools.data_ai_tool import data_and_ai_tool
from teams_agent.prompt import (
    PRODUCT_FETCHER_PROMPT,
    PRODUCT_VERIFIER_PROMPT,
    OFFER_GENERATOR_PROMPT
)

ADK_MODEL = os.getenv("MODEL", "gemini-2.0-flash")

# --- Individual Agents for Interactive Workflow ---

# Product Fetcher Agent - Gets products from Data & AI system
product_fetcher_agent = Agent(
    model=ADK_MODEL,
    name="ProductFetcherAgent",
    description="Fetches available products from Data & AI system and asks for user confirmation",
    instruction=PRODUCT_FETCHER_PROMPT,
    tools=[data_and_ai_tool],
)

# Product Verifier Agent - Verifies products using buscar_produto
product_verifier_agent = Agent(
    model=ADK_MODEL,
    name="ProductVerifierAgent", 
    description="Verifies products from Data & AI using Salesforce buscar_produto and asks for user confirmation",
    instruction=PRODUCT_VERIFIER_PROMPT,
    tools=[buscar_produto_tool],
)

# Offer Generator Agent - Creates the final contextualized offer
offer_generator_agent = Agent(
    model=ADK_MODEL,
    name="OfferGeneratorAgent",
    description="Generates contextualized offers using verified products",
    instruction=OFFER_GENERATOR_PROMPT,
    tools=[],  # No tools needed, just uses verified data
)

# --- Main Contextualized Offer Agent ---
# This agent coordinates the workflow with user confirmation steps
contextualized_offer_agent = Agent(
    model=ADK_MODEL,
    name="ContextualizedOfferAgent",
    sub_agents=[product_fetcher_agent, product_verifier_agent, offer_generator_agent],
    description="Coordinates contextualized offer creation with user confirmation at each step",
    instruction="""You are the Contextualized Offer Coordinator Agent.

Your role is to coordinate the creation of personalized business offers through a multi-step process that requires user confirmation at each stage.

WORKFLOW PROCESS:
1. **Initial Information Gathering**: Ensure you have client name, strategy, and investment amount
2. **Product Fetching**: Delegate to ProductFetcherAgent to get products and wait for user confirmation
3. **Product Verification**: After user confirms, delegate to ProductVerifierAgent for verification and wait for user confirmation  
4. **Offer Generation**: After user confirms verified products, delegate to OfferGeneratorAgent to create the final offer

DELEGATION RULES:
- Start with ProductFetcherAgent when user requests contextualized offer: use transfer_to_agent(agent_name="ProductFetcherAgent")
- Only proceed to ProductVerifierAgent after user confirms they want to proceed with fetched products: use transfer_to_agent(agent_name="ProductVerifierAgent")
- Only proceed to OfferGeneratorAgent after user confirms they want to proceed with verified products: use transfer_to_agent(agent_name="OfferGeneratorAgent")
- If user says "no" at any confirmation step, ask them what they would like to do instead

MANDATORY REQUIREMENTS:
- NEVER create offers without client name, strategy, and investment amount
- ALWAYS wait for user confirmation between each step
- Use sub_agents to handle the actual product fetching, verification, and offer generation
- Coordinate the flow based on user responses

When user first requests contextualized offer, ensure you have all required information, then IMMEDIATELY delegate to ProductFetcherAgent using transfer_to_agent(agent_name="ProductFetcherAgent")."""
)
