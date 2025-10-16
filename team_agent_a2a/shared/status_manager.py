"""Status manager for A2A task updates - copied from c6flow"""
import logging
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, Message

logger = logging.getLogger(__name__)

class StatusManager:
    """Manages status updates for A2A tasks"""
    
    def __init__(self, updater: TaskUpdater):
        self.updater = updater
    
    def send_update(self, state: TaskState, message: Message = None, final: bool = False):
        """Send a status update synchronously"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a task
                asyncio.create_task(self.updater.update_status(state, message=message, final=final))
            else:
                # If no loop, run synchronously
                loop.run_until_complete(self.updater.update_status(state, message=message, final=final))
        except Exception as e:
            logger.error(f"Error sending status update: {e}")

