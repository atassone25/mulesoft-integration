"""
Salesforce tools - consolidated implementation.
Contains all Salesforce agent integrations for the ADK system.

Available tools:
- buscar_historico: Get client history from Salesforce
- buscar_produto: Search for products in Salesforce  
- oportunidades: Manage sales opportunities in Salesforce
"""

import asyncio
import os
import requests
import logging
from google.adk.tools import FunctionTool
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Standard logging for tools
import logging
logger = logging.getLogger(__name__)


class SalesforceClient:
    """Lightweight Salesforce client for ADK agent tools."""
    
    def __init__(self):
        self.base_url = os.getenv("SALESFORCE_BASE_URL")
        self.oauth_url = os.getenv("SALESFORCE_OAUTH_URL") 
        self.instance_endpoint = os.getenv("SALESFORCE_INSTANCE_ENDPOINT")
        self.client_id = os.getenv("SALESFORCE_CLIENT_ID")
        self.client_secret = os.getenv("SALESFORCE_CLIENT_SECRET")
        
        # Agent IDs for different tools
        self.agent_ids = {
            "buscar_historico": os.getenv("SALESFORCE_AGENT_BUSCAR_HISTORICO"),
            "buscar_produto": os.getenv("SALESFORCE_AGENT_BUSCAR_PRODUTO"),
            "oportunidades": os.getenv("SALESFORCE_AGENT_OPORTUNIDADES")
        }
        
        self.access_token: Optional[str] = None
        self.sessions: dict = {}  # Store session IDs per agent
    
    def get_access_token(self) -> bool:
        """Get Salesforce access token."""
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(self.oauth_url, data=payload, timeout=30)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            return bool(self.access_token)
        except Exception:
            return False
    
    def start_session(self, agent_type: str) -> bool:
        """Start session with specified Salesforce agent."""
        if not self.access_token or agent_type not in self.agent_ids:
            return False
            
        agent_id = self.agent_ids[agent_type]
        if not agent_id:
            return False
            
        url = f"{self.base_url}/agents/{agent_id}/sessions"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        body = {
            "externalSessionKey": f"{agent_type}-session",
            "instanceConfig": {"endpoint": self.instance_endpoint},
            "variables": [],
            "streamingCapabilities": {"chunkTypes": ["Text"]},
            "bypassUser": True
        }
        
        try:
            response = requests.post(url, headers=headers, json=body, timeout=30)
            response.raise_for_status()
            session_data = response.json()
            session_id = session_data.get("sessionId")
            if session_id:
                self.sessions[agent_type] = session_id
                return True
            return False
        except Exception:
            return False
    
    def send_message(self, agent_type: str, message: str) -> Optional[str]:
        """Send message to specified Salesforce agent."""
        if not self.access_token or agent_type not in self.sessions:
            return None
            
        session_id = self.sessions[agent_type]
        url = f"{self.base_url}/sessions/{session_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        body = {
            "message": {
                "sequenceId": 1,
                "type": "Text", 
                "text": message
            },
            "variables": []
        }
        
        try:
            response = requests.post(url, headers=headers, json=body, timeout=60)
            response.raise_for_status()
            response_data = response.json()
            
            messages = response_data.get("messages", [])
            if messages and len(messages) > 0:
                return messages[0].get("message", "")
            return None
        except Exception:
            return None
    
    def call_agent(self, agent_type: str, query: str) -> Optional[str]:
        """Complete flow: authenticate, start session, send message."""
        if not self.get_access_token():
            return None
        if not self.start_session(agent_type):
            return None
        return self.send_message(agent_type, query)


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

async def buscar_historico(query: str) -> str:
    """
    Get client history from Salesforce buscar_historico agent.
    
    Args:
        query: User query containing client name, CNPJ, or other search terms
        
    Returns:
        Client history response from Salesforce agent
    """
    text = (query or "").strip()
    if not text:
        return "Informe o nome do cliente ou CNPJ para buscar o histórico."

    try:
        # Log tool usage
        logger.info(f"🔧 TOOL: buscar_historico({text[:50]}{'...' if len(text) > 50 else ''})")
        
        client = SalesforceClient()
        response = await asyncio.get_event_loop().run_in_executor(
            None, 
            client.call_agent, 
            "buscar_historico",
            text
        )
        
        if response:
            return response
        else:
            return "Não foi possível obter o histórico do cliente. Verifique as credenciais e tente novamente."
            
    except Exception as e:
        return f"Erro ao consultar histórico do cliente: {str(e)}"


async def buscar_produto(query: str) -> str:
    """
    Search for products in Salesforce using buscar_produto agent.
    
    Args:
        query: Product search query (name, category, specifications, etc.)
        
    Returns:
        Product search results from Salesforce agent
    """
    text = (query or "").strip()
    if not text:
        return "Informe o nome do produto ou características para buscar."

    try:
        logger.info(f"🔧 TOOL: buscar_produto({text[:50]}{'...' if len(text) > 50 else ''})")
        
        client = SalesforceClient()
        response = await asyncio.get_event_loop().run_in_executor(
            None, 
            client.call_agent, 
            "buscar_produto",
            text
        )
        
        if response:
            return response
        else:
            return "Não foi possível encontrar produtos. Verifique os critérios de busca e tente novamente."
            
    except Exception as e:
        return f"Erro ao buscar produtos: {str(e)}"


async def oportunidades(query: str) -> str:
    """
    Manage sales opportunities using Salesforce oportunidades agent.
    
    Args:
        query: Opportunity query (create, update, search opportunities)
        
    Returns:
        Opportunity management response from Salesforce agent
    """
    text = (query or "").strip()
    if not text:
        return "Informe os detalhes da oportunidade (criar, atualizar, ou consultar)."

    try:
        logger.info(f"🔧 TOOL: oportunidades({text[:50]}{'...' if len(text) > 50 else ''})")
        
        client = SalesforceClient()
        response = await asyncio.get_event_loop().run_in_executor(
            None, 
            client.call_agent, 
            "oportunidades",
            text
        )
        
        if response:
            return response
        else:
            return "Não foi possível processar a solicitação de oportunidade. Tente novamente."
            
    except Exception as e:
        return f"Erro ao gerenciar oportunidades: {str(e)}"


# ============================================================================
# TOOL INSTANCES - Export these for use in agents
# ============================================================================

buscar_historico_tool = FunctionTool(func=buscar_historico)
buscar_produto_tool = FunctionTool(func=buscar_produto)  
oportunidades_tool = FunctionTool(func=oportunidades)

# Legacy compatibility - keep the old name for existing agents
buscar_historico_tool_instance = buscar_historico_tool

# All tools list for easy import
all_salesforce_tools = [
    buscar_historico_tool,
    buscar_produto_tool, 
    oportunidades_tool
]
