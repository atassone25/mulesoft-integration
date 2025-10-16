"""A2A Server for Data AI Agent - FIXED VERSION with direct Starlette routing"""
import os
import logging
import uvicorn
import json
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai

# Imports do Starlette
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import StreamingResponse, JSONResponse
from starlette.requests import Request

# Imports do A2A
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, SendMessageRequest
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.events.event_queue import EventQueue
from a2a.server.agent_execution import RequestContext

# Imports do ADK
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService

# Imports locais
from data_ai_agent.agent import root_agent
from data_ai_agent.agent_executor import DataAIAgentExecutor

# --- Configurações Iniciais ---
load_dotenv()
genai.configure()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

host = os.environ.get("A2A_HOST", "localhost")
port = int(os.environ.get("DATA_AI_AGENT_PORT", 10001))
PUBLIC_URL = os.environ.get("DATA_AI_AGENT_URL", f"http://{host}:{port}")

# Global executor (will be initialized in main)
executor = None
agent_card = None

# --- Stream Generator ---
async def stream_generator(event_queue):
    """Generator que consome eventos da fila e os transforma em strings JSON para o stream."""
    try:
        while True:
            # Use the correct API based on EventQueue implementation
            event = await event_queue.dequeue_event()
            if event is None:
                logger.info("📌 No more events, closing stream")
                break
            event_dict = event.model_dump(by_alias=True, exclude_none=True)
            yield json.dumps(event_dict) + "\n"
            event_queue.task_done()
            # Check if this is a final event (status updates have a 'final' field at event level)
            if hasattr(event, 'final') and event.final:
                logger.info("📌 Final event sent, closing stream")
                break
    except asyncio.CancelledError:
        logger.info("Stream generator was cancelled")
    finally:
        logger.info("Stream generator closed")

# --- Route Handlers ---
async def get_agent_card(request: Request):
    """Returns the agent card"""
    logger.info("📋 Agent card requested")
    return JSONResponse(agent_card.model_dump(by_alias=True, exclude_none=True))

async def handle_message(request: Request):
    """Handles message/send requests with streaming support"""
    global executor
    
    accept_header = request.headers.get("accept", "application/json")
    logger.info(f"📨 Message request received, Accept: {accept_header}")
    
    try:
        body = await request.json()
        logger.debug(f"📦 Request body: {json.dumps(body, indent=2)[:500]}")
        
        # Validate it's a proper A2A request
        if body.get("method") != "message/send":
            logger.warning(f"⚠️  Invalid method: {body.get('method')}")
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {"code": -32601, "message": "Method not found"}
            }, status_code=400)
        
        message_request = SendMessageRequest.model_validate(body)
        
        # Check if streaming is requested
        if "application/x-ndjson" in accept_header:
            logger.info("🌊 Streaming request detected")
            
            # 1. Create event queue
            event_queue = EventQueue()
            
            # 2. Create request context from the request params
            context = RequestContext(
                request=message_request.params,
                task_id=message_request.params.message.task_id,
                context_id=message_request.params.message.context_id
            )
            logger.info(f"✅ Context created: task_id={context.task_id}, context_id={context.context_id}")
            
            # 3. Start agent executor as background task
            asyncio.create_task(executor.execute(context, event_queue))
            logger.info(f"🚀 Agent executor task started in background")
            
            # 4. Return streaming response immediately
            return StreamingResponse(
                stream_generator(event_queue),
                media_type="application/x-ndjson"
            )
        else:
            # Non-streaming request (not typically used but supported)
            logger.info("📄 Synchronous request detected")
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {"code": -32000, "message": "Synchronous mode not fully implemented"}
            })
            
    except Exception as e:
        logger.error(f"❌ Error processing request: {e}", exc_info=True)
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id") if 'body' in locals() else None,
            "error": {"code": -32000, "message": str(e)}
        }, status_code=500)

def create_app():
    """Creates the Starlette application with custom routing"""
    global agent_card
    
    logger.info("--- Starting Data AI Agent A2A Server (FIXED) ---")
    
    # 1. Runner e componentes ADK
    runner = Runner(
        app_name=root_agent.name,
        agent=root_agent,
        session_service=InMemorySessionService(),
        artifact_service=InMemoryArtifactService(),
        memory_service=InMemoryMemoryService(),
    )
    
    # 2. Agent Card
    supported_content_types = ["text", "text/plain"]
    capabilities = AgentCapabilities(streaming=True)
    skill = AgentSkill(
        id="search_b2b_products",
        name="Search B2B Products and Offers",
        description="Searches B2B products and offers from Vertex AI Search datastore",
        tags=['products', 'offers', 'b2b', 'search', 'vertexai'],
    )
    agent_card = AgentCard(
        name="Data AI Agent",
        description="Agent that searches B2B products and offers from Vertex AI Search datastore",
        url=f"{PUBLIC_URL}",
        version="1.0.0",
        defaultInputModes=supported_content_types,
        defaultOutputModes=supported_content_types,
        capabilities=capabilities,
        skills=[skill],
    )
    
    # 3. Executor
    global executor
    executor = DataAIAgentExecutor(runner=runner, card=agent_card)
    logger.info("✅ DataAIAgentExecutor initialized")
    
    # 4. Create Starlette app with direct routing
    app = Starlette(
        debug=True,
        routes=[
            Route("/.well-known/agent-card.json", get_agent_card, methods=["GET"]),
            Route("/", handle_message, methods=["POST"]),
        ]
    )
    
    logger.info(f"✅ Starlette app created with custom routes")
    logger.info(f"Agent Card: {agent_card.name} - {agent_card.description}")
    
    return app

def main():
    """Função principal"""
    app = create_app()
    
    logger.info(f"🚀 Starting Data AI Agent server on {host}:{port}")
    logger.info(f"📍 Public URL: {PUBLIC_URL}")
    
    uvicorn.run(app, host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()

