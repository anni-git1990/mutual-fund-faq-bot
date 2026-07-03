# Edge Case Analysis & Corner Scenarios

This document analyzes potential edge cases, failure modes, and corner scenarios for the Mutual Fund FAQ Assistant RAG Bot, along with mitigation strategies defined across the system layers.

---

## 1. Data Ingestion & ETL Edge Cases

| Scenario | Edge Case | Mitigation Strategy |
|---|---|---|
| **HTML Layout Shift** | Groww changes its website CSS/HTML structure, causing the web scraper to return empty or corrupted text/tables. | 1. Implement fallback CSS selectors in the scraper.<br>2. Add schema validation checks on the parsed JSON output.<br>3. Send alert or log errors if key metrics (NAV, Expense Ratio) are missing. |
| **Missing Core Metrics** | A mutual fund page is missing details (e.g., a newly launched fund with no Riskometer rating or `N/A` for exit load). | 1. Map missing fields to a standard placeholder (e.g., "Not Applicable" or "Information not available on source page").<br>2. Prevent ingestion script from crashing by using safe dictionary lookups (`.get()`). |
| **Broken Table Chunking** | Tabular information (like expense ratios or asset allocations) is split across chunks, making it unreadable. | 1. Convert HTML tables to Markdown format before chunking.<br>2. Implement a custom chunking policy that preserves complete Markdown table structures within a single block. |

---

## 2. Input Guardrail & Query Routing Edge Cases

| Scenario | Edge Case | Mitigation Strategy |
|---|---|---|
| **Hybrid/Mixed Intent Queries** | User asks a question combining facts and advice: *"What is the exit load of HDFC Nifty 50, and is it a good buy?"* | 1. The query classifier is configured with a safety-first bias: if **any** part of the query requests advice, it classifies the entire query as `ADVISORY`.<br>2. Return the standard refusal response immediately. |
| **Typographical Errors in Fund Names** | User queries a scheme with typos: *"What is exit load for Nipon large cap?"* | 1. Rely on semantic dense embeddings (BGE) which capture spelling similarity.<br>2. Implement fuzzy matching (e.g., using `rapidfuzz` or Levenshtein distance) to map "Nipon" to the correct metadata filter: "Nippon India Large Cap Fund". |
| **Out-of-Scope Mutual Funds** | User asks about a fund not present in the 5 selected schemes: *"What is the NAV of Parag Parikh Flexi Cap?"* | 1. Detect if the parsed fund name matches any of our 5 supported schemes.<br>2. If not, route to a friendly refusal: *"I can only provide information on the 5 supported schemes on Groww."* |
| **Non-Financial / General Queries** | User inputs completely unrelated queries: *"What is the capital of France?"* or asks general programming questions. | 1. The input guardrail query classifier screens for mutual fund context.<br>2. Route non-financial queries to a standard out-of-scope refusal message. |

---

## 3. Retrieval Engine Edge Cases

| Scenario | Edge Case | Mitigation Strategy |
|---|---|---|
| **Cross-Context Leakage** | User asks about HDFC, but the search retrieves a highly similar Nippon India chunk (e.g. general discussion about Nifty 50 index tracking). | 1. Apply a strict metadata filter in ChromaDB using the target `fund_name` before performing vector search.<br>2. This guarantees that only chunks matching the query's target fund are returned. |
| **Empty Search Results** | Search query does not find any chunks matching the retrieval threshold score. | 1. Fallback to general scheme-level chunks (e.g., main landing text of the fund).<br>2. If still empty, LLM declines to answer and cites the homepage `https://groww.in`. |

---

## 4. LLM Generation (Groq) & Compliance Edge Cases

| Scenario | Edge Case | Mitigation Strategy |
|---|---|---|
| **Hallucinated Citation URLs** | Groq's LLM fabricates a Groww URL or alters the path parameters (e.g., generating `https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth-custom-page`). | 1. The output guardrail matches the output URL against a whitelist of valid chunk URLs.<br>2. If the URL does not match exactly, the guardrail replaces it with the canonical URL of the fund from metadata, or rejects the generation. |
| **Advisory Leak in Output** | The LLM provides factual answers but appends soft recommendations: *"The exit load is 0.25%, which is very low and makes it a great choice."* | 1. Hard negative constraints in the system prompt: "Do not use qualitative adjectives like 'great', 'poor', 'high return', or 'recommended'".<br>2. The output guardrail scans for banned words ("buy", "recommend", "great choice", "outperform") and triggers a rewrite or block if matched. |
| **Length Rule Breach** | The LLM outputs a 4- or 5-sentence response, violating the 3-sentence limit. | 1. Output guardrail splits the text by punctuation (`.`, `!`, `?`) and truncates the response to the first 3 sentences.<br>2. Appends the citation link and updated date to the truncated output. |
| **Token Limit / API Timeout** | Groq API times out or returns rate limit errors during high traffic. | 1. Implement retry logic with exponential backoff on the backend API wrapper.<br>2. Return a friendly client-side error: *"The assistant is currently busy. Please try again in a few moments."* |
