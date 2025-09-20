#!/usr/bin/env python3
import requests
import json
import base64
import os
from dotenv import load_dotenv

load_dotenv()

def test_historico_compras():
    """Test the purchase history skill"""
    # Endpoint and credentials from environment
    url = os.getenv("SALESFORCE_A2A_AGENT_BUSCAR_HISTORICO")
    username = os.getenv("A2A_AUTH_USERNAME")
    password = os.getenv("A2A_AUTH_PASSWORD")
    
    if not all([url, username, password]):
        raise ValueError("Missing required environment variables: SALESFORCE_A2A_AGENT_BUSCAR_HISTORICO, A2A_AUTH_USERNAME, A2A_AUTH_PASSWORD")
    
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
                "parts": [{"kind": "text", "text": "histórico de mídia da Nova Casas Bahia"}],
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
    # Endpoint and credentials from environment
    url = os.getenv("SALESFORCE_A2A_AGENT_BUSCAR_HISTORICO")
    username = os.getenv("A2A_AUTH_USERNAME")
    password = os.getenv("A2A_AUTH_PASSWORD")
    
    if not all([url, username, password]):
        raise ValueError("Missing required environment variables: SALESFORCE_A2A_AGENT_BUSCAR_HISTORICO, A2A_AUTH_USERNAME, A2A_AUTH_PASSWORD")
    
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
