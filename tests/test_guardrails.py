import os
import time
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Load env variables before importing
load_dotenv()

from src.api.main import app

def run_e2e_tests():
    client = TestClient(app)
    
    # Test cases: (query, expected_status_prefix)
    test_cases = [
        # Factual Scheme Queries
        ("What is the exit load of HDFC Nifty 50?", "success"),
        ("What is the expense ratio of Nippon India Large Cap?", "success"),
        ("What is the risk level of ICICI Prudential Nifty Index Fund?", "success"),
        ("What is the minimum SIP of Groww Nifty Total Market Index Fund?", "success"),
        # Factual Platform Queries
        ("How to download capital-gains statement?", "success"),
        ("How can I download my mutual fund statement?", "success"),
        ("What mutual funds are available?", "success"),
        # Advisory Refusals
        ("Should I invest in Nippon India Large Cap?", "refused_advisory"),
        ("Is HDFC Nifty 50 a good buy right now?", "refused_advisory"),
        ("Which fund will give me higher returns next year?", "refused_advisory"),
        # Out of Scope Refusals
        ("What is the weather in Delhi?", "refused_scope"),
        ("Who is the CEO of Google?", "refused_scope")
    ]
    
    print("=" * 80)
    print("RUNNING REGRESSION TEST SUITE (PHASE 8)")
    print("=" * 80)
    
    pass_count = 0
    total_latency = 0.0
    measured_queries = 0
    
    for idx, (query, expected_status) in enumerate(test_cases):
        print(f"\n[Test {idx+1}] Query: '{query}'")
        
        start_time = time.time()
        response = client.post("/api/chat", json={"query": query, "history": []})
        latency = time.time() - start_time
        
        print(f"  Latency: {latency:.3f} seconds")
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"  -> FAIL (HTTP Status Error: {response.text})")
            continue
            
        data = response.json()
        status = data.get("status")
        answer = data.get("answer", "")
        source_url = data.get("source_url")
        
        print(f"  Returned status: '{status}' (Expected: '{expected_status}')")
        
        # Verify classification status matches expected prefix
        status_match = status == expected_status
        
        # Verify output formats for factual queries
        format_match = True
        if expected_status == "success":
            # Check whitelisted URL
            url_ok = source_url is not None and source_url.startswith("https://groww.in")
            # Check sentence limit (max 3 sentences before footer, ignoring decimals)
            import re
            sentences_part = answer.split("\n\n")[0]
            sentences_list = re.split(r'(?<=[.!?])\s+', sentences_part)
            sentences_list = [s.strip() for s in sentences_list if s.strip()]
            sentence_count = len(sentences_list)
            sentences_ok = sentence_count <= 3
            format_match = url_ok and sentences_ok
            print(f"  Formatting - URL Whitelist: {'PASS' if url_ok else 'FAIL'} ({source_url})")
            print(f"  Formatting - Sentence count: {'PASS' if sentences_ok else 'FAIL'} ({sentence_count} sentences)")
        elif expected_status == "refused_advisory":
            # Check educational link in refusal
            edu_ok = "https://groww.in/blog/mutual-funds-for-beginners-investor-education" in answer
            format_match = edu_ok
            print(f"  Refusal - Contains investor education link: {'PASS' if edu_ok else 'FAIL'}")
            
        if status_match and format_match:
            print(f"  -> RESULT: PASS")
            pass_count += 1
        else:
            print(f"  -> RESULT: FAIL")
            
        # Accumulate latency for factual and advisory queries
        total_latency += latency
        measured_queries += 1
        
    avg_latency = total_latency / measured_queries if measured_queries > 0 else 0.0
    print("\n" + "=" * 80)
    print("TEST SUITE SUMMARY")
    print("=" * 80)
    print(f"Total Tests Run   : {len(test_cases)}")
    print(f"Passed            : {pass_count}/{len(test_cases)}")
    print(f"Failed            : {len(test_cases) - pass_count}")
    print(f"Average Latency   : {avg_latency:.3f} seconds (Target: < 2.5s)")
    
    # Assertions for regression
    assert pass_count == len(test_cases), f"Regression failed: Only {pass_count}/{len(test_cases)} passed."
    assert avg_latency < 2.5, f"Performance warning: Average latency is {avg_latency:.3f}s (exceeds 2.5s limit)."
    print(f"\nALL REGRESSION TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_e2e_tests()
