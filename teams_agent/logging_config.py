"""
Logging configuration for ADK agents.
Provides comprehensive logging for agent interactions, tool calls, and system events.
"""

import logging
import sys
from typing import Optional


def setup_adk_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure logging for ADK agents with console and optional file output.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log output
    """
    
    # Create formatter with emojis for better readability
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    loggers_config = {
        'salesforce_tools': logging.INFO,
        'adk_agent': logging.INFO,
        'contextualized_offer_agent': logging.INFO,
        'coordinator_agent': logging.INFO,
    }
    
    for logger_name, log_level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
    
    # Suppress noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger('adk_system')
    logger.info("🚀 ADK Agent System - Logging initialized")
    logger.info(f"📊 Log level: {level}")
    if log_file:
        logger.info(f"📁 Log file: {log_file}")


def log_agent_interaction(agent_name: str, user_input: str, agent_response: str) -> None:
    """
    Log agent interactions in a structured format.
    
    Args:
        agent_name: Name of the agent
        user_input: User's input message
        agent_response: Agent's response
    """
    logger = logging.getLogger('agent_interactions')
    
    logger.info(f"🤖 [{agent_name.upper()}] INTERACTION START")
    logger.info(f"👤 USER INPUT: {user_input}")
    logger.info(f"🤖 AGENT RESPONSE ({len(agent_response)} chars): {agent_response[:300]}{'...' if len(agent_response) > 300 else ''}")
    logger.info(f"✅ [{agent_name.upper()}] INTERACTION END")


def log_tool_call(tool_name: str, input_data: str, output_data: str, duration_ms: float = None) -> None:
    """
    Log tool calls with input/output data.
    
    Args:
        tool_name: Name of the tool being called
        input_data: Input data sent to the tool
        output_data: Output data returned by the tool
        duration_ms: Optional duration in milliseconds
    """
    logger = logging.getLogger('tool_calls')
    
    duration_str = f" ({duration_ms:.1f}ms)" if duration_ms else ""
    logger.info(f"🔧 [{tool_name.upper()}] TOOL CALL{duration_str}")
    logger.info(f"📥 INPUT: {input_data[:200]}{'...' if len(input_data) > 200 else ''}")
    logger.info(f"📤 OUTPUT: {output_data[:200]}{'...' if len(output_data) > 200 else ''}")


# Auto-initialize logging when module is imported
setup_adk_logging()
