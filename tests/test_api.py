import os
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Load env variables before importing main to ensure API keys are loaded
load_dotenv()

from src.api.main import app

def test_chat_api():
    client = TestClient(app)
    
    print("="*60)
    print("TESTING FASTAPI /api/chat ENDPOINT")
    print("="*60)
    
    # 1. Test Factual Query
    factual_payload = {
        "query": "What is the exit load of HDFC Nifty 50?",
        "history": []
    }
    print(f"\n[Test 1] Sending Factual Query: '{factual_payload['query']}'")
    response = client.post("/api/chat", json=factual_payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Response JSON:")
        print(f"  - status: {data.get('status')}")
        print(f"  - source_url: {data.get('source_url')}")
        print(f"  - last_updated: {data.get('last_updated')}")
        print(f"  - answer:\n{data.get('answer')}")
    else:
        print(f"Error output: {response.text}")
        
    # 2. Test Advisory Query
    advisory_payload = {
        "query": "Should I buy Nippon India Large Cap?",
        "history": []
    }
    print(f"\n[Test 2] Sending Advisory Query: '{advisory_payload['query']}'")
    response = client.post("/api/chat", json=advisory_payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Response JSON:")
        print(f"  - status: {data.get('status')}")
        print(f"  - answer:\n{data.get('answer')}")
    else:
        print(f"Error output: {response.text}")

    # 3. Test Out of Scope Query
    out_of_scope_payload = {
        "query": "What is the capital of France?",
        "history": []
    }
    print(f"\n[Test 3] Sending Out-of-Scope Query: '{out_of_scope_payload['query']}'")
    response = client.post("/api/chat", json=out_of_scope_payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Response JSON:")
        print(f"  - status: {data.get('status')}")
        print(f"  - answer:\n{data.get('answer')}")
    else:
        print(f"Error output: {response.text}")

if __name__ == "__main__":
    test_chat_api()
