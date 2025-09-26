# """ADK Configuration for Memory Service Integration."""

# import os
# from google.adk.memory import InMemoryMemoryService, VertexAiMemoryBankService
# import logging

# logger = logging.getLogger(__name__)

# def get_memory_service():
#     """
#     Get the configured memory service based on environment variables.
#     This function can be used by ADK runners to get the appropriate memory service.
    
#     Based on ADK documentation: https://google.github.io/adk-docs/sessions/memory/
#     """
#     use_vertex = os.getenv("USE_VERTEX_MEMORY", "").lower() in ("1", "true", "yes")
    
#     if not use_vertex:
#         logger.info("Using InMemoryMemoryService (USE_VERTEX_MEMORY not enabled)")
#         return InMemoryMemoryService()

#     project = os.getenv("GOOGLE_CLOUD_PROJECT")
#     location = os.getenv("GOOGLE_CLOUD_LOCATION")
#     agent_engine_id = os.getenv("AGENT_ENGINE_ID")

#     if not (project and location and agent_engine_id):
#         logger.warning(
#             f"Missing required environment variables for VertexAiMemoryBankService: "
#             f"GOOGLE_CLOUD_PROJECT={project}, GOOGLE_CLOUD_LOCATION={location}, "
#             f"AGENT_ENGINE_ID={agent_engine_id}. Falling back to InMemoryMemoryService."
#         )
#         return InMemoryMemoryService()

#     try:
#         logger.info(f"Initializing VertexAiMemoryBankService with project={project}, location={location}, agent_engine_id={agent_engine_id}")
#         return VertexAiMemoryBankService(
#             project=project,
#             location=location,
#             agent_engine_id=agent_engine_id,
#         )
#     except Exception as e:
#         logger.error(f"Failed to initialize VertexAiMemoryBankService: {e}. Falling back to InMemoryMemoryService.")
#         return InMemoryMemoryService()

# def get_memory_service_uri():
#     """
#     Get the memory service URI for use with ADK web server --memory_service_uri flag.
#     Returns the appropriate URI format based on environment configuration.
#     """
#     use_vertex = os.getenv("USE_VERTEX_MEMORY", "").lower() in ("1", "true", "yes")
    
#     if not use_vertex:
#         return None  # Use default in-memory service
    
#     agent_engine_id = os.getenv("AGENT_ENGINE_ID")
#     if agent_engine_id:
#         return f"agentengine://{agent_engine_id}"
    
#     return None
