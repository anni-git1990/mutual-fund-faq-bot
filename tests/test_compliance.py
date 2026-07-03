import os
from dotenv import load_dotenv
from groq import Groq
from src.api.guardrails import classify_query, validate_and_format_output

# Load environment
load_dotenv()

def run_tests():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not found in environment.")
        return
        
    client = Groq(api_key=api_key)
    
    print("="*60)
    print("TESTING INPUT GUARDRAIL (QUERY CLASSIFICATION)")
    print("="*60)
    
    test_queries = {
        "What is the exit load of HDFC Nifty 50?": "FACTUAL",
        "Should I buy Nippon India Large Cap?": "ADVISORY",
        "Is ICICI Prudential Nifty Next 50 a good buy right now?": "ADVISORY",
        "Which fund will give me higher returns next year?": "ADVISORY",
        "What is the capital of India?": "OUT_OF_SCOPE",
        "How is the weather in Delhi?": "OUT_OF_SCOPE"
    }
    
    success_count = 0
    for query, expected in test_queries.items():
        result = classify_query(query, client)
        matched = (result == expected)
        print(f"Query: '{query}'")
        print(f"  -> Got: {result} (Expected: {expected}) -> {'PASS' if matched else 'FAIL'}")
        if matched:
            success_count += 1
            
    print(f"\nClassification success: {success_count}/{len(test_queries)}")
    
    print("\n" + "="*60)
    print("TESTING OUTPUT GUARDRAIL (VALIDATION & FORMATTING)")
    print("="*60)
    
    sample_answers = [
        (
            "The exit load of HDFC Nifty 50 is 0.25% if redeemed within 3 days. "
            "This makes it a great choice to buy. It is a very safe fund.",
            "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth",
            "02-Jul-2026"
        ),
        (
            "Nippon India Large Cap Fund has an expense ratio of 0.92%. "
            "We recommend you invest in it. You should buy it today. It is safe.",
            "https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth",
            "02-Jul-2026"
        )
    ]
    
    for idx, (ans, url, date) in enumerate(sample_answers):
        print(f"\n[Test {idx+1}] Raw Output:")
        print(ans)
        formatted = validate_and_format_output(ans, url, date)
        print("Formatted Output:")
        print(formatted)
        
        # Verify sentence count limits (max 3 sentences before footer)
        sentences_part = formatted.split("\n\n")[0]
        sentence_count = len([s for s in sentences_part.split(".") if s.strip()])
        print(f"  Sentence count: {sentence_count} (Must be <= 3)")
        
        # Verify whitelisted url presence
        print(f"  Contains whitelist URL: {url in formatted}")

if __name__ == "__main__":
    run_tests()
