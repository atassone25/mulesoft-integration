"""
Data and AI Tool - Returns Globo product names for contextualized offers
"""

import logging
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


async def data_and_ai(query: str) -> str:
    """
    Get product names from Data and AI system.
    
    Args:
        query: Product query or request for available products
        
    Returns:
        Available Globo products: Globo Reporter, Jornal Nacional, Futebol
    """
    try:
        logger.info(f"🔧 DATA AI TOOL: data_and_ai({query[:50] if query else 'empty'}{'...' if query and len(query) > 50 else ''})")
        
        # Return the three specified products
        products = [
            "Globo Reporter",
            "Jornal Nacional", 
            "Futebol"
        ]
        
        response = "Produtos disponíveis no sistema Data and AI:\n"
        for i, product in enumerate(products, 1):
            response += f"{i}. {product}\n"
        
        response += "\nEstes produtos podem ser incorporados em ofertas contextualizadas para clientes."
        
        return response
            
    except Exception as e:
        logger.error(f"Error in data_and_ai tool: {e}")
        return f"Erro ao consultar produtos Data and AI: {str(e)}"


# Create ADK FunctionTool instance
data_and_ai_tool = FunctionTool(func=data_and_ai)
