import os
import re
import datetime
import time
from groq import Groq

# Whitelist of the target Groww URLs
GROWW_WHITELIST_URLS = [
    "https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/icici-prudential-nifty-next-50-index-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth",
    "https://groww.in/mutual-funds/groww-nifty-total-market-index-fund-direct-growth",
    "https://groww.in/mutual-funds/icici-prudential-nifty-index-fund-direct-growth",
    "https://groww.in/help/mutual-funds/reports-and-statements/how-to-download-capital-gains-statement",
    "https://groww.in/blog/mutual-funds-for-beginners-investor-education",
    "https://groww.in"
]

ADVISORY_REFUSAL_TEXT = (
    "I can help with factual mutual fund information, but I cannot provide investment advice, "
    "recommendations, or return predictions. Please refer to official investor education resources "
    "before making investment decisions."
)

OUT_OF_SCOPE_TEXT = (
    "I can only answer factual mutual fund questions about the 5 supported schemes on Groww: "
    "Nippon India Large Cap, ICICI Prudential Nifty Next 50, HDFC Nifty 50, Groww Nifty Total Market, "
    "and ICICI Prudential Nifty Index."
)

CLASSIFIER_PROMPT = """You are a compliance guardrail classifier for a mutual fund FAQ assistant.
Your job is to classify the user query into exactly one of three categories:
- FACTUAL: The query asks for objective, verifiable, historical metrics about a mutual fund (e.g., exit load, expense ratio, AUM, holdings, NAV, riskometer, risk level, benchmark, fund manager, OR queries asking to list the available/supported schemes, download platform reports, and general helper queries).
- ADVISORY: The query asks for investment advice, opinions, recommendations, predictions, buy/sell suggestions, or compares returns to decide which fund to buy (e.g. "should I buy this?", "which fund is better?", "will HDFC give good returns?").
- OUT_OF_SCOPE: The query is unrelated to mutual funds (e.g., questions about stocks, weather, general knowledge), or asks about funds outside our scope of the 5 supported schemes.

Reply with exactly one word: FACTUAL, ADVISORY, or OUT_OF_SCOPE. Do not output anything else.
"""

def classify_query(query: str, client: Groq, model: str = "llama-3.3-70b-versatile") -> str:
    """
    Classifies the user query using Groq LLM with retry logic.
    Returns: 'FACTUAL', 'ADVISORY', or 'OUT_OF_SCOPE'
    """
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": CLASSIFIER_PROMPT},
                    {"role": "user", "content": f"Query: {query}"}
                ],
                model=model,
                temperature=0.0,
                max_tokens=10
            )
            result = response.choices[0].message.content.strip().upper()
            if "FACTUAL" in result:
                return "FACTUAL"
            elif "ADVISORY" in result:
                return "ADVISORY"
            else:
                return "OUT_OF_SCOPE"
        except Exception as e:
            err_str = str(e).lower()
            if "rate limit" in err_str or "429" in err_str:
                sleep_time = 2 ** attempt
                print(f"Rate limit hit in classifier. Sleeping for {sleep_time}s and retrying...")
                time.sleep(sleep_time)
                continue
            print(f"Classifier error: {e}. Defaulting to OUT_OF_SCOPE for safety.")
    return "OUT_OF_SCOPE"

def validate_and_format_output(answer: str, primary_url: str, last_updated: str) -> str:
    """
    Applies output guardrails to the LLM response:
    1. Sentence count validation (max 3 sentences).
    2. URL validation (checks whitelist, forces exactly one).
    3. Banned term filter (strips advisory leakage).
    4. Date footer compliance check.
    """
    # 1. Banned terms filter (simple check, replace qualitative advisory terms with neutral ones)
    banned_words_map = {
        r"\b(buy|sell|purchase|invest in)\b": "examine the facts of",
        r"\b(recommend|recommendation)\b": "provide information for",
        r"\b(great choice|good choice|excellent investment|wonderful investment)\b": "subject of factual inquiry",
        r"\b(guaranteed returns|high returns|sure returns)\b": "past historical returns"
    }
    for pattern, repl in banned_words_map.items():
        answer = re.sub(pattern, repl, answer, flags=re.IGNORECASE)

    # 2. Sentence validation (maximum 3 sentences)
    # Split text into sentences using simple regex
    sentences = re.split(r'(?<=[.!?])\s+', answer)
    # Filter out empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # If more than 3 sentences, truncate
    if len(sentences) > 3:
        # Check if the last sentence contains the URL, so we don't truncate the citation
        url_in_last = any(url in sentences[-1] for url in GROWW_WHITELIST_URLS) or "http" in sentences[-1]
        truncated_sentences = sentences[:3]
        answer = " ".join(truncated_sentences)
    else:
        answer = " ".join(sentences)

    # 3. Clean up existing URLs to ensure we append exactly one verified whitelisted URL
    # Extract any URLs present in the text
    found_urls = re.findall(r'https?://[^\s)]+', answer)
    for url in found_urls:
        answer = answer.replace(url, "")
        
    # Clean trailing spaces/punctuation after stripping url
    answer = answer.strip().rstrip(".").rstrip(",")
    
    # 4. Enforce exactly one whitelisted URL and date footer
    target_url = primary_url if primary_url in GROWW_WHITELIST_URLS else GROWW_WHITELIST_URLS[0]
    
    final_output = (
        f"{answer}\n\n"
        f"Source: {target_url}\n"
        f"Last updated from sources: {last_updated}"
    )
    
    return final_output
