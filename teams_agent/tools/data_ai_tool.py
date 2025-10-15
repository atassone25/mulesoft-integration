"""
Data and AI Tool - Real implementation using the deployed datastore_agent as a service
"""

import logging
import asyncio
from google.adk.tools import FunctionTool
import google.auth
import google.auth.transport.requests
import requests
import json

logger = logging.getLogger(__name__)

# Use the working datastore_agent as a service
DATASTORE_AGENT_ID = "4757723152828596224" # Datastore Agent with Sources
PROJECT_ID = "gglobo-agentsb2b-hdg-dev"
LOCATION = "us-central1"

logger.info(f"Initializing Data & AI tool using datastore_agent service: {DATASTORE_AGENT_ID}")

def get_google_token():
    """Get Google Cloud authentication token"""
    try:
        credentials, project = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        return credentials.token
    except Exception as e:
        logger.error(f"Failed to get Google Cloud token: {e}")
        return None

async def data_and_ai(query: str) -> str:
    """
    Search for B2B offers and products using the deployed datastore_agent.
    
    Args:
        query: Search query for products, offers, or business information
        
    Returns:
        Relevant B2B offers and products from the datastore
    """
    try:
        logger.info(f"🔧 DATA AI TOOL: Searching via datastore_agent for: {query[:100]}{'...' if len(query) > 100 else ''}")
        
        # Get authentication token
        token = get_google_token()
        if not token:
            return "Error: Could not authenticate with Google Cloud"
        
        # Create session with datastore agent
        session_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{DATASTORE_AGENT_ID}:query"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Create session
        session_payload = {
            "class_method": "create_session",
            "input": {"user_id": "data_ai_tool"}
        }
        
        session_response = requests.post(session_url, headers=headers, json=session_payload, timeout=30)
        session_response.raise_for_status()
        session_data = session_response.json()
        session_id = session_data["output"]["id"]
        
        # Query the datastore agent using stream_query
        # Note: The datastore agent expects queries with product attributes and criteria
        # We pass the query directly to let the datastore agent extract keywords
        query_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{DATASTORE_AGENT_ID}:streamQuery?alt=sse"
        query_payload = {
            "class_method": "stream_query", 
            "input": {
                "user_id": "data_ai_tool",
                "session_id": session_id,
                "message": f"Buscar produtos com os seguintes critérios: {query}"
            }
        }
        
        query_response = requests.post(query_url, headers=headers, json=query_payload, timeout=60, stream=True)
        query_response.raise_for_status()
        
        # Parse streaming response
        response_text = ""
        for line in query_response.iter_lines():
            if line:
                line_str = line.decode('utf-8').strip()
                if line_str:  # Skip empty lines
                    try:
                        json_data = json.loads(line_str)
                        if "content" in json_data and "parts" in json_data["content"]:
                            for part in json_data["content"]["parts"]:
                                if "text" in part:
                                    response_text += part["text"]
                    except json.JSONDecodeError:
                        continue
        
        if response_text.strip():
            # Format for teams_agent context
            formatted_response = f"Produtos disponíveis encontrados na base de dados:\n\n{response_text.strip()}\n\nEstes produtos podem ser incorporados em ofertas contextualizadas para clientes."
            return formatted_response
        
        return "No results found in the datastore for the given query."
            
    except requests.exceptions.Timeout:
        logger.error("Timeout while querying datastore agent")
        return "Error: Search request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error while querying datastore agent: {e}")
        return f"Error: Failed to search datastore - {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in data_and_ai tool: {e}")
        return f"Error: Unexpected error occurred - {str(e)}"

# Create ADK FunctionTool instance (compatible with other FunctionTools)
data_and_ai_tool = FunctionTool(func=data_and_ai)
