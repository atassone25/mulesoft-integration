"""
Salesforce A2A Tools - Google ADK tool implementations
Tools that use the A2A protocol to communicate with external Salesforce agents.
"""

import logging
from google.adk.tools import FunctionTool
from teams_agent.tools.a2a_client import get_salesforce_a2a_client

logger = logging.getLogger(__name__)


async def buscar_historico(query: str) -> str:
    """
    Get client history from Salesforce via A2A protocol.
    
    Args:
        query: User query containing client name, CNPJ, or other search terms
        
    Returns:
        Client history response from Salesforce agent
    """
    text = (query or "").strip()
    if not text:
        return "Informe o nome do cliente ou CNPJ para buscar o histórico."

    try:
        logger.info(f"🔧 A2A TOOL: buscar_historico({text[:50]}{'...' if len(text) > 50 else ''})")
        
        # Get A2A client and send message
        client = await get_salesforce_a2a_client()
        response = await client.buscar_historico(text)
        
        return response
            
    except Exception as e:
        logger.error(f"Error in A2A buscar_historico: {e}")
        return f"Erro ao consultar histórico do cliente via A2A: {str(e)}"


async def buscar_produto(query: str) -> str:
    """
    Search for products in Salesforce via A2A protocol.
    
    Args:
        query: Product search query (name, category, specifications, etc.)
        
    Returns:
        Product search results from Salesforce agent
    """
    text = (query or "").strip()
    if not text:
        return "Informe o nome do produto ou características para buscar."

    try:
        logger.info(f"🔧 A2A TOOL: buscar_produto({text[:50]}{'...' if len(text) > 50 else ''})")
        
        # Get A2A client and send message
        client = await get_salesforce_a2a_client()
        response = await client.buscar_produto(text)
        
        return response
            
    except Exception as e:
        logger.error(f"Error in A2A buscar_produto: {e}")
        return f"Erro ao buscar produtos via A2A: {str(e)}"


async def oportunidades(query: str) -> str:
    """
    Manage sales opportunities via A2A protocol.
    
    Args:
        query: Opportunity query (create, update, search opportunities)
        
    Returns:
        Opportunity management response from Salesforce agent
    """
    text = (query or "").strip()
    if not text:
        return "Informe os detalhes da oportunidade (criar, atualizar, ou consultar)."

    try:
        logger.info(f"🔧 A2A TOOL: oportunidades({text[:50]}{'...' if len(text) > 50 else ''})")
        
        # Get A2A client and send message
        client = await get_salesforce_a2a_client()
        response = await client.oportunidades(text)
        
        return response
            
    except Exception as e:
        logger.error(f"Error in A2A oportunidades: {e}")
        return f"Erro ao gerenciar oportunidades via A2A: {str(e)}"


# Create ADK FunctionTool instances
buscar_historico_tool = FunctionTool(func=buscar_historico)
buscar_produto_tool = FunctionTool(func=buscar_produto)
oportunidades_tool = FunctionTool(func=oportunidades)

# All tools list for easy import
all_salesforce_a2a_tools = [
    buscar_historico_tool,
    buscar_produto_tool,
    oportunidades_tool
]
