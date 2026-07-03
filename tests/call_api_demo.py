import os
import json
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Load environment
load_dotenv()

from src.api.main import app

def run_demo():
    client = TestClient(app)
    
    url = "/api/chat"
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": "What mutual funds are available?",
        "history": []
    }
    
    print("\n" + "="*80)
    print("DEMONSTRATING API REQUEST & PAYLOAD")
    print("="*80)
    print(f"HTTP METHOD : POST")
    print(f"URL         : {url}")
    print(f"HEADERS     : {json.dumps(headers, indent=2)}")
    print(f"PAYLOAD     :")
    print(json.dumps(payload, indent=2))
    
    print("\n" + "="*80)
    print("CALLING API & RETRIEVING RESPONSE")
    print("="*80)
    
    response = client.post(url, headers=headers, json=payload)
    
    print(f"HTTP STATUS : {response.status_code}")
    print("RESPONSE BODY :")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(response.text)
    print("="*80 + "\n")

if __name__ == "__main__":
    run_demo()
