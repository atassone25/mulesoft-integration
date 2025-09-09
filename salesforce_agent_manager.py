import requests
import time
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class SalesforceAgentManager:
    def __init__(self):
        self.agents = {
            "oportunidades": os.getenv("SALESFORCE_AGENT_OPORTUNIDADES"),
            "buscar_produto": os.getenv("SALESFORCE_AGENT_BUSCAR_PRODUTO"),
            "buscar_historico": os.getenv("SALESFORCE_AGENT_BUSCAR_HISTORICO")
        }
        
        self.base_url = os.getenv("SALESFORCE_BASE_URL")
        self.oauth_url = os.getenv("SALESFORCE_OAUTH_URL")
        self.instance_endpoint = os.getenv("SALESFORCE_INSTANCE_ENDPOINT")
        
        self.client_id = os.getenv("SALESFORCE_CLIENT_ID")
        self.client_secret = os.getenv("SALESFORCE_CLIENT_SECRET")
        
        self.access_token: Optional[str] = None
        self.session_ids: Dict[str, str] = {}
    
    def get_credentials(self) -> bool:
        """Gets and stores the Salesforce access token"""
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(self.oauth_url, data=payload)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            
            if self.access_token:
                print(f"✓ Credentials obtained successfully")
                return True
            else:
                print("✗ Error: Could not obtain access_token")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Error getting credentials: {e}")
            return False
    
    def start_session(self, agent_name: str) -> bool:
        """Starts a session for the specified agent and saves its ID"""
        if agent_name not in self.agents:
            print(f"✗ Error: Agent '{agent_name}' does not exist. Available: {list(self.agents.keys())}")
            return False
        
        if not self.access_token:
            print("✗ Error: No credentials available. Run get_credentials() first")
            return False
        
        agent_id = self.agents[agent_name]
        url = f"{self.base_url}/agents/{agent_id}/sessions"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        body = {
            "externalSessionKey": "2b4a51fe-3ab5-4041-8468-c27730e1b9ac",
            "instanceConfig": {
                "endpoint": self.instance_endpoint
            },
            "variables": [],
            "streamingCapabilities": {
                "chunkTypes": ["Text"]
            },
            "bypassUser": True
        }
        
        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            
            session_data = response.json()
            session_id = session_data.get("sessionId")
            
            if session_id:
                self.session_ids[agent_name] = session_id
                print(f"✓ Session started for '{agent_name}': {session_id}")
                return True
            else:
                print(f"✗ Error: Could not obtain session_id for '{agent_name}'")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Error starting session for '{agent_name}': {e}")
            return False
    
    def send_message(self, agent_name: str, message: str) -> Optional[str]:
        """Sends a message to the agent, saves and returns the response"""
        if agent_name not in self.agents:
            print(f"✗ Error: Agent '{agent_name}' does not exist. Available: {list(self.agents.keys())}")
            return None
        
        if agent_name not in self.session_ids:
            print(f"✗ Error: No active session for '{agent_name}'. Run start_session() first")
            return None
        
        if not self.access_token:
            print("✗ Error: No credentials available. Run get_credentials() first")
            return None
        
        session_id = self.session_ids[agent_name]
        url = f"{self.base_url}/sessions/{session_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        timestamp = int(time.time() * 1000)
        
        body = {
            "message": {
                "sequenceId": timestamp,
                "type": "Text",
                "text": message
            },
            "variables": []
        }
        
        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            
            response_data = response.json()
            
            # Extract the response message
            messages = response_data.get("messages", [])
            if messages and len(messages) > 0:
                response = messages[0].get("message", "")
                print(f"📨 Response from '{agent_name}':")
                print(f"{response}")
                return response
            else:
                print(f"⚠️  No text response from '{agent_name}'")
                print(f"Full response: {response_data}")
                return str(response_data)
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Error sending message to '{agent_name}': {e}")
            return None
    
    def get_available_agents(self) -> list:
        """Returns the list of available agents"""
        return list(self.agents.keys())
    
    def get_status(self) -> dict:
        """Returns the current status of the manager"""
        return {
            "has_credentials": bool(self.access_token),
            "active_sessions": list(self.session_ids.keys()),
            "available_agents": list(self.agents.keys())
        }
    
    def complete_flow(self, agent_name: str, message: str) -> Optional[str]:
        """Executes the complete flow: get credentials, start session and send message"""
        print(f"🚀 Starting complete flow for '{agent_name}'...")
        
        # Step 1: Get credentials
        if not self.get_credentials():
            return None
        
        # Step 2: Start session
        if not self.start_session(agent_name):
            return None
        
        # Step 3: Send message
        return self.send_message(agent_name, message)

    def interactive_mode(self):
        """Interactive terminal mode for agent interaction"""
        print("\n=== Salesforce Agent Manager - Interactive Mode ===")
        print(f"Available agents: {', '.join(self.get_available_agents())}")
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
                        print(f"\n🚀 Sending to {current_agent}...")
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
                        print(f"Status: {status}")
                    elif command == 'help':
                        self.show_help()
                    elif command in self.agents:
                        # Start conversation with agent
                        message = input(f"💬 Enter your first message for {command}: ")
                        if message.strip():
                            print(f"\n🚀 Starting conversation with {command}...")
                            
                            # Initialize session if needed
                            if not self.access_token:
                                if not self.get_credentials():
                                    continue
                            
                            if command not in self.session_ids:
                                if not self.start_session(command):
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
        print("\n=== HELP ===")
        print("Commands:")
        print("  - <agent_name>: Start conversation with agent")
        print("  - status: Show current status")
        print("  - help: Show this help")
        print("  - quit/exit: Exit interactive mode")
        print(f"\nAvailable agents: {', '.join(self.get_available_agents())}")
        print("\nConversation mode:")
        print("  - Once in conversation with an agent, keep typing messages")
        print("  - Type 'back' to return to agent selection")
        print("  - Type 'quit' to exit completely")
        print("\nExample workflow:")
        print("  1. Type: buscar_historico")
        print("  2. Enter your first message")
        print("  3. Continue the conversation with follow-up messages")
        print("  4. Type 'back' when done to switch agents\n")


# Usage examples
if __name__ == "__main__":
    manager = SalesforceAgentManager()
    
    # Interactive mode
    manager.interactive_mode()
    
    # Programmatic usage examples:
    # response = manager.complete_flow("oportunidades", "Hello, I need information about sales opportunities")
    # 
    # Step by step:
    # manager.get_credentials()
    # manager.start_session("buscar_historico")
    # manager.send_message("buscar_historico", "Search client ABC history")