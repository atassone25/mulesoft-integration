import requests
import time
import os
import uuid
import base64
import json
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class SalesforceAgentManager:
    def __init__(self):
        # A2A agent endpoints (JSON-RPC protocol)
        self.agents = {
            "oportunidades": os.getenv("SALESFORCE_A2A_AGENT_OPORTUNIDADES"),
            "buscar_produto": os.getenv("SALESFORCE_A2A_AGENT_BUSCAR_PRODUTO"),
            "buscar_historico": os.getenv("SALESFORCE_A2A_AGENT_BUSCAR_HISTORICO")
        }
        
        # A2A authentication (Basic auth)
        self.auth_username = os.getenv("A2A_AUTH_USERNAME")
        self.auth_password = os.getenv("A2A_AUTH_PASSWORD")
        
        # Create Basic auth header
        if self.auth_username and self.auth_password:
            auth_token = base64.b64encode(f"{self.auth_username}:{self.auth_password}".encode()).decode()
            self.auth_header = f"Basic {auth_token}"
        else:
            self.auth_header = None
        
        # Context management for A2A sessions
        self.context_ids: Dict[str, str] = {}
        self.context_timestamps: Dict[str, float] = {}
        self.context_timeout_hours = 2  # Contexts expire after 2 hours
    
    def _generate_context_id(self) -> str:
        """Generate a unique context ID with timestamp"""
        timestamp = int(time.time() * 1000)
        unique_id = str(uuid.uuid4())[:8]
        return f"ctx-{timestamp}-{unique_id}"
    
    def _generate_message_id(self) -> str:
        """Generate a unique message ID"""
        return f"msg-{int(time.time() * 1000)}"
    
    def _is_context_expired(self, agent_name: str) -> bool:
        """Check if a context has expired"""
        if agent_name not in self.context_timestamps:
            return True
        
        context_time = self.context_timestamps[agent_name]
        current_time = time.time()
        hours_elapsed = (current_time - context_time) / 3600
        
        return hours_elapsed >= self.context_timeout_hours
    
    def _clear_expired_context(self, agent_name: str):
        """Clear expired context data"""
        if agent_name in self.context_ids:
            del self.context_ids[agent_name]
        if agent_name in self.context_timestamps:
            del self.context_timestamps[agent_name]
    
    def check_credentials(self) -> bool:
        """Check if A2A credentials are available"""
        if not self.auth_header:
            print("✗ Error: No A2A credentials available. Check A2A_AUTH_USERNAME and A2A_AUTH_PASSWORD environment variables")
            return False
        
        print("✓ A2A credentials are available")
        return True
    
    def start_context(self, agent_name: str) -> bool:
        """Initialize a context for the specified agent"""
        if agent_name not in self.agents:
            print(f"✗ Error: Agent '{agent_name}' does not exist. Available: {list(self.agents.keys())}")
            return False
        
        if not self.check_credentials():
            return False
        
        # Generate new context ID
        context_id = self._generate_context_id()
        self.context_ids[agent_name] = context_id
        self.context_timestamps[agent_name] = time.time()
        
        print(f"✓ Context initialized for '{agent_name}': {context_id}")
        return True
    
    def send_message(self, agent_name: str, message: str, max_retries: int = 2) -> Optional[str]:
        """Sends a message to the agent using A2A JSON-RPC protocol"""
        if agent_name not in self.agents:
            print(f"✗ Error: Agent '{agent_name}' does not exist. Available: {list(self.agents.keys())}")
            return None
        
        if not self.check_credentials():
            return None
        
        agent_url = self.agents[agent_name]
        if not agent_url:
            print(f"✗ Error: No URL configured for agent '{agent_name}'")
            return None
        
        # Check if context exists and is not expired
        if agent_name not in self.context_ids or self._is_context_expired(agent_name):
            if agent_name in self.context_ids:
                print(f"⚠️  Context for '{agent_name}' has expired, creating new context...")
                self._clear_expired_context(agent_name)
            
            if not self.start_context(agent_name):
                return None
        
        # Retry logic for handling context expiration during message sending
        for attempt in range(max_retries + 1):
            # Get current context ID (may be updated during retries)
            context_id = self.context_ids[agent_name]
            message_id = self._generate_message_id()
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            }
            
            # A2A JSON-RPC payload
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "message/send",
                "params": {
                    "contextId": context_id,
                    "message": {
                        "role": "user",
                        "parts": [{"kind": "text", "text": message}],
                        "contextId": context_id,
                        "messageId": message_id
                    },
                    "metadata": {}
                }
            }
            
            try:
                print(f"🚀 Sending message to '{agent_name}' (contextId: {context_id})")
                response = requests.post(agent_url, headers=headers, json=payload)
                
                # Check for context expiration error (500 with "not found (404)" in error message)
                if response.status_code == 500 and attempt < max_retries:
                    try:
                        error_data = response.json()
                        error_message = error_data.get("error", {}).get("message", "")
                        
                        if "not found (404)" in error_message:
                            print(f"🔄 Context expired (attempt {attempt + 1}/{max_retries + 1}), generating new contextId...")
                            
                            # Generate new context ID and message ID directly (like in oportunidades_test.py)
                            new_context_id = self._generate_context_id()
                            new_message_id = self._generate_message_id()
                            
                            # Update our internal context tracking
                            self.context_ids[agent_name] = new_context_id
                            self.context_timestamps[agent_name] = time.time()
                            
                            print(f"✓ Generated new contextId: {new_context_id}")
                            continue
                    except:
                        pass
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check for JSON-RPC error
                    if "error" in result:
                        print(f"✗ A2A JSON-RPC error: {result['error']}")
                        return None
                    
                    # Extract the agent's response
                    response_text = "No response received from agent"
                    if 'result' in result and 'status' in result['result'] and 'message' in result['result']['status']:
                        agent_message = result['result']['status']['message']
                        if 'parts' in agent_message and agent_message['parts']:
                            response_text = agent_message['parts'][0].get('text', '')
                    
                    print(f"📨 Response from '{agent_name}':")
                    print(f"{response_text}")
                    return response_text
                else:
                    print(f"✗ HTTP Error {response.status_code}: {response.text}")
                    if attempt == max_retries:
                        return None
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    print(f"🔄 Request failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    # Try creating a new context on request errors
                    self._clear_expired_context(agent_name)
                    if not self.start_context(agent_name):
                        return None
                    continue
                else:
                    print(f"✗ Error sending message to '{agent_name}' after {max_retries + 1} attempts: {e}")
                    return None
        
        return None
    
    def get_available_agents(self) -> list:
        """Returns the list of available agents"""
        return list(self.agents.keys())
    
    def get_status(self) -> dict:
        """Returns the current status of the manager"""
        context_status = {}
        current_time = time.time()
        
        for agent_name in self.context_ids.keys():
            if agent_name in self.context_timestamps:
                context_time = self.context_timestamps[agent_name]
                hours_elapsed = (current_time - context_time) / 3600
                is_expired = hours_elapsed >= self.context_timeout_hours
                
                context_status[agent_name] = {
                    "context_id": self.context_ids[agent_name],
                    "hours_elapsed": round(hours_elapsed, 2),
                    "is_expired": is_expired,
                    "expires_in_hours": round(self.context_timeout_hours - hours_elapsed, 2) if not is_expired else 0
                }
        
        return {
            "has_credentials": bool(self.auth_header),
            "active_contexts": list(self.context_ids.keys()),
            "available_agents": list(self.agents.keys()),
            "context_details": context_status,
            "context_timeout_hours": self.context_timeout_hours,
            "auth_method": "A2A Basic Authentication"
        }
    
    def complete_flow(self, agent_name: str, message: str) -> Optional[str]:
        """Executes the complete flow: check credentials, start context and send message"""
        print(f"🚀 Starting complete A2A flow for '{agent_name}'...")
        
        # Step 1: Check credentials
        if not self.check_credentials():
            return None
        
        # Step 2: Start context
        if not self.start_context(agent_name):
            return None
        
        # Step 3: Send message
        return self.send_message(agent_name, message)

    def interactive_mode(self):
        """Interactive terminal mode for A2A agent interaction"""
        print("\n=== Salesforce A2A Agent Manager - Interactive Mode ===")
        print(f"Available A2A agents: {', '.join(self.get_available_agents())}")
        print("Commands: 'quit' to exit, 'status' to check status, 'help' for help\n")
        
        current_agent = None
        
        while True:
            try:
                if current_agent:
                    # In conversation mode
                    message = input(f"💬 [{current_agent}] Your message: ").strip()
                    
                    if message.lower() == 'back':
                        current_agent = None
                        print("Switched back to agent selection mode\n")
                        continue
                    elif message.lower() in ['quit', 'exit']:
                        print("Goodbye!")
                        break
                    elif message:
                        print(f"\n🚀 Sending A2A message to {current_agent}...")
                        response = self.send_message(current_agent, message)
                        if response:
                            print("\n" + "="*30 + "\n")
                else:
                    # Agent selection mode
                    command = input("🤖 Enter command (or agent name): ").strip().lower()
                    
                    if command == 'quit' or command == 'exit':
                        print("Goodbye!")
                        break
                    elif command == 'status':
                        status = self.get_status()
                        print(f"A2A Status: {json.dumps(status, indent=2)}")
                    elif command == 'help':
                        self.show_help()
                    elif command in self.agents:
                        # Start conversation with agent
                        message = input(f"💬 Enter your first message for {command}: ")
                        if message.strip():
                            print(f"\n🚀 Starting A2A conversation with {command}...")
                            
                            # Initialize context if needed
                            if not self.check_credentials():
                                continue
                            
                            if command not in self.context_ids:
                                if not self.start_context(command):
                                    continue
                            
                            response = self.send_message(command, message)
                            if response:
                                current_agent = command
                    else:
                        print(f"Unknown command or agent: {command}")
                        print(f"Available: {', '.join(self.get_available_agents())}, status, help, quit")
                        
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def show_help(self):
        """Shows help information"""
        print("\n=== A2A HELP ===")
        print("Commands:")
        print("  - <agent_name>: Start A2A conversation with agent")
        print("  - status: Show current A2A status")
        print("  - help: Show this help")
        print("  - quit/exit: Exit interactive mode")
        print(f"\nAvailable A2A agents: {', '.join(self.get_available_agents())}")
        print("\nConversation mode:")
        print("  - Once in conversation with an agent, keep typing messages")
        print("  - Each message uses A2A JSON-RPC protocol")
        print("  - Type 'back' to return to agent selection")
        print("  - Type 'quit' to exit completely")
        print("\nExample workflow:")
        print("  1. Type: oportunidades")
        print("  2. Enter: Criar nova oportunidade de venda para empresa ABC")
        print("  3. Continue the conversation with follow-up messages")
        print("  4. Type 'back' when done to switch agents")
        print("\nA2A Features:")
        print("  - Context-aware conversations")
        print("  - Automatic context management")
        print("  - Retry logic for expired contexts")
        print("  - Basic authentication with Salesforce\n")


# Usage examples
if __name__ == "__main__":
    manager = SalesforceAgentManager()
    
    # Interactive mode
    manager.interactive_mode()
    
    # Programmatic usage examples:
    # response = manager.complete_flow("oportunidades", "Criar nova oportunidade de venda para empresa ABC")
    # 
    # Step by step:
    # manager.check_credentials()
    # manager.start_context("buscar_historico")
    # manager.send_message("buscar_historico", "Buscar histórico do cliente ABC")
    # manager.send_message("buscar_historico", "Mostrar últimas compras")