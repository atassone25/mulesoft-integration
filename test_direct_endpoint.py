#!/usr/bin/env python3
"""
Direct test of the deployed datastore agent endpoint
Mimics what the Flask app does
"""
import requests
import google.auth
import google.auth.transport.requests
import json
import time

PROJECT_ID = "gglobo-agentsb2b-hdg-dev"
LOCATION = "us-central1"
ENGINE_ID = "4757723152828596224"

def get_google_token():
    """Get authentication token"""
    try:
        credentials, project = google.auth.default(quota_project_id=PROJECT_ID)
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        return credentials.token
    except Exception as e:
        print(f"❌ Failed to get credentials: {e}")
        return None

def test_endpoint():
    """Test the endpoint directly"""
    
    print("="*70)
    print(f"TESTING ENDPOINT: {ENGINE_ID}")
    print("="*70)
    
    # Get token
    print("\n1. Getting authentication token...")
    token = get_google_token()
    if not token:
        print("❌ Failed to get token")
        return
    print("✅ Token obtained")
    
    # Step 1: Create session
    print("\n2. Creating session...")
    endpoint = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{ENGINE_ID}:query"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"class_method": "create_session", "input": {"user_id": "test_user_direct"}}
    
    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data['output']['id']
        print(f"✅ Session created: {session_id}")
        print(f"   Full response: {json.dumps(session_data, indent=2)}")
    except Exception as e:
        print(f"❌ Failed to create session: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response status: {e.response.status_code}")
            print(f"   Response text: {e.response.text}")
        return
    
    # Wait a moment
    time.sleep(1)
    
    # Step 2: Send query
    print("\n3. Sending query...")
    test_message = "Buscar produtos com os seguintes critérios: automotivo, TV aberta, mídia avulsa"
    
    endpoint_stream = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{ENGINE_ID}:streamQuery?alt=sse"
    data = {
        "class_method": "stream_query",
        "input": {"user_id": "test_user_direct", "session_id": session_id, "message": test_message}
    }
    
    print(f"   Query: '{test_message}'")
    print(f"   Endpoint: {endpoint_stream}")
    print("\n📝 Agent Response:")
    print("-"*70)
    
    try:
        with requests.post(endpoint_stream, headers=headers, json=data, stream=True, timeout=120) as r:
            r.raise_for_status()
            print("✅ Connection established")
            
            full_response = ""
            chunk_count = 0
            
            for chunk in r.iter_content(chunk_size=None):
                if chunk:
                    chunk_count += 1
                    chunk_str = chunk.decode('utf-8')
                    
                    # Try to parse as direct JSON first
                    try:
                        data_json = json.loads(chunk_str)
                        if 'content' in data_json and 'parts' in data_json['content']:
                            for part in data_json['content']['parts']:
                                if 'text' in part:
                                    text = part['text']
                                    print(text, end='', flush=True)
                                    full_response += text
                        continue
                    except json.JSONDecodeError:
                        pass
                    
                    # Parse SSE format
                    for line in chunk_str.split('\n'):
                        if line.startswith('data: '):
                            try:
                                data_json = json.loads(line[6:])
                                if 'parts' in data_json:
                                    for part in data_json['parts']:
                                        if 'text' in part:
                                            text = part['text']
                                            print(text, end='', flush=True)
                                            full_response += text
                            except json.JSONDecodeError:
                                pass
            
            print("\n" + "-"*70)
            
            if full_response:
                print(f"\n✅ Test successful! Agent responded.")
                print(f"   Response length: {len(full_response)} characters")
                print(f"   Chunks received: {chunk_count}")
            else:
                print(f"\n⚠️  Warning: No text content in response")
                print(f"   Chunks received: {chunk_count}")
                
    except Exception as e:
        print(f"\n❌ Query failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response status: {e.response.status_code}")
            print(f"   Response text: {e.response.text[:500]}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*70)
    print("TEST COMPLETED")
    print("="*70)

if __name__ == "__main__":
    test_endpoint()

