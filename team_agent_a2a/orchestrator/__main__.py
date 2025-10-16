"""Entry point for ADK run web orchestrator"""
from orchestrator.agent import root_agent

# This allows `adk run web orchestrator` to work
__all__ = ['root_agent']

