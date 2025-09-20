#!/usr/bin/env python3
import requests
import json
import base64
import os
import uuid
import time
from dotenv import load_dotenv

load_dotenv()

def generate_context_id():
    """Generate a unique context ID with timestamp"""
    timestamp = int(time.time() * 1000)
    unique_id = str(uuid.uuid4())[:8]
    return f"ctx-{timestamp}-{unique_id}"

def make_agent_request(url, headers, payload, max_retries=2):
    """Make request to agent with retry logic for expired sessions"""
    for attempt in range(max_retries + 1):
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 500:
            try:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "")
                
                # Check if it's a session expiration error (404 on session resource)
                if "not found (404)" in error_message and attempt < max_retries:
                    print(f"Session expired (attempt {attempt + 1}/{max_retries + 1}), generating new contextId...")
                    
                    # Generate new contextId and update payload
                    new_context_id = generate_context_id()
                    payload["params"]["contextId"] = new_context_id
                    payload["params"]["message"]["contextId"] = new_context_id
                    payload["params"]["message"]["messageId"] = f"msg-{int(time.time() * 1000)}"
                    
                    continue
            except:
                pass
        
        return response
    
    return response

def test_buscar_produto():
    # Endpoint and credentials from environment
    url = os.getenv("SALESFORCE_A2A_AGENT_BUSCAR_PRODUTO")
    username = os.getenv("A2A_AUTH_USERNAME")
    password = os.getenv("A2A_AUTH_PASSWORD")
    
    if not all([url, username, password]):
        raise ValueError("Missing required environment variables: SALESFORCE_A2A_AGENT_BUSCAR_PRODUTO, A2A_AUTH_USERNAME, A2A_AUTH_PASSWORD")
    
    # Create auth header
    auth_token = base64.b64encode(f"{username}:{password}".encode()).decode()
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_token}'
    }
    
    # Generate dynamic contextId and messageId
    context_id = generate_context_id()
    message_id = f"msg-{int(time.time() * 1000)}"
    
    # Payload
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "message/send",
        "params": {
            "contextId": context_id,
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": "Buscar produtos de tecnologia"}],
                "contextId": context_id,
                "messageId": message_id
            },
            "metadata": {}
        }
    }
    
    print(f"Using contextId: {context_id}")
    print(f"Using messageId: {message_id}")
    
    # Make request with retry logic
    response = make_agent_request(url, headers, payload)
    
    # Show output
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(response.text)

if __name__ == "__main__":
    test_buscar_produto()
