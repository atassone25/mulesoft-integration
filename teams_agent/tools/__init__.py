"""Initialize the Salesforce A2A tools."""

from .salesforce_tools import all_salesforce_a2a_tools
from .a2a_client import get_salesforce_a2a_client, close_salesforce_a2a_client

__all__ = [
    'all_salesforce_a2a_tools', 
    'get_salesforce_a2a_client',
    'close_salesforce_a2a_client'
]
