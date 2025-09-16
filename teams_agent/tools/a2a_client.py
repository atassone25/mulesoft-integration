"""
A2A Client for Salesforce Agent Integration
Based on A2A Protocol specification and Google ADK integration patterns.
"""

import asyncio
import logging
import os
import uuid
from typing import Optional, Dict, Any, List
import aiohttp
import base64
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class A2AClient:
    """
    A2A client implementation following the A2A protocol specification.
    
    This client communicates with external A2A-compatible agents using the
    standard A2A protocol methods like createTask, getTask, etc.
    """
    
    def __init__(self, url: str, auth_token: Optional[str] = None):
        """
        Initialize A2A client.
        
        Args:
            url: Base URL of the A2A agent endpoint
            auth_token: Authentication token for Bearer auth
        """
        self.url = url.rstrip('/')
        self.auth_token = auth_token
        self.session: Optional[aiohttp.ClientSession] = None
        self._tasks: Dict[str, Dict] = {}  # Local task cache
    
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for A2A requests."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        return headers
    
    def _get_headers_with_basic_auth(self, basic_auth_header: str) -> Dict[str, str]:
        """Get HTTP headers for A2A requests with Basic auth."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': basic_auth_header
        }
        
        return headers
    
    async def create_task(self, message: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create a new task following A2A protocol.
        
        Args:
            message: Message object with parts array
            metadata: Optional metadata for the task
            
        Returns:
            Task object with taskId and status
        """
        await self._ensure_session()
        
        task_id = str(uuid.uuid4())
        
        # A2A createTask payload
        payload = {
            "message": message,
            "metadata": metadata or {}
        }
        
        try:
            logger.info(f"🔧 A2A: Creating task {task_id}")
            
            async with self.session.post(
                f"{self.url}/tasks",
                headers=self._get_headers(),
                json=payload
            ) as response:
                
                if response.status == 201:
                    result = await response.json()
                    
                    # Store task locally for tracking
                    task = {
                        "taskId": result.get("taskId", task_id),
                        "status": result.get("status", "Pending"),
                        "message": message,
                        "metadata": metadata or {},
                        "created": result.get("created"),
                        "artifacts": result.get("artifacts", [])
                    }
                    
                    self._tasks[task["taskId"]] = task
                    logger.info(f"✅ A2A: Created task {task['taskId']}")
                    return task
                    
                else:
                    error_text = await response.text()
                    logger.error(f"❌ A2A createTask failed: HTTP {response.status}")
                    logger.error(f"Error: {error_text}")
                    raise Exception(f"Failed to create task: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Error creating A2A task: {e}")
            raise
    
    async def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Get task status following A2A protocol.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Updated task object
        """
        await self._ensure_session()
        
        try:
            async with self.session.get(
                f"{self.url}/tasks/{task_id}",
                headers=self._get_headers()
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Update local cache
                    self._tasks[task_id] = result
                    logger.debug(f"✅ A2A: Retrieved task {task_id}, status: {result.get('status')}")
                    return result
                    
                else:
                    error_text = await response.text()
                    logger.error(f"❌ A2A getTask failed: HTTP {response.status}")
                    raise Exception(f"Failed to get task: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Error getting A2A task {task_id}: {e}")
            raise
    
    async def wait_for_task(self, task_id: str, timeout: int = 30, poll_interval: float = 1.0) -> Dict[str, Any]:
        """
        Wait for task completion with polling.
        
        Args:
            task_id: ID of the task to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between polls in seconds
            
        Returns:
            Completed task object
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            task = await self.get_task(task_id)
            status = task.get("status", "Pending")
            
            if status in ["Completed", "Failed", "Cancelled"]:
                logger.info(f"✅ A2A: Task {task_id} finished with status: {status}")
                return task
            
            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                logger.warning(f"⏰ A2A: Task {task_id} timeout after {timeout}s")
                raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
            
            # Wait before next poll
            await asyncio.sleep(poll_interval)
    
    async def send_simple_message(self, text: str, basic_auth_header: Optional[str] = None) -> str:
        """
        Send a simple text message using A2A protocol (based on working simple_a2a_client.py).
        
        Args:
            text: Text message to send
            basic_auth_header: Optional Basic auth header to override Bearer auth
            
        Returns:
            Response text from the agent
        """
        try:
            # Use the working A2A message/send pattern
            result = await self.send_message_a2a(text, basic_auth_header)
            return result.get("response", "No response received from agent")
        except Exception as e:
            logger.error(f"❌ Error in send_simple_message: {e}")
            return f"Error: {str(e)}"
    
    async def send_message_a2a(self, message_text: str, basic_auth_header: Optional[str] = None, context_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send message using A2A protocol message/send method (based on working simple_a2a_client.py).
        
        Args:
            message_text: Text message to send
            basic_auth_header: Optional Basic auth header
            context_id: Optional context ID for conversation continuity
            
        Returns:
            Response from the agent
        """
        await self._ensure_session()
        
        # Generate IDs if not provided
        if not context_id:
            context_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        
        # A2A JSON-RPC message/send payload (based on working simple_a2a_client.py)
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
                            "text": message_text
                        }
                    ],
                    "contextId": context_id,
                    "messageId": message_id
                },
                "metadata": {}
            }
        }
        
        # Choose headers based on auth type
        if basic_auth_header:
            headers = self._get_headers_with_basic_auth(basic_auth_header)
        else:
            headers = self._get_headers()
        
        try:
            logger.info(f"🔧 A2A: Sending message via message/send")
            
            async with self.session.post(
                self.url,  # Use base URL for JSON-RPC
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    logger.info("✅ Message sent successfully!")
                    
                    # Check for JSON-RPC error
                    if "error" in result:
                        logger.error(f"❌ A2A JSON-RPC error: {result['error']}")
                        raise Exception(f"A2A error: {result['error']}")
                    
                    # Extract the agent's response (based on working simple_a2a_client.py)
                    response_text = "No response received from agent"
                    if 'result' in result and 'status' in result['result'] and 'message' in result['result']['status']:
                        agent_message = result['result']['status']['message']
                        if 'parts' in agent_message and agent_message['parts']:
                            response_text = agent_message['parts'][0].get('text', '')
                            logger.info(f"🤖 Agent response: {response_text}")
                    
                    return {
                        "status": "Completed",
                        "response": response_text,
                        "contextId": context_id,
                        "full_result": result
                    }
                    
                else:
                    error_text = await response.text()
                    logger.error(f"❌ A2A message/send failed: HTTP {response.status}")
                    logger.error(f"Error: {error_text}")
                    raise Exception(f"Failed to send message: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Error sending A2A message: {e}")
            raise
    
    async def wait_for_task_with_auth(self, task_id: str, basic_auth_header: Optional[str] = None, timeout: int = 30, poll_interval: float = 1.0) -> Dict[str, Any]:
        """
        Wait for task completion with polling and custom auth.
        
        Args:
            task_id: ID of the task to wait for
            basic_auth_header: Optional Basic auth header
            timeout: Maximum time to wait in seconds
            poll_interval: Time between polls in seconds
            
        Returns:
            Completed task object
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            task = await self.get_task_with_auth(task_id, basic_auth_header)
            status = task.get("status", "Pending")
            
            if status in ["Completed", "Failed", "Cancelled"]:
                logger.info(f"✅ A2A: Task {task_id} finished with status: {status}")
                return task
            
            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                logger.warning(f"⏰ A2A: Task {task_id} timeout after {timeout}s")
                raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
            
            # Wait before next poll
            await asyncio.sleep(poll_interval)
    
    async def get_task_with_auth(self, task_id: str, basic_auth_header: Optional[str] = None) -> Dict[str, Any]:
        """
        Get task status using A2A protocol tasks/get method.
        
        Args:
            task_id: ID of the task to retrieve
            basic_auth_header: Optional Basic auth header
            
        Returns:
            Updated task object
        """
        await self._ensure_session()
        
        # A2A JSON-RPC tasks/get payload according to specification
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/get",
            "params": {
                "taskId": task_id
            }
        }
        
        # Choose headers based on auth type
        if basic_auth_header:
            headers = self._get_headers_with_basic_auth(basic_auth_header)
        else:
            headers = self._get_headers()
        
        try:
            async with self.session.post(
                self.url,  # Use base URL for JSON-RPC
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Check for JSON-RPC error
                    if "error" in result:
                        logger.error(f"❌ A2A JSON-RPC error: {result['error']}")
                        raise Exception(f"A2A error: {result['error']}")
                    
                    # Extract task from result
                    task_data = result.get("result", {})
                    task = {
                        "taskId": task_data.get("taskId", task_id),
                        "status": task_data.get("status", {}).get("state", "Pending"),
                        "created": task_data.get("status", {}).get("created"),
                        "artifacts": task_data.get("artifacts", [])
                    }
                    
                    # Update local cache
                    self._tasks[task_id] = task
                    logger.debug(f"✅ A2A: Retrieved task {task_id}, status: {task.get('status')}")
                    return task
                    
                else:
                    error_text = await response.text()
                    logger.error(f"❌ A2A tasks/get failed: HTTP {response.status}")
                    raise Exception(f"Failed to get task: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Error getting A2A task {task_id}: {e}")
            raise
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("Closed A2A client session")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


class SalesforceA2AClient:
    """
    Specialized A2A client for Salesforce agents.
    
    This class provides a higher-level interface for communicating with
    Salesforce-specific A2A agents for different business functions.
    """
    
    def __init__(self):
        """Initialize Salesforce A2A client with configuration."""
        # Get configuration from environment
        self.auth_username = os.getenv("A2A_AUTH_USERNAME", "agentforce_dev")
        self.auth_password = os.getenv("A2A_AUTH_PASSWORD", "9229e770-767c-417b-a0b0-f0741243c589")
        
        # Create auth token for Basic authentication (not Bearer)
        auth_string = f"{self.auth_username}:{self.auth_password}"
        auth_bytes = auth_string.encode('ascii')
        auth_token = base64.b64encode(auth_bytes).decode('ascii')
        
        # Salesforce A2A agent endpoints - use Basic auth instead of Bearer
        self.agents = {
            "buscar_historico": A2AClient(
                url=os.getenv("SALESFORCE_A2A_AGENT_BUSCAR_HISTORICO", 
                            "https://agentforce-b2b-fv3b5q.3ch7y1.usa-e1.cloudhub.io/historico/historico"),
                auth_token=None  # We'll use Basic auth in headers instead
            ),
            "buscar_produto": A2AClient(
                url=os.getenv("SALESFORCE_A2A_AGENT_BUSCAR_PRODUTO", 
                            "https://agentforce-b2b-fv3b5q.3ch7y1.usa-e1.cloudhub.io/produtos/busca-produtos"),
                auth_token=None  # We'll use Basic auth in headers instead
            ),
            "oportunidades": A2AClient(
                url=os.getenv("SALESFORCE_A2A_AGENT_OPORTUNIDADES",
                            "https://agentforce-b2b-fv3b5q.3ch7y1.usa-e1.cloudhub.io/oportunidade/agentforce-agent"),
                auth_token=None  # We'll use Basic auth in headers instead
            )
        }
        
        # Store the Basic auth header for use in requests
        self.basic_auth_header = f'Basic {auth_token}'
    
    async def buscar_historico(self, query: str) -> str:
        """Get client history from Salesforce via A2A protocol."""
        try:
            logger.info(f"🔧 A2A: Searching client history")
            return await self.agents["buscar_historico"].send_simple_message(query, self.basic_auth_header)
        except Exception as e:
            logger.error(f"❌ Error in buscar_historico: {e}")
            return f"Erro ao consultar histórico do cliente: {str(e)}"
    
    async def buscar_produto(self, query: str) -> str:
        """Search for products in Salesforce via A2A protocol."""
        try:
            logger.info(f"🔧 A2A: Searching products")
            return await self.agents["buscar_produto"].send_simple_message(query, self.basic_auth_header)
        except Exception as e:
            logger.error(f"❌ Error in buscar_produto: {e}")
            return f"Erro ao buscar produtos: {str(e)}"
    
    async def oportunidades(self, query: str) -> str:
        """Manage opportunities in Salesforce via A2A protocol."""
        try:
            logger.info(f"🔧 A2A: Managing opportunities")
            return await self.agents["oportunidades"].send_simple_message(query, self.basic_auth_header)
        except Exception as e:
            logger.error(f"❌ Error in oportunidades: {e}")
            return f"Erro ao gerenciar oportunidades: {str(e)}"
    
    async def close_all(self):
        """Close all A2A client sessions."""
        for agent_name, client in self.agents.items():
            try:
                await client.close()
                logger.debug(f"Closed {agent_name} A2A client")
            except Exception as e:
                logger.warning(f"Error closing {agent_name} client: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_all()


# Global client instance for reuse
_salesforce_a2a_client: Optional[SalesforceA2AClient] = None


async def get_salesforce_a2a_client() -> SalesforceA2AClient:
    """Get or create global Salesforce A2A client instance."""
    global _salesforce_a2a_client
    if _salesforce_a2a_client is None:
        _salesforce_a2a_client = SalesforceA2AClient()
    return _salesforce_a2a_client


async def close_salesforce_a2a_client():
    """Close global Salesforce A2A client instance."""
    global _salesforce_a2a_client
    if _salesforce_a2a_client:
        await _salesforce_a2a_client.close_all()
        _salesforce_a2a_client = None
