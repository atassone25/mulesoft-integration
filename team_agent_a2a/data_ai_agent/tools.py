"""Tools for Data AI Agent - Vertex AI Search integration"""
import logging
import os
import json
import google.auth
import google.auth.transport.requests
import requests
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)

# Configuration from environment  
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "gglobo-agentsb2b-hdg-dev")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
# Use the WORKING datastore agent ID from teams_agent
DATASTORE_AGENT_ID = "4757723152828596224"  # Datastore Agent with Sources (WORKING!)

logger.info(f"Vertex Search Tool configured: project={PROJECT_ID}, location={LOCATION}, datastore={DATASTORE_AGENT_ID}")

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

async def vertex_search(query: str) -> str:
    """
    Search for B2B products and offers from Vertex AI Search datastore.
    
    Args:
        query: Search query for products, offers, or business information
        
    Returns:
        Relevant B2B offers and products from the datastore
    """
    text = (query or "").strip()
    if not text:
        return "Please provide search criteria (segment, time period, investment, location, etc.)"
    
    try:
        logger.info(f"🔍 Vertex AI Search: {text[:100]}{'...' if len(text) > 100 else ''}")
        
        # Get authentication token
        token = get_google_token()
        if not token:
            return "Error: Could not authenticate with Google Cloud"
        
        # Vertex AI Search endpoint
        base_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1"
        search_url = f"{base_url}/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{DATASTORE_AGENT_ID}:query"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Create session first
        session_payload = {
            "class_method": "create_session",
            "input": {"user_id": "data_ai_agent"}
        }
        
        logger.debug(f"Creating session with datastore agent {DATASTORE_AGENT_ID}")
        session_response = requests.post(search_url, headers=headers, json=session_payload, timeout=30)
        session_response.raise_for_status()
        session_data = session_response.json()
        session_id = session_data["output"]["id"]
        logger.debug(f"Session created: {session_id}")
        
        # Query with streaming
        stream_url = f"{base_url}/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{DATASTORE_AGENT_ID}:streamQuery?alt=sse"
        query_payload = {
            "class_method": "stream_query",
            "input": {
                "user_id": "data_ai_agent",
                "session_id": session_id,
                "message": f"Buscar produtos com os seguintes critérios: {text}"
            }
        }
        
        logger.debug(f"Executing search query")
        query_response = requests.post(stream_url, headers=headers, json=query_payload, timeout=60, stream=True)
        query_response.raise_for_status()
        
        # Parse streaming response
        response_text = ""
        for line in query_response.iter_lines():
            if line:
                line_str = line.decode('utf-8').strip()
                if line_str:
                    try:
                        json_data = json.loads(line_str)
                        if "content" in json_data and "parts" in json_data["content"]:
                            for part in json_data["content"]["parts"]:
                                if "text" in part:
                                    response_text += part["text"]
                    except json.JSONDecodeError:
                        continue
        
        if response_text.strip():
            logger.info(f"✅ Search completed: {len(response_text)} characters")
            # Format for better readability
            formatted_response = f"I found the following products:\n\n{response_text.strip()}"
            return formatted_response
        
        logger.warning("Search returned no results")
        return "No products found matching the search criteria. Try different keywords or criteria."
        
    except requests.exceptions.Timeout:
        logger.error("Timeout while querying Vertex AI Search")
        return "Error: Search request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error while querying Vertex AI Search: {e}")
        return f"Error: Failed to search - {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in vertex_search: {e}", exc_info=True)
        return f"Error: Unexpected error occurred - {str(e)}"

# Create ADK FunctionTool instance
vertex_search_tool = FunctionTool(func=vertex_search)

