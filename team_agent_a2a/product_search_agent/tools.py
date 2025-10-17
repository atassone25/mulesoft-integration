"""Tools for Product Search Agent - Salesforce integration via A2A"""
import logging
import os
import asyncio
import httpx
import uuid
import base64
from google.adk.tools import FunctionTool
from dotenv import load_dotenv

# Load .env from parent mulesoft-integration directory
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)

logger = logging.getLogger(__name__)

# Configuration from environment
SALESFORCE_BUSCAR_PRODUTO_URL = os.getenv("SALESFORCE_A2A_AGENT_BUSCAR_PRODUTO")

# A2A authentication (Basic auth) - Required by MuleSoft endpoint
AUTH_USERNAME = os.getenv("A2A_AUTH_USERNAME")
AUTH_PASSWORD = os.getenv("A2A_AUTH_PASSWORD")

# Create Basic auth header
if AUTH_USERNAME and AUTH_PASSWORD:
    auth_string = f"{AUTH_USERNAME}:{AUTH_PASSWORD}"
    auth_bytes = auth_string.encode('ascii')
    auth_token = base64.b64encode(auth_bytes).decode('ascii')
    BASIC_AUTH_HEADER = f'Basic {auth_token}'
    logger.info(f"Salesforce Search Tool configured with URL: {SALESFORCE_BUSCAR_PRODUTO_URL} (authenticated)")
else:
    BASIC_AUTH_HEADER = None
    logger.warning(f"Salesforce Search Tool configured without authentication - this may cause errors!")

# Context management for persistent conversations
_context_id = None
_context_timestamp = None
_context_timeout_hours = 2

def _generate_context_id() -> str:
    """Generate a unique context ID with timestamp."""
    import time
    timestamp = int(time.time() * 1000)
    unique_id = str(uuid.uuid4())[:8]
    return f"ctx-{timestamp}-{unique_id}"

def _is_context_expired() -> bool:
    """Check if context has expired."""
    global _context_timestamp
    if _context_timestamp is None:
        return True
    
    import time
    current_time = time.time()
    hours_elapsed = (current_time - _context_timestamp) / 3600
    
    return hours_elapsed >= _context_timeout_hours

def _get_or_create_context_id() -> str:
    """Get existing context ID or create a new one if expired."""
    global _context_id, _context_timestamp
    
    if _context_id is None or _is_context_expired():
        import time
        _context_id = _generate_context_id()
        _context_timestamp = time.time()
        logger.info(f"🆕 Created new context for Salesforce search: {_context_id}")
    else:
        logger.debug(f"🔄 Reusing existing context for Salesforce search: {_context_id}")
    
    return _context_id

def _clear_expired_context():
    """Clear expired context data."""
    global _context_id, _context_timestamp
    _context_id = None
    _context_timestamp = None
    logger.info(f"🗑️  Cleared expired context for Salesforce search")

