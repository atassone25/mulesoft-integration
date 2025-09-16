#!/usr/bin/env python3
import requests
import json
import base64
import os
from dotenv import load_dotenv

load_dotenv()

def test_oportunidades():
    # Endpoint and credentials from environment
    url = os.getenv("SALESFORCE_A2A_AGENT_OPORTUNIDADES")
    username = os.getenv("A2A_AUTH_USERNAME")
    password = os.getenv("A2A_AUTH_PASSWORD")
    
    if not all([url, username, password]):
        raise ValueError("Missing required environment variables: SALESFORCE_A2A_AGENT_OPORTUNIDADES, A2A_AUTH_USERNAME, A2A_AUTH_PASSWORD")
    
    # Create auth header
    auth_token = base64.b64encode(f"{username}:{password}".encode()).decode()
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_token}'
    }
    
    # Payload
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "message/send",
        "params": {
            "contextId": "test-123",
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": "Criar nova oportunidade de venda para empresa ABC"}],
                "contextId": "test-123",
                "messageId": "msg-456"
            },
            "metadata": {}
        }
    }
    
    # Make request
    response = requests.post(url, headers=headers, json=payload)
    
    # Show output
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(response.text)

if __name__ == "__main__":
    test_oportunidades()
