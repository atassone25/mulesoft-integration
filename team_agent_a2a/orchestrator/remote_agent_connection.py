"""Remote Agent Connection - Handles A2A communication with remote agents"""
import logging
import os
import asyncio
import json
from typing import Dict, Optional
import httpx

logger = logging.getLogger(__name__)

class RemoteAgentConnections:
    """Manages connections to remote A2A agents"""
    
    def __init__(self):
        self.agent_cards = {}
        self.agent_urls = {}
        self.httpx_client = None
        self._initialized = False
        
    async def initialize(self):
        """Discover and connect to remote A2A agents"""
        if self._initialized:
            return
            
        # Create httpx client
        if self.httpx_client is None:
            self.httpx_client = httpx.AsyncClient(timeout=120.0)
            
        # Get remote agent addresses from environment
        remote_addresses = os.getenv('REMOTE_AGENT_ADDRESSES', '')
        if not remote_addresses:
            logger.warning("No REMOTE_AGENT_ADDRESSES configured")
            return
            
        addresses = [addr.strip() for addr in remote_addresses.split(',') if addr.strip()]
        logger.info(f"Discovering {len(addresses)} remote agents...")
        
        for url in addresses:
            try:
                logger.info(f"Fetching agent card from: {url}")
                
                # Fetch agent card directly
                card_url = f"{url}/.well-known/agent-card.json"
                response = await self.httpx_client.get(card_url)
                
                if response.status_code == 200:
                    card_data = response.json()
                    agent_name = card_data.get('name')
                    
                    if agent_name:
                        self.agent_cards[agent_name] = card_data
                        self.agent_urls[agent_name] = url
                        logger.info(f"✅ Connected to: {agent_name} at {url}")
                    else:
                        logger.warning(f"⚠️  Agent card missing 'name' field from: {url}")
                else:
                    logger.warning(f"⚠️  Could not fetch agent card from {url}: HTTP {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to connect to {url}: {e}")
                
        self._initialized = True
        logger.info(f"Remote agent discovery complete. Connected to: {list(self.agent_cards.keys())}")
        
    def get_agent_names(self) -> list:
        """Get list of available agent names"""
        return list(self.agent_cards.keys())
        
    async def send_message(self, agent_name: str, message: str, context_id: Optional[str] = None) -> str:
        """
        Send a message to a remote A2A agent and return the response.
        
        Args:
            agent_name: Name of the remote agent (e.g., "Data AI Agent")
            message: Message text to send
            context_id: Optional context ID for conversation continuity
            
        Returns:
            Response text from the agent
        """
        # Ensure we're initialized
        if not self._initialized:
            await self.initialize()
            
        if agent_name not in self.agent_urls:
            available = ", ".join(self.agent_cards.keys())
            error_msg = f"Agente '{agent_name}' não encontrado. Disponíveis: {available}"
            logger.error(error_msg)
            return f"{{\"error\": \"{error_msg}\"}}"
            
        url = self.agent_urls[agent_name]
        
        try:
            logger.info(f"📤 Sending message to {agent_name}: {message[:100]}...")
            
            # Ensure httpx client exists
            if self.httpx_client is None:
                self.httpx_client = httpx.AsyncClient(timeout=120.0)
            
            # Generate IDs if not provided
            import uuid
            if not context_id:
                context_id = f"ctx-{uuid.uuid4()}"
            message_id = f"msg-{uuid.uuid4()}"
            task_id = f"task-{uuid.uuid4()}"
            
            # Construct A2A message/send payload
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "message/send",
                "params": {
                    "contextId": context_id,
                    "message": {
                        "role": "user",
                        "parts": [{"kind": "text", "text": message}],
                        "contextId": context_id,
                        "messageId": message_id,
                        "taskId": task_id
                    }
                }
            }
            
            # Use the class httpx client for HTTP requests with streaming
            client = self.httpx_client
            logger.debug(f"Sending A2A request to {url}")
            
            # Request with streaming support
            async with client.stream(
                'POST',
                url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/x-ndjson'
                }
            ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        logger.error(f"A2A request failed: {response.status_code} - {error_text.decode()}")
                        return f"{{\"error\": \"Request failed with status {response.status_code}\"}}"
                    
                    # Process streaming response
                    final_response = None
                    artifacts = []
                    
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                            
                        try:
                            event = json.loads(line)
                            logger.debug(f"📥 Stream line received: {json.dumps(event, indent=2)[:200]}")
                            
                            # Look for artifacts in the event
                            if 'artifact' in event:
                                artifact = event['artifact']
                                artifacts.append(artifact)
                                logger.debug(f"📋 Artifact: name={artifact.get('name')}, keys={artifact.keys()}")
                                
                                # Extract final_response artifact
                                if artifact.get('name') == 'final_response':
                                    if 'parts' in artifact and artifact['parts']:
                                        for part in artifact['parts']:
                                            if 'text' in part:
                                                final_response = part['text']
                                                logger.info(f"✅ Resultado final capturado: {len(final_response)} chars")
                                                
                        except json.JSONDecodeError as e:
                            logger.warning(f"⚠️  Recebida linha ou estrutura JSON inválida: {line[:100]}")
                            continue
                    
                    # Return the final response
                    if final_response:
                        logger.info(f"✅ Received response from {agent_name}: {len(final_response)} characters")
                        return final_response
                    else:
                        logger.warning(f"⚠️  No final_response artifact found in stream")
                        return "Nenhum resultado textual foi retornado."
                        
        except httpx.TimeoutException:
            logger.error(f"⏱️  Timeout sending message to {agent_name}")
            return f"{{\"error\": \"Timeout comunicando com {agent_name}\"}}"
        except Exception as e:
            logger.error(f"❌ Error sending message to {agent_name}: {e}", exc_info=True)
            return f"{{\"error\": \"Erro: {str(e)}\"}}"

# Global instance
_remote_connections = None

def get_remote_connections() -> RemoteAgentConnections:
    """Get or create the global RemoteAgentConnections instance"""
    global _remote_connections
    if _remote_connections is None:
        _remote_connections = RemoteAgentConnections()
    return _remote_connections

