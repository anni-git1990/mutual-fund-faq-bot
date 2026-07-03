import os
import datetime
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from groq import Groq
from src.api.retriever import MutualFundRetriever
from src.api.guardrails import (
    classify_query, 
    validate_and_format_output, 
    ADVISORY_REFUSAL_TEXT, 
    OUT_OF_SCOPE_TEXT
)

router = APIRouter()

# In-memory query response cache to conserve daily tokens (TPD/RPD) and avoid rate limit blocks
RESPONSE_CACHE = {}

# Initialize retriever
try:
    retriever = MutualFundRetriever()
except Exception as e:
    print(f"Warning: Failed to initialize retriever. Chroma DB might not be built yet: {e}")
    retriever = None

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[Message]] = []

class ChatResponse(BaseModel):
    answer: str
    source_url: Optional[str] = None
    last_updated: Optional[str] = None
    status: str

SYSTEM_INSTRUCTIONS = """You are a facts-only Mutual Fund FAQ Assistant for the platform Groww.
Answer the user's query factually using ONLY the provided context chunks.

CONTEXT:
{context_text}

STRICT RULES:
1. Answer the query factually using ONLY the provided context. If the answer cannot be found in the context, politely refuse to answer.
2. Limit your answer to a MAXIMUM of 3 sentences.
3. You must include exactly ONE official source link (URL) at the end of your answer, taken directly from the context metadata. Do not assume or fabricate any URLs.
4. Append the date in this exact format: "Last updated from sources: {last_updated_date}" using the date from the context metadata.
5. Do not offer financial recommendations, opinions, comparisons, or buy/sell suggestions. Keep the tone completely neutral, clear, and factual.
"""

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not retriever:
        raise HTTPException(status_code=500, detail="Retriever is not initialized.")
        
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable is missing.")
        
    query = request.query
    model_name = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    client = Groq(api_key=groq_api_key)
    current_date = datetime.datetime.now().strftime("%d-%b-%Y")
    
    # 0. Check Response Cache (saves 100% of tokens and requests for identical queries)
    cache_key = query.strip().lower()
    if cache_key in RESPONSE_CACHE:
        print(f"Cache hit for query: '{query}'")
        return RESPONSE_CACHE[cache_key]
        
    # 1. Run Input Guardrail: Classify Query Intent (with retries for Groq rate limits)
    intent = classify_query(query, client, model=model_name)
    print(f"Query Classifier matched intent: '{intent}' for query: '{query}'")
    
    if intent == "ADVISORY":
        refusal_answer = (
            f"{ADVISORY_REFUSAL_TEXT}\n\n"
            f"Source: https://groww.in/blog/mutual-funds-for-beginners-investor-education\n"
            f"Last updated from sources: {current_date}"
        )
        response_payload = ChatResponse(
            answer=refusal_answer,
            source_url="https://groww.in/blog/mutual-funds-for-beginners-investor-education",
            last_updated=current_date,
            status="refused_advisory"
        )
        RESPONSE_CACHE[cache_key] = response_payload
        return response_payload
        
    elif intent == "OUT_OF_SCOPE":
        refusal_answer = (
            f"{OUT_OF_SCOPE_TEXT}\n\n"
            f"Source: https://groww.in\n"
            f"Last updated from sources: {current_date}"
        )
        response_payload = ChatResponse(
            answer=refusal_answer,
            source_url="https://groww.in",
            last_updated=current_date,
            status="refused_scope"
        )
        RESPONSE_CACHE[cache_key] = response_payload
        return response_payload
        
    # 2. Proceed to retrieval (intent is FACTUAL)
    try:
        retrieved_chunks = retriever.retrieve(query, limit=3)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
        
    if not retrieved_chunks:
        fallback_answer = (
            "I'm sorry, I couldn't find any relevant factual information for your query in our corpus.\n\n"
            "Source: https://groww.in\n"
            "Last updated from sources: {current_date}"
        )
        response_payload = ChatResponse(
            answer=fallback_answer,
            source_url="https://groww.in",
            last_updated=current_date,
            status="no_context"
        )
        RESPONSE_CACHE[cache_key] = response_payload
        return response_payload
        
    # 3. Format context text & metadata details
    context_text_list = []
    source_urls = []
    last_updated_dates = []
    
    for chunk in retrieved_chunks:
        context_text_list.append(chunk["text"])
        source_urls.append(chunk["metadata"].get("source_url"))
        last_updated_dates.append(chunk["metadata"].get("last_updated"))
        
    context_text = "\n\n---\n\n".join(context_text_list)
    primary_source_url = source_urls[0] if source_urls else "https://groww.in"
    primary_last_updated = last_updated_dates[0] if last_updated_dates else current_date
    
    # 4. Generate answer using Groq (with retry logic for rate limits)
    try:
        system_prompt = SYSTEM_INSTRUCTIONS.format(
            context_text=context_text,
            last_updated_date=primary_last_updated
        )
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        for msg in request.history:
            messages.append({"role": msg.role, "content": msg.content})
            
        messages.append({"role": "user", "content": query})
        
        raw_answer = ""
        for attempt in range(3):
            try:
                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=model_name,
                    temperature=0.0,
                    max_tokens=300
                )
                raw_answer = chat_completion.choices[0].message.content.strip()
                break
            except Exception as e:
                err_str = str(e).lower()
                if ("rate limit" in err_str or "429" in err_str) and attempt < 2:
                    sleep_time = 2 ** attempt
                    print(f"Rate limit hit in LLM generator. Sleeping for {sleep_time}s and retrying...")
                    time.sleep(sleep_time)
                    continue
                raise e
        
        # 5. Run Output Guardrails (Validation and formatting sanitization)
        final_answer = validate_and_format_output(
            answer=raw_answer,
            primary_url=primary_source_url,
            last_updated=primary_last_updated
        )
        
        response_payload = ChatResponse(
            answer=final_answer,
            source_url=primary_source_url,
            last_updated=primary_last_updated,
            status="success"
        )
        RESPONSE_CACHE[cache_key] = response_payload
        return response_payload
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")
