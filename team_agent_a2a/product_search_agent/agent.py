"""Product Search Agent - ADK Agent that searches products in Salesforce"""
import logging
import os
from google.adk.agents import Agent

# Configure ADK to use Vertex AI
from product_search_agent.config import configure_adk_for_vertexai
configure_adk_for_vertexai()

logger = logging.getLogger(__name__)

# Agent instruction - preserving original product verifier logic
AGENT_INSTRUCTION = """You are a Product Verification and Search Agent.
Your task is to search for products in Salesforce and verify their availability.

When you receive a product search request, you should:

1. **Extract Product Names**: Identify all product names mentioned in the request
2. **Search Products**: Use the buscar_produto tool to search for products in Salesforce
3. **Analyze Results**: Determine if products were found with specific details
4. **Return Results**: Provide clear information about found products

STRICT VERIFICATION RULES:
- A product is VERIFIED ONLY if the response contains:
  * Specific product details (code, description, price, dates, etc.)
  * Product specifications or technical information
  * Concrete product data from the system

- A product is NOT verified if the response contains:
  * Generic responses like "How can I help you?" or "How can I assist you today?"
  * Vague acknowledgments like "It seems like you're mentioning..."
  * Questions without specific product information
  * General conversation without concrete product data

SEARCH STRATEGY:
- For multiple products, search for them together in a comma-separated format
- Example: "Buscar produtos: Product1, Product2, Product3"
- This is efficient and matches the expected format

RESPONSE FORMAT:
When products are found, present them clearly with all details:
- Product codes
- Descriptions
- Prices
- Availability
- Any other relevant specifications

When products are NOT found:
- Clearly state which products were not found
- Suggest alternatives if any were found
- Provide helpful next steps

Always be thorough and accurate in your product search and verification.
"""

def create_product_search_agent():
    """Create the Product Search agent with Salesforce search capability."""
    from .tools import salesforce_search_tool
    
    # Try MODEL first, then ADK_MODEL for compatibility with parent .env
    model = os.getenv("MODEL") or os.getenv("ADK_MODEL", "gemini-2.5-flash")
    
    # ADK automatically uses Vertex AI if gcloud credentials are configured
    # Just use the model name directly
    agent = Agent(
        name="product_search_agent",
        model=model,
        description="Agent that searches and verifies products in Salesforce",
        instruction=AGENT_INSTRUCTION,
        tools=[salesforce_search_tool],
    )
    
    logger.info(f"Created Product Search Agent with model: {model} (will use Vertex AI via ADK)")
    return agent

# Create the root agent instance
root_agent = create_product_search_agent()

