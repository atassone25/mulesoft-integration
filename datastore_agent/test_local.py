#!/usr/bin/env python3
"""
Local test script for the datastore agent
Test the agent locally before deploying to Agent Engine
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_datastore_agent():
    """Test the datastore agent locally"""
    
    try:
        # Import the agent
        from datastore_agent.agent import root_agent as agent
        
        logger.info("✓ Agent imported successfully")
        logger.info(f"Agent name: {agent.name}")
        logger.info(f"Agent description: {agent.description}")
        logger.info(f"Tools available: {[tool.name for tool in agent.tools]}")
        
        # Create a test session
        logger.info("Creating test session...")
        from google.adk import Runner
        
        runner = Runner(agent)
        session = await runner.async_create_session(user_id="test_user")
        
        logger.info(f"✓ Session created: {session.id}")
        
        # Test queries
        test_queries = [
            "Search for B2B offers in the datastore",
            "What products are available?",
            "Find information about business services",
        ]
        
        for query in test_queries:
            logger.info(f"\n🔍 Testing query: '{query}'")
            
            try:
                response_events = []
                async for event in runner.async_stream_query(
                    user_id="test_user",
                    session_id=session.id,
                    message=query
                ):
                    response_events.append(event)
                
                if response_events:
                    logger.info("✅ Query successful!")
                    # Show response
                    for event in response_events:
                        if event.get('parts'):
                            for part in event['parts']:
                                if part.get('text'):
                                    print(f"Response: {part['text'][:200]}...")
                                    break
                else:
                    logger.warning("⚠️ No response received")
                    
            except Exception as query_error:
                logger.error(f"❌ Query failed: {query_error}")
        
        logger.info("\n✅ Local testing completed!")
        
    except Exception as e:
        logger.error(f"❌ Local test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_datastore_agent())
