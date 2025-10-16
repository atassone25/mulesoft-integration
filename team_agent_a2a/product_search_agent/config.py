"""Configuration for ADK to use Vertex AI - loads from parent .env"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def configure_adk_for_vertexai():
    """Configure ADK to use Vertex AI backend by loading parent .env"""
    # Load .env from parent mulesoft-integration directory
    parent_dir = Path(__file__).parent.parent.parent
    env_file = parent_dir / '.env'
    
    if env_file.exists():
        load_dotenv(env_file)
        logger.info(f"Loaded .env from: {env_file}")
    else:
        logger.warning(f"No .env file found at: {env_file}")
    
    # Verify Vertex AI is configured
    use_vertexai = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', '').upper()
    project = os.getenv('GOOGLE_CLOUD_PROJECT', '').strip('"')
    location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1').strip('"')
    
    if use_vertexai in ['TRUE', '1', 'YES']:
        logger.info(f"✅ ADK configured to use Vertex AI: project={project}, location={location}")
    else:
        logger.warning("⚠️  GOOGLE_GENAI_USE_VERTEXAI not set to TRUE")
    
    return project, location

# Configure on module import
configure_adk_for_vertexai()

