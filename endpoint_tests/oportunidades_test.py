#!/usr/bin/env python3
import requests
import json
import base64

def test_oportunidades():
    # Endpoint and credentials
    url = "https://agentforce-b2b-fv3b5q.3ch7y1.usa-e1.cloudhub.io/oportunidade/agentforce-agent"
    username = "agentforce_dev"
    password = "9229e770-767c-417b-a0b0-f0741243c589"
    
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
