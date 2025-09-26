#!/usr/bin/env python3
"""
ADK Datastore Agent Deployment Script - Following official documentation
https://google.github.io/adk-docs/deploy/agent-engine/

Simple agent for testing Vertex AI Search datastore connectivity.
"""

import vertexai
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Configuration from environment variables
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION") 
STAGING_BUCKET = f"gs://b2b-dev-vertex-agents"

if not PROJECT_ID or not LOCATION:
    raise ValueError("GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION must be set in .env file")

def get_agent():
    """Import and return the datastore agent"""
    from datastore_agent.agent import root_agent
    logger.info(f"✓ Imported datastore agent: {root_agent.name}")
    logger.info(f"  Description: {root_agent.description}")
    logger.info(f"  Tools: {[tool.name for tool in root_agent.tools]}")
    return root_agent

def main():
    """Deploy datastore agent following ADK documentation standard deployment process"""
    
    logger.info("Starting ADK datastore agent deployment...")
    logger.info(f"Project: {PROJECT_ID}")
    logger.info(f"Location: {LOCATION}")
    logger.info(f"Staging Bucket: {STAGING_BUCKET}")
    
    try:
        # Step 1: Initialize Vertex AI (as per ADK docs)
        logger.info("Step 1: Initialize Vertex AI...")
        vertexai.init(
            project=PROJECT_ID,
            location=LOCATION,
            staging_bucket=STAGING_BUCKET,
        )
        logger.info("✓ Vertex AI initialized successfully")
        
        # Step 2: Define your agent (import datastore agent)
        logger.info("Step 2: Define your agent...")
        agent = get_agent()
        
        # Step 3: Prepare the agent for deployment
        logger.info("Step 3: Prepare the agent for deployment...")
        from vertexai.preview import reasoning_engines
        
        adk_app = reasoning_engines.AdkApp(
            agent=agent,
            enable_tracing=True,  # Enable Google Cloud Trace
        )
        logger.info("✓ ADK App created with Cloud Trace enabled")
        
        # Step 4: Deploy to agent engine
        logger.info("Step 4: Deploy to agent engine...")
        logger.info("This may take several minutes...")
        
        from vertexai import agent_engines
        
        # Read requirements from datastore_agent/requirements.txt
        requirements_file = "datastore_agent/requirements.txt"
        requirements = []
        try:
            with open(requirements_file, 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            logger.info(f"✓ Loaded requirements from {requirements_file}: {requirements}")
        except FileNotFoundError:
            logger.warning(f"⚠️ Requirements file {requirements_file} not found, using minimal requirements")
            requirements = ["google-cloud-aiplatform[adk,agent_engines]"]
        
        # Prepare environment variables for deployment (same as teams_agent)
        env_vars = {
            "MODEL": os.getenv("MODEL", "gemini-2.0-flash"),
            "ADK_ENV": os.getenv("ADK_ENV", "dev"),
            "USE_VERTEX_MEMORY": os.getenv("USE_VERTEX_MEMORY", "FALSE"),  # Disabled for simple agent
            # A2A Configuration (keep same env vars available)
            "SALESFORCE_A2A_AGENT_BUSCAR_HISTORICO": os.getenv("SALESFORCE_A2A_AGENT_BUSCAR_HISTORICO"),
            "SALESFORCE_A2A_AGENT_BUSCAR_PRODUTO": os.getenv("SALESFORCE_A2A_AGENT_BUSCAR_PRODUTO"),
            "SALESFORCE_A2A_AGENT_OPORTUNIDADES": os.getenv("SALESFORCE_A2A_AGENT_OPORTUNIDADES"),
            "A2A_AUTH_USERNAME": os.getenv("A2A_AUTH_USERNAME"),
            "A2A_AUTH_PASSWORD": os.getenv("A2A_AUTH_PASSWORD"),
            # Salesforce Configuration
            "SALESFORCE_CLIENT_ID": os.getenv("SALESFORCE_CLIENT_ID"),
            "SALESFORCE_CLIENT_SECRET": os.getenv("SALESFORCE_CLIENT_SECRET"),
        }
        
        # Filter out None values
        env_vars = {k: v for k, v in env_vars.items() if v is not None}
        logger.info(f"✓ Environment variables prepared for deployment: {list(env_vars.keys())}")
        
        remote_app = agent_engines.create(
            agent_engine=adk_app,
            display_name="Datastore Test Agent",
            description="Simple agent for testing Vertex AI Search datastore connectivity (ma014-datastore-oferta_b2b)",
            requirements=requirements,
            env_vars=env_vars
        )
        
        logger.info("✅ Datastore agent deployed successfully!")
        logger.info(f"Resource Name: {remote_app.resource_name}")
        
        print("\n" + "="*70)
        print("🎉 DATASTORE AGENT DEPLOYMENT SUCCESSFUL!")
        print("="*70)
        print(f"Agent Name: Datastore Test Agent")
        print(f"Resource Name: {remote_app.resource_name}")
        print(f"Project: {PROJECT_ID}")
        print(f"Location: {LOCATION}")
        print(f"Staging Bucket: {STAGING_BUCKET}")
        print(f"Cloud Trace: ✅ ENABLED")
        print(f"Datastore: ma014-datastore-oferta_b2b")
        print(f"Tools: Vertex AI Search")
        print("="*70)
        
        # Test the deployed agent
        logger.info("Testing deployed datastore agent...")
        try:
            # Create a test session
            test_session = remote_app.create_session(user_id="test_user")
            logger.info(f"✓ Test session created: {test_session['id']}")
            
            # Send a simple test message to test datastore connectivity
            logger.info("Sending test message to search datastore...")
            response_events = list(remote_app.stream_query(
                user_id="test_user",
                session_id=test_session["id"],
                message="Search for any B2B offers or products available in the datastore"
            ))
            
            if response_events:
                logger.info("✓ Datastore agent responded successfully!")
                print(f"\n✅ Test successful - Datastore connection working!")
                
                # Show the response
                for event in response_events:
                    if event.get('parts'):
                        for part in event['parts']:
                            if part.get('text'):
                                print(f"Agent response: {part['text'][:300]}...")
                                break
            else:
                logger.warning("⚠️ Agent deployed but test response was empty")
                
        except Exception as test_error:
            logger.warning(f"⚠️ Agent deployed successfully but test failed: {test_error}")
            print(f"\n⚠️ Agent deployed but initial test failed: {test_error}")
        
        return remote_app
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        print(f"❌ Deployment failed: {e}")
        import traceback
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    deployed_app = main()
    if deployed_app:
        print(f"\n📋 Save this resource name for future reference:")
        print(f"   {deployed_app.resource_name}")
        print(f"\n💡 Next steps:")
        print(f"   1. Test datastore queries in the Vertex AI console")
        print(f"   2. View traces in Cloud Trace: https://console.cloud.google.com/traces/list?project={PROJECT_ID}")
        print(f"   3. Try different search queries to test datastore connectivity")
        print(f"   4. Monitor search performance and results")
        print(f"   5. Verify Vertex AI Search tool is working correctly")
    else:
        print(f"\n❌ Deployment failed. Check the logs above for details.")
        print(f"   Common issues:")
        print(f"   - Incorrect datastore ID or permissions")
        print(f"   - Missing Vertex AI Search API enablement")
        print(f"   - Network connectivity issues")