async def _send_message_with_retry(query: str, max_retries: int = 5) -> str:
    """Send message with persistent retry logic for timeouts and empty responses."""
    for attempt in range(max_retries + 1):
        try:
            # Get current context ID (may be updated during retries)
            context_id = _get_or_create_context_id()
            message_id = str(uuid.uuid4())
            
            # A2A JSON-RPC message/send payload
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "message/send",
                "params": {
                    "contextId": context_id,
                    "message": {
                        "role": "user",
                        "parts": [
                            {
                                "kind": "text",
                                "text": query
                            }
                        ],
                        "contextId": context_id,
                        "messageId": message_id
                    },
                    "metadata": {}
                }
            }
            
            # Headers with Basic authentication (required by MuleSoft)
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Add authentication header if configured
            if BASIC_AUTH_HEADER:
                headers['Authorization'] = BASIC_AUTH_HEADER
            else:
                logger.warning("⚠️  No authentication configured - request may fail!")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                logger.debug(f"Sending request to Salesforce: {SALESFORCE_BUSCAR_PRODUTO_URL}")
                response = await client.post(SALESFORCE_BUSCAR_PRODUTO_URL, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check for JSON-RPC error
                    if "error" in result:
                        logger.error(f"❌ A2A JSON-RPC error: {result['error']}")
                        raise Exception(f"A2A error: {result['error']}")
                    
                    # Extract the agent's response
                    response_text = "No response received from agent"
                    if 'result' in result and 'status' in result['result'] and 'message' in result['result']['status']:
                        agent_message = result['result']['status']['message']
                        if 'parts' in agent_message and agent_message['parts']:
                            response_text = agent_message['parts'][0].get('text', '')
                    
                    # Check if we got a meaningful response
                    if response_text and response_text.strip():
                        # Check for generic/unhelpful responses and confirmation questions
                        generic_responses = [
                            "how can i help you",
                            "how can i assist you", 
                            "hi there",
                            "hello",
                            "what can i do for you"
                        ]
                        
                        # Check for confirmation questions (agent asking for clarification)
                        confirmation_patterns = [
                            "could you confirm",
                            "can you confirm",
                            "please confirm",
                            "is this the product you want",
                            "if there are additional products"
                        ]
                        
                        response_lower = response_text.lower()
                        is_generic = any(generic in response_lower for generic in generic_responses)
                        is_confirmation = any(pattern in response_lower for pattern in confirmation_patterns)
                        
                        # If it's a confirmation question and we're early in attempts, accept it
                        # (the agent might need clarification from upstream)
                        if is_confirmation and attempt == 0:
                            logger.info(f"✅ Got confirmation request from Salesforce on attempt {attempt + 1}")
                            return response_text
                        
                        # If we got a meaningful, non-generic response, return it
                        if not is_generic or len(response_text) > 50:
                            logger.info(f"✅ Got meaningful response from Salesforce on attempt {attempt + 1}")
                            return response_text
                        else:
                            logger.warning(f"🔄 Got generic response from Salesforce, retrying (attempt {attempt + 1}/{max_retries + 1})")
                    
                    # If empty or generic response, retry
                    if attempt < max_retries:
                        logger.warning(f"🔄 Empty or generic response from Salesforce, retrying (attempt {attempt + 1}/{max_retries + 1})")
                        await asyncio.sleep(1)
                        continue
                    else:
                        logger.error(f"❌ Failed to get meaningful response from Salesforce after {max_retries + 1} attempts")
                        return "Error: No meaningful response received after multiple attempts"
                else:
                    error_text = response.text
                    logger.error(f"❌ A2A message/send failed: HTTP {response.status_code}")
                    logger.error(f"Error details: {error_text}")
                    raise Exception(f"Failed to send message: HTTP {response.status_code}")
                        
        except asyncio.TimeoutError as e:
            # Check for timeout errors
            if attempt < max_retries:
                logger.info(f"🔄 Timeout for Salesforce search (attempt {attempt + 1}/{max_retries + 1}), retrying...")
                await asyncio.sleep(2)
                continue
            else:
                logger.error(f"❌ Failed after {max_retries + 1} timeout attempts")
                raise e
                
        except Exception as e:
            error_message = str(e).lower()
            
            # Check for context expiration error
            if ("not found (404)" in error_message or "context" in error_message) and attempt < max_retries:
                logger.info(f"🔄 Context expired for Salesforce search (attempt {attempt + 1}/{max_retries + 1}), generating new context...")
                _clear_expired_context()
                continue
            
            # For other errors, retry a few times before giving up
            if attempt < max_retries:
                logger.warning(f"🔄 Retry {attempt + 1}/{max_retries + 1} for Salesforce search: {e}")
                await asyncio.sleep(1)
                continue
            else:
                logger.error(f"❌ Failed after {max_retries + 1} attempts for Salesforce search: {e}")
                raise e
    
    return "Error: Failed to send message after retries"

async def salesforce_search(query: str) -> str:
    """
    Search for products in Salesforce via A2A protocol.
    
    Args:
        query: Product search query (names, codes, specifications)
        
    Returns:
        Product search results from Salesforce
    """
    text = (query or "").strip()
    if not text:
        return "Please provide product names or specifications to search."

    try:
        # Format query with explicit search intent (like working test examples)
        # The Salesforce agent expects queries with action verbs like "Buscar"
        if not any(keyword in text.lower() for keyword in ['buscar', 'verificar', 'procurar', 'pesquisar', 'listar']):
            # Add explicit search prefix to make intent clear
            formatted_query = f"Buscar produto: {text}"
            logger.debug(f"Added search prefix to query: {formatted_query}")
        else:
            formatted_query = text
        
        logger.info(f"🔍 Salesforce Search: {formatted_query[:100]}{'...' if len(formatted_query) > 100 else ''}")
        response = await _send_message_with_retry(formatted_query)
        logger.info(f"✅ Salesforce search completed")
        return response
            
    except Exception as e:
        logger.error(f"Error in salesforce_search: {e}")
        return f"Error searching products in Salesforce: {str(e)}"

# Create ADK FunctionTool instance
salesforce_search_tool = FunctionTool(func=salesforce_search)
