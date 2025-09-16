#!/usr/bin/env python3
import requests
import json
import base64

def test_historico_compras():
    """Test the purchase history skill"""
    # Endpoint and credentials
    url = "https://agentforce-b2b-fv3b5q.3ch7y1.usa-e1.cloudhub.io/historico/historico"
    username = "agentforce_dev"
    password = "9229e770-767c-417b-a0b0-f0741243c589"
    
    # Create auth header
    auth_token = base64.b64encode(f"{username}:{password}".encode()).decode()
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_token}'
    }
    
    # Payload for purchase history
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "message/send",
        "params": {
            "contextId": "test-123",
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": "Mostrar histórico de compras do cliente FISK SCHOOLS"}],
                "contextId": "test-123",
                "messageId": "msg-456"
            },
            "metadata": {}
        }
    }
    
    print("=== Testing Purchase History ===")
    
    # Make request
    response = requests.post(url, headers=headers, json=payload)
    
    # Show output
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(response.text)

def test_oportunidades_perdidas():
    """Test the lost opportunities skill"""
    # Endpoint and credentials
    url = "https://agentforce-b2b-fv3b5q.3ch7y1.usa-e1.cloudhub.io/historico/historico"
    username = "agentforce_dev"
    password = "9229e770-767c-417b-a0b0-f0741243c589"
    
    # Create auth header
    auth_token = base64.b64encode(f"{username}:{password}".encode()).decode()
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_token}'
    }
    
    # Payload for lost opportunities
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "message/send",
        "params": {
            "contextId": "test-456",
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": "Consultar oportunidades perdidas do cliente XYZ"}],
                "contextId": "test-456",
                "messageId": "msg-789"
            },
            "metadata": {}
        }
    }
    
    print("\n=== Testing Lost Opportunities ===")
    
    # Make request
    response = requests.post(url, headers=headers, json=payload)
    
    # Show output
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(response.text)

def test_both_skills():
    """Test both skills in sequence"""
    print("Testing Historico endpoint with both skills...")
    test_historico_compras()
    test_oportunidades_perdidas()

if __name__ == "__main__":
    test_both_skills()
