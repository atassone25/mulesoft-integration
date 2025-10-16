"""Agent Executor for Product Search Agent - handles A2A task execution"""
import logging
import asyncio
import sys
import os

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from shared.status_manager import StatusManager
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import AgentCard, Part, TaskState, TextPart, Message
from google.adk.runners import Runner
from google.genai import types as genai_types
from google.adk.sessions.session import Session
from a2a.utils import new_agent_text_message

logger = logging.getLogger(__name__)

DEFAULT_USER_ID = 'self'

class ProductSearchAgentExecutor(AgentExecutor):
    """Executor for Product Search Agent A2A tasks"""
    
    def __init__(self, runner: Runner, card: AgentCard):
        super().__init__()
        self.runner = runner
        self.logger = logger
        self._card = card
        self.logger.info(f"ProductSearchAgentExecutor initialized for agent: {runner.agent.name}")

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        self.logger.info(f"Starting task execution {context.task_id} for context {context.context_id}")
        
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        status_manager = StatusManager(updater)
        self.logger.info("TaskUpdater and StatusManager initialized")
        
        initial_message = new_agent_text_message("Request received, starting product search...", context.context_id, context.task_id)
        self.logger.info("Sending initial 'working' status")
        status_manager.send_update(TaskState.working, message=initial_message)
        
        try:
            self.logger.info(f"Checking/Creating ADK session with ID: {context.context_id}")
            await self._upsert_session(context.context_id)
            self.logger.info(f"ADK session {context.context_id} ensured")

            self.logger.info("Extracting text from user message")
            parts_text_list = [
                part.root.text
                for part in context.message.parts
                if isinstance(part.root, TextPart)
            ]
            user_message = genai_types.UserContent(parts=parts_text_list)
            self.logger.info(f"User message processed: {parts_text_list[0][:100] if parts_text_list else 'empty'}...")
            
            self.logger.info("Starting runner.run_async to get agent response")
            async for event in self.runner.run_async(
                new_message=user_message,
                session_id=context.context_id,
                user_id=DEFAULT_USER_ID
            ):
                event_description = f"final_response={event.is_final_response()}"
                if event.content and event.content.parts:
                    has_tool_call = any(part.function_call for part in event.content.parts)
                    event_description += f", has_tool_call={has_tool_call}"
                self.logger.info(f"Event received from runner: {event_description}")
                
                if not event.content or not event.content.parts:
                    self.logger.warning("Event received without content or parts, skipping")
                    continue

                for part in event.content.parts:
                    if part.function_call:
                        tool_name = part.function_call.name
                        status_text = f"Executing product search: '{tool_name}'..."
                        self.logger.info(f"Sending status: {status_text}")
                        status_message = new_agent_text_message(status_text, context.context_id, context.task_id)
                        status_manager.send_update(TaskState.working, message=status_message)
                
                if event.is_final_response():
                    self.logger.info("Final response event detected")
                    final_text_parts = [part.text for part in event.content.parts if part.text]
                    
                    if final_text_parts:
                        final_text = " ".join(final_text_parts)
                        self.logger.info(f"Final response received: {final_text[:200]}...")
                        
                        final_parts = [Part(root=TextPart(text=final_text))]
                        self.logger.info("Adding final_response artifact")
                        await updater.add_artifact(final_parts, name="final_response")
                        self.logger.info("Artifact added successfully")
                        break

            self.logger.info("Sending final 'completed' status...")
            await updater.update_status(TaskState.completed, final=True)
            self.logger.info("Final 'completed' status sent successfully")

        except Exception as e:
            self.logger.error(f"Error in agent execution: {e}", exc_info=True)
            error_message = new_agent_text_message(f"An error occurred: {e}", context.context_id, context.task_id)
            self.logger.info("Sending final 'failed' status...")
            await updater.update_status(TaskState.failed, message=error_message, final=True)
            self.logger.info("Final 'failed' status sent successfully")

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        self.logger.info(f"Cancel request received for task: {context.task_id}")
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        status_manager = StatusManager(updater)
        self.logger.info(f"Sending 'canceled' status for task {context.task_id}")
        status_manager.send_update(TaskState.canceled, final=True)
        self.logger.info(f"Status 'canceled' for task {context.task_id} sent")

    async def _upsert_session(self, session_id: str) -> Session:
        self.logger.info(f"Looking for existing ADK session with ID: {session_id}")
        session = await self.runner.session_service.get_session(
            app_name=self.runner.agent.name,
            user_id=DEFAULT_USER_ID,
            session_id=session_id,
        )
        if session is None:
            self.logger.info(f"ADK session not found ({session_id}), creating new one")
            session = await self.runner.session_service.create_session(
                app_name=self.runner.agent.name,
                user_id=DEFAULT_USER_ID,
                session_id=session_id,
            )
            self.logger.info(f"New ADK session created with ID: {session_id}")
        else:
            self.logger.info(f"ADK session found: {session_id}")
            
        return session

